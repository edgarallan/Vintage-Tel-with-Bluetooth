"""
dial_reader.py — Lettura del disco combinatore SIP

Il disco genera impulsi a 10Hz contando le interruzioni del contatto "pulse"
durante il ritorno meccanico. Il contatto NSI ("off-normal switch") indica
quando il disco è in movimento e funge da gate per la conta degli impulsi.
"""

import asyncio
import logging
import time
from typing import AsyncIterator

try:
    from gpiozero import Button
except ImportError:
    Button = None  # Per test su macchina non-Pi


log = logging.getLogger("dial_reader")


class DialReader:
    """Legge le cifre dal disco combinatore.

    Algoritmo:
    1. NSI a riposo (HIGH con pull-up, contatto chiuso a GND quindi LOW in pratica)
       quando il disco è fermo. Quando l'utente inizia a ruotare, NSI cambia stato.
    2. Mentre NSI è "in movimento", contiamo i fronti del contatto Pulse.
    3. Quando NSI torna a riposo, il numero di impulsi = cifra composta
       (con 10 impulsi → cifra 0).
    """

    def __init__(self, config: dict):
        self.config = config
        self._pulse_gpio = 4    # BCM
        self._nsi_gpio = 17     # BCM

        self._pulse_count = 0
        self._dialing = False    # True quando NSI indica disco in moto
        self._last_pulse_time = 0.0
        self._bounce_s = config["pulse_bouncetime_ms"] / 1000.0

        self._digit_queue: asyncio.Queue[int] = asyncio.Queue()
        self._new_digit_event = asyncio.Event()

        self._pulse_btn = None
        self._nsi_btn = None
        self._loop: asyncio.AbstractEventLoop | None = None

    async def start(self):
        self._loop = asyncio.get_running_loop()

        if Button is None:
            log.warning("gpiozero non disponibile — modalità simulazione")
            return

        # Pulse: quando il contatto si apre (rising edge con pull-up) è un impulso
        self._pulse_btn = Button(self._pulse_gpio, pull_up=True, bounce_time=self._bounce_s)
        self._pulse_btn.when_released = self._on_pulse  # released = contatto si apre

        # NSI: quando si "preme" (disco inizia a girare)
        self._nsi_btn = Button(self._nsi_gpio, pull_up=True, bounce_time=0.02)
        self._nsi_btn.when_pressed = self._on_nsi_start
        self._nsi_btn.when_released = self._on_nsi_end

        log.info("DialReader avviato (pulse=GPIO%d, NSI=GPIO%d)",
                 self._pulse_gpio, self._nsi_gpio)

    async def stop(self):
        if self._pulse_btn:
            self._pulse_btn.close()
        if self._nsi_btn:
            self._nsi_btn.close()

    def _on_nsi_start(self):
        """Disco ha iniziato a ruotare."""
        log.debug("Disco: NSI start (rotazione iniziata)")
        self._pulse_count = 0
        self._dialing = True

    def _on_nsi_end(self):
        """Disco è tornato a riposo: emetti cifra."""
        if not self._dialing:
            return
        self._dialing = False
        count = self._pulse_count
        log.debug("Disco: NSI end con %d impulsi", count)

        if count == 0:
            return  # Disco mosso senza completare

        # Conversione: 10 impulsi = 0 (standard italiano/europeo)
        if count >= self.config.get("zero_pulses", 10):
            digit = 0
        elif 1 <= count <= 9:
            digit = count
        else:
            log.warning("Conta impulsi anomala: %d — scarto", count)
            return

        # Notifica al loop async
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._enqueue_digit(digit), self._loop
            )

    def _on_pulse(self):
        """Un impulso del contatto pulse (solo se in rotazione)."""
        if not self._dialing:
            return
        # Debouncing aggiuntivo software
        now = time.monotonic()
        if now - self._last_pulse_time < self._bounce_s:
            return
        self._last_pulse_time = now
        self._pulse_count += 1
        log.debug("Disco: impulso %d", self._pulse_count)

    async def _enqueue_digit(self, digit: int):
        await self._digit_queue.put(digit)
        self._new_digit_event.set()

    async def digits(self) -> AsyncIterator[int]:
        """Generator async che emette ogni cifra composta."""
        while True:
            digit = await self._digit_queue.get()
            yield digit

    async def next_digit_event(self):
        """Attende il prossimo evento di cifra (per timeout)."""
        self._new_digit_event.clear()
        await self._new_digit_event.wait()


# ─── Test standalone ──────────────────────────────────────────────────

async def _test():
    logging.basicConfig(level=logging.DEBUG)
    cfg = {"pulse_bouncetime_ms": 50, "zero_pulses": 10, "dial_timeout_s": 8}
    reader = DialReader(cfg)
    await reader.start()
    print("Componi cifre con il disco (Ctrl+C per uscire)...")
    try:
        async for digit in reader.digits():
            print(f"➡️  Cifra: {digit}")
    except KeyboardInterrupt:
        pass
    finally:
        await reader.stop()


if __name__ == "__main__":
    asyncio.run(_test())
