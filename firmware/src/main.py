"""
main.py — Vintage Tel BL orchestrator

State machine principale che coordina tutti i moduli:
hook switch, disco, audio, Bluetooth HFP, SIP client, display, LED, campanello.
"""

import asyncio
import logging
import signal
import sys
from enum import Enum, auto
from pathlib import Path

import yaml

from .dial_reader import DialReader
from .hook_switch import HookSwitch
from .bell_driver import BellDriver
from .bt_phone import BluetoothPhone
from .sip_client import SipClient
from .display import Display
from .phonebook import Phonebook
from .audio import AudioManager
from .led import StatusLed


CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"


class State(Enum):
    """Stati del telefono."""
    IDLE = auto()           # cornetta giù, niente attività
    DIALING = auto()        # cornetta su, in attesa cifre
    CALLING = auto()        # chiamata in uscita / in corso
    RINGING = auto()        # chiamata in arrivo, campanello suona
    IN_CALL = auto()        # chiamata attiva (BT o SIP)
    ERROR = auto()


class VintageTel:
    """Orchestratore principale."""

    def __init__(self, config: dict):
        self.config = config
        self.log = logging.getLogger("vintage_tel")

        self.state = State.IDLE
        self._state_lock = asyncio.Lock()
        self._dialed_digits = ""
        self._call_backend = None  # "bt" o "sip"

        # Inizializza i moduli
        self.hook = HookSwitch(config["hook"])
        self.dial = DialReader(config["dial"])
        self.bell = BellDriver(config["bell"])
        self.display = Display(config["display"]) if config["display"]["enabled"] else None
        self.led = StatusLed(config["led"]) if config["led"]["enabled"] else None
        self.audio = AudioManager(config["audio"])
        self.phonebook = Phonebook(config["phonebook"])

        # Backend chiamate
        self.bt = BluetoothPhone(config["bluetooth"]) if config["bluetooth"]["enabled"] else None
        self.sip = SipClient(config["sip"]) if config["sip"]["enabled"] else None

        self._tasks: list[asyncio.Task] = []
        self._shutdown = asyncio.Event()

    async def start(self):
        """Avvia tutti i moduli e i loop di evento."""
        self.log.info("🟢 Vintage Tel BL — avvio in modalità %s", self.config["mode"])

        # Avvia moduli
        await self.hook.start()
        await self.dial.start()
        await self.bell.start()
        await self.audio.start()
        if self.display:
            await self.display.start()
            await self.display.show_idle()
        if self.led:
            await self.led.start()
            await self.led.idle()

        # Backend
        if self.bt:
            await self.bt.start()
            self.bt.on_incoming_call = self._on_incoming_call_bt
            self.bt.on_call_ended = self._on_call_ended
        if self.sip:
            await self.sip.start()
            self.sip.on_incoming_call = self._on_incoming_call_sip
            self.sip.on_call_ended = self._on_call_ended

        # Loop principali (coroutine in parallelo)
        self._tasks.append(asyncio.create_task(self._hook_loop()))
        self._tasks.append(asyncio.create_task(self._dial_loop()))

        await self._shutdown.wait()
        await self._cleanup()

    async def stop(self):
        """Spegnimento ordinato."""
        self.log.info("🔴 Spegnimento richiesto")
        self._shutdown.set()

    async def _cleanup(self):
        """Cleanup risorse."""
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

        await self.bell.stop()
        await self.dial.stop()
        await self.hook.stop()
        await self.audio.stop()
        if self.display: await self.display.stop()
        if self.led: await self.led.stop()
        if self.bt: await self.bt.stop()
        if self.sip: await self.sip.stop()

        self.log.info("Spegnimento completato")

    # ─── State transitions ────────────────────────────────────────────

    async def _transition(self, new_state: State):
        """Cambio stato con logging e side-effects UI."""
        async with self._state_lock:
            old = self.state
            self.state = new_state
            self.log.info("🔄 Stato: %s → %s", old.name, new_state.name)

            if self.led:
                await {
                    State.IDLE:    self.led.idle,
                    State.DIALING: self.led.dialing,
                    State.CALLING: self.led.calling,
                    State.RINGING: self.led.ringing,
                    State.IN_CALL: self.led.in_call,
                    State.ERROR:   self.led.error,
                }[new_state]()

            if self.display:
                await self.display.show_state(new_state.name, extra=self._dialed_digits)

    # ─── Hook switch loop ─────────────────────────────────────────────

    async def _hook_loop(self):
        """Reagisce al sollevamento/abbassamento della cornetta."""
        async for hook_up in self.hook.events():
            self.log.debug("Hook event: %s", "UP" if hook_up else "DOWN")

            if hook_up:
                # Cornetta sollevata
                if self.state == State.RINGING:
                    # Rispondi alla chiamata in arrivo
                    await self.bell.stop_ringing()
                    await self._answer_call()
                elif self.state == State.IDLE:
                    # Inizia composizione
                    self._dialed_digits = ""
                    await self._transition(State.DIALING)
                    await self.audio.play_dial_tone()
            else:
                # Cornetta abbassata
                if self.state in (State.IN_CALL, State.CALLING):
                    await self._hangup()
                elif self.state == State.DIALING:
                    await self.audio.stop_dial_tone()
                    self._dialed_digits = ""
                    await self._transition(State.IDLE)
                elif self.state == State.RINGING:
                    # Rifiuto chiamata
                    await self.bell.stop_ringing()
                    await self._reject_call()

    # ─── Dial reader loop ─────────────────────────────────────────────

    async def _dial_loop(self):
        """Raccoglie cifre dal disco e avvia chiamata quando il numero è completo."""
        dial_timeout = self.config["dial"]["dial_timeout_s"]

        async for digit in self.dial.digits():
            if self.state != State.DIALING:
                # Disco usato fuori contesto — ignora o usa per DTMF in-call
                if self.state == State.IN_CALL:
                    await self._send_dtmf(digit)
                continue

            self.log.info("Cifra composta: %d", digit)
            self._dialed_digits += str(digit)
            await self.audio.stop_dial_tone()
            await self.audio.play_keypress()

            if self.display:
                await self.display.show_dialing(self._dialed_digits)

            # Check quick-dial (singola cifra dopo silenzio sufficiente)
            if len(self._dialed_digits) == 1:
                qd = self.config["phonebook"]["quick_dial"].get(digit)
                if qd:
                    # Aspetta breve, se non arrivano altre cifre → quick dial
                    await asyncio.sleep(1.5)
                    if self._dialed_digits == str(digit):
                        await self._place_call(qd)
                        continue

            # Aspetta nuova cifra; se timeout → componi numero raccolto
            try:
                await asyncio.wait_for(
                    self.dial.next_digit_event(),
                    timeout=dial_timeout
                )
            except asyncio.TimeoutError:
                if self._dialed_digits:
                    await self._place_call(self._dialed_digits)

    # ─── Call management ──────────────────────────────────────────────

    async def _place_call(self, number: str):
        """Avvia una chiamata in uscita scegliendo backend in base alla mode."""
        await self._transition(State.CALLING)
        self.log.info("📞 Chiamo: %s", number)

        backend = self._choose_backend()
        self._call_backend = backend

        if backend == "bt":
            ok = await self.bt.place_call(number)
        elif backend == "sip":
            ok = await self.sip.place_call(number)
        else:
            self.log.error("Nessun backend disponibile!")
            ok = False

        if not ok:
            await self.audio.play_busy_tone()
            await asyncio.sleep(3)
            await self.audio.stop_busy_tone()
            self._dialed_digits = ""
            await self._transition(State.IDLE)
        else:
            await self._transition(State.IN_CALL)

    async def _answer_call(self):
        """Risponde alla chiamata in arrivo."""
        if self._call_backend == "bt":
            await self.bt.answer()
        elif self._call_backend == "sip":
            await self.sip.answer()
        await self._transition(State.IN_CALL)

    async def _reject_call(self):
        if self._call_backend == "bt":
            await self.bt.reject()
        elif self._call_backend == "sip":
            await self.sip.reject()
        self._call_backend = None
        await self._transition(State.IDLE)

    async def _hangup(self):
        if self._call_backend == "bt":
            await self.bt.hangup()
        elif self._call_backend == "sip":
            await self.sip.hangup()
        self._call_backend = None
        self._dialed_digits = ""
        await self._transition(State.IDLE)

    async def _send_dtmf(self, digit: int):
        """Invia un tono DTMF durante chiamata (per IVR)."""
        if self._call_backend == "bt":
            await self.bt.send_dtmf(str(digit))
        elif self._call_backend == "sip":
            await self.sip.send_dtmf(str(digit))

    # ─── Backend selection ────────────────────────────────────────────

    def _choose_backend(self) -> str | None:
        mode = self.config["mode"]
        if mode == "bt_only":
            return "bt" if self.bt and self.bt.connected else None
        if mode == "sip_only":
            return "sip" if self.sip and self.sip.registered else None
        # hybrid: BT se disponibile, altrimenti SIP
        if self.bt and self.bt.connected:
            return "bt"
        if self.sip and self.sip.registered:
            return "sip"
        return None

    # ─── Incoming call callbacks ──────────────────────────────────────

    async def _on_incoming_call_bt(self, caller: str):
        await self._on_incoming_call("bt", caller)

    async def _on_incoming_call_sip(self, caller: str):
        await self._on_incoming_call("sip", caller)

    async def _on_incoming_call(self, backend: str, caller: str):
        if self.state != State.IDLE:
            self.log.warning("Chiamata in arrivo ma non in IDLE — ignoro")
            return

        # Risolvi numero → nome se in rubrica
        name = self.phonebook.lookup(caller) or caller
        self.log.info("📲 Chiamata in arrivo da: %s (%s)", name, backend)

        self._call_backend = backend
        if self.display:
            await self.display.show_incoming(name, caller)

        await self._transition(State.RINGING)
        await self.bell.start_ringing()

    async def _on_call_ended(self):
        self.log.info("Chiamata terminata dal remoto")
        await self.bell.stop_ringing()
        self._call_backend = None
        self._dialed_digits = ""
        await self._transition(State.IDLE)


# ─── Entry point ──────────────────────────────────────────────────────

def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return yaml.safe_load(f)


async def main():
    config = load_config()
    logging.basicConfig(
        level=config.get("logging", {}).get("level", "INFO"),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    tel = VintageTel(config)

    # Gestione signal per spegnimento ordinato
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(tel.stop()))

    try:
        await tel.start()
    except Exception:
        logging.exception("Errore fatale")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
