"""Test del wiring config in AudioManager (sample_rate + speaker gain)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.audio import AudioManager


def test_sample_rate_from_config():
    assert AudioManager({"sample_rate": 16000}).sample_rate == 16000


def test_defaults_when_missing():
    a = AudioManager({})
    assert a.sample_rate == 44100
    assert abs(a._amplitude - AudioManager.BASE_AMPLITUDE) < 1e-9


def test_speaker_gain_scales_amplitude():
    a = AudioManager({"speaker_gain_db": 6})
    expected = AudioManager.BASE_AMPLITUDE * (10 ** (6 / 20.0))
    assert abs(a._amplitude - expected) < 1e-9


def test_gain_clamped_to_one():
    assert AudioManager({"speaker_gain_db": 40})._amplitude == 1.0
