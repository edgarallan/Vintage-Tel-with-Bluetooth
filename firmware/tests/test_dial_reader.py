"""Test della conversione impulsi → cifra del disco combinatore.

Off-Pi gpiozero.Button è None, quindi piloto direttamente i callback
(_on_nsi_start / _on_pulse / _on_nsi_end) come farebbero le interruzioni GPIO.
"""

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dial_reader import DialReader


async def _read_one(reader, timeout=1.0):
    agen = reader.digits()
    return await asyncio.wait_for(agen.__anext__(), timeout)


async def _dial(reader, pulses: int):
    reader._on_nsi_start()
    for _ in range(pulses):
        reader._on_pulse()
    reader._on_nsi_end()


@pytest.mark.parametrize("pulses,expected", [
    (1, 1), (5, 5), (9, 9),
    (10, 0),   # convenzione italiana: 10 impulsi = 0
    (11, 0),   # oltre 10 → comunque 0
])
async def test_pulse_count_to_digit(pulses, expected):
    reader = DialReader({"pulse_bouncetime_ms": 0, "zero_pulses": 10})
    await reader.start()        # Button None off-Pi → cattura solo il loop
    try:
        await _dial(reader, pulses)
        assert await _read_one(reader) == expected
    finally:
        await reader.stop()


async def test_zero_pulses_emits_nothing():
    reader = DialReader({"pulse_bouncetime_ms": 0, "zero_pulses": 10})
    await reader.start()
    try:
        await _dial(reader, 0)   # disco mosso ma nessun impulso
        with pytest.raises(asyncio.TimeoutError):
            await _read_one(reader, timeout=0.1)
    finally:
        await reader.stop()


async def test_consecutive_digits():
    reader = DialReader({"pulse_bouncetime_ms": 0, "zero_pulses": 10})
    await reader.start()
    try:
        await _dial(reader, 3)
        await _dial(reader, 10)
        assert await _read_one(reader) == 3
        assert await _read_one(reader) == 0
    finally:
        await reader.stop()
