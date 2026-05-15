"""
bell_driver.py — Driver del campanello elettromeccanico originale

Genera un'onda quadra a 20-25Hz applicata tramite H-bridge L9110S
alle bobine del campanello, alimentate da boost converter XL6009.

Pattern italiano standard: 1s squillo, 4s pausa.
"""

import asyncio
import logging

try:
    from gpiozero import OutputDevice, PWMOutputDevice
except ImportError:
    OutputDevice = None
    PWMOutputDevice = None


log = logging.getLogger("bell_driver")


class BellDriver:
    """Pilota il campanello tramite GPIO."""

    def __init__(self, config: dict):
        self.config = config
        self._en_gpio = 22       # BCM, abilita boost converter
        self._ph_gpio = 23       # BCM, fase H-bridge

        self._enable = None
        self._phase = None

        self._ringing = False
        self._ring_task: asyncio.Task | None = None

    async def start(self):
        if OutputDevice is None:
            log.warning("gpiozero non disponibile — modalità simulazione")
            return

        self._enable = OutputDevice(self._en_gpio, initial_value=False)
        # PWM 50% duty per pilotare l'H-bridge (onda quadra)
        self._phase = PWMOutputDevice(self._ph_gpio, frequency=self.config["frequency_hz"])
        self._phase.value = 0

        log.info("BellDriver pronto (EN=GPIO%d, PH=GPIO%d, freq=%dHz)",
                 self._en_gpio, self._ph_gpio, self.config["frequency_hz"])

    async def stop(self):
        await self.stop_ringing()
        if self._enable:
            self._enable.close()
        if self._phase:
            self._phase.close()

    async def start_ringing(self):
        """Avvia pattern di squillo (loop fino a stop_ringing)."""
        if self._ringing:
            return
        self._ringing = True
        log.info("🔔 Inizio squillo")
        self._ring_task = asyncio.create_task(self._ring_loop())

    async def stop_ringing(self):
        """Ferma lo squillo immediatamente."""
        self._ringing = False
        if self._ring_task:
            self._ring_task.cancel()
            try:
                await self._ring_task
            except asyncio.CancelledError:
                pass
            self._ring_task = None
        self._bell_off()
        log.info("🔕 Stop squillo")

    async def _ring_loop(self):
        """Pattern italiano: on/off ciclico."""
        on_s = self.config["pattern_on_ms"] / 1000.0
        off_s = self.config["pattern_off_ms"] / 1000.0
        max_rings = self.config.get("max_rings", 30)
        count = 0

        try:
            while self._ringing and count < max_rings:
                self._bell_on()
                await asyncio.sleep(on_s)
                self._bell_off()
                if not self._ringing:
                    break
                await asyncio.sleep(off_s)
                count += 1
        finally:
            self._bell_off()

    def _bell_on(self):
        """Abilita boost + avvia onda quadra."""
        if self._enable:
            self._enable.on()
        if self._phase:
            self._phase.value = 0.5  # 50% duty = onda quadra simmetrica

    def _bell_off(self):
        """Spegne tutto."""
        if self._phase:
            self._phase.value = 0
        if self._enable:
            self._enable.off()


async def _test():
    logging.basicConfig(level=logging.DEBUG)
    cfg = {
        "frequency_hz": 22,
        "pattern_on_ms": 1000,
        "pattern_off_ms": 2000,
        "max_rings": 3,
    }
    bell = BellDriver(cfg)
    await bell.start()
    print("Test campanello: 3 squilli")
    await bell.start_ringing()
    await asyncio.sleep(15)
    await bell.stop_ringing()
    await bell.stop()


if __name__ == "__main__":
    asyncio.run(_test())
