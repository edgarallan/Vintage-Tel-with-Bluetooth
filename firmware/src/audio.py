"""
audio.py — Gestione audio: toni di sistema (dial tone, busy, keypress)

I toni vengono generati al volo con NumPy e riprodotti via ALSA/PulseAudio.
Per le chiamate vere, l'audio è gestito da oFono (BT-HFP) o PJSIP (SIP),
che dialogano direttamente con il dispositivo audio I2S.
"""

import asyncio
import logging
import subprocess
from pathlib import Path

try:
    import numpy as np
    import sounddevice as sd
    AUDIO_OK = True
except ImportError:
    AUDIO_OK = False


log = logging.getLogger("audio")


class AudioManager:
    """Genera e riproduce toni di sistema in stile telefono italiano."""

    DEFAULT_SAMPLE_RATE = 44100
    BASE_AMPLITUDE = 0.3  # ampiezza di riferimento (gain 0 dB)

    def __init__(self, config: dict):
        self.config = config
        # Allinea il sample rate al device I2S/ALSA configurato (default 44100).
        self.sample_rate = int(config.get("sample_rate", self.DEFAULT_SAMPLE_RATE))
        # Gain altoparlante applicato ai toni di sistema (dB → fattore lineare),
        # con clamp per evitare clipping dell'onda generata.
        gain_db = float(config.get("speaker_gain_db", 0))
        self._amplitude = min(self.BASE_AMPLITUDE * (10 ** (gain_db / 20.0)), 1.0)
        self._dial_task: asyncio.Task | None = None
        self._busy_task: asyncio.Task | None = None

    async def start(self):
        if not AUDIO_OK:
            log.warning("sounddevice/numpy non disponibili — audio simulato")
            return
        log.info("AudioManager pronto (sample_rate=%d, ampiezza=%.2f)",
                 self.sample_rate, self._amplitude)

    async def stop(self):
        await self.stop_dial_tone()
        await self.stop_busy_tone()

    # ─── Toni italiani ────────────────────────────────────────────────
    # Riferimento: ITU-T E.180 + standard italiano Telecom
    # Dial tone IT: 425Hz continuo
    # Busy tone IT: 425Hz, 500ms on / 500ms off
    # Ring-back IT: 425Hz, 1s on / 4s off

    def _tone(self, freq: float, duration_s: float) -> "np.ndarray":
        t = np.linspace(0, duration_s, int(self.sample_rate * duration_s), False)
        # Fade in/out per evitare click
        wave = np.sin(2 * np.pi * freq * t) * self._amplitude
        fade = int(0.01 * self.sample_rate)
        wave[:fade] *= np.linspace(0, 1, fade)
        wave[-fade:] *= np.linspace(1, 0, fade)
        return wave.astype(np.float32)

    async def play_dial_tone(self):
        """Riproduce dial tone continuo (425Hz, fino a stop)."""
        if not AUDIO_OK or self._dial_task:
            return
        self._dial_task = asyncio.create_task(self._dial_loop())

    async def stop_dial_tone(self):
        if self._dial_task:
            self._dial_task.cancel()
            try:
                await self._dial_task
            except asyncio.CancelledError:
                pass
            self._dial_task = None
            if AUDIO_OK:
                sd.stop()

    async def _dial_loop(self):
        wave = self._tone(425, 1.0)
        try:
            while True:
                sd.play(wave, samplerate=self.sample_rate, blocking=False)
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            pass

    async def play_busy_tone(self):
        if not AUDIO_OK or self._busy_task:
            return
        self._busy_task = asyncio.create_task(self._busy_loop())

    async def stop_busy_tone(self):
        if self._busy_task:
            self._busy_task.cancel()
            try:
                await self._busy_task
            except asyncio.CancelledError:
                pass
            self._busy_task = None
            if AUDIO_OK:
                sd.stop()

    async def _busy_loop(self):
        wave = self._tone(425, 0.5)
        try:
            while True:
                sd.play(wave, samplerate=self.sample_rate, blocking=False)
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            pass

    async def play_keypress(self):
        """Beep breve di feedback alla pressione tasto/cifra."""
        if not AUDIO_OK:
            return
        wave = self._tone(800, 0.05)
        sd.play(wave, samplerate=self.sample_rate, blocking=False)
