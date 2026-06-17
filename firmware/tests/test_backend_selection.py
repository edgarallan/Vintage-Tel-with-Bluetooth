"""Test della selezione backend (_choose_backend)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fakes import FakeBackend, make_config

from src.main import VintageTel


def _machine(tmp_path, mode):
    cfg = make_config(mode)
    cfg["phonebook"]["db_path"] = str(tmp_path / "phonebook.db")
    return VintageTel(cfg)


def test_bt_only_requires_connected(tmp_path):
    m = _machine(tmp_path, "bt_only")
    m.bt = FakeBackend(connected=True)
    m.sip = FakeBackend(registered=True)
    assert m._choose_backend() == "bt"
    m.bt.connected = False
    assert m._choose_backend() is None   # non ripiega su SIP in bt_only


def test_sip_only_requires_registered(tmp_path):
    m = _machine(tmp_path, "sip_only")
    m.bt = FakeBackend(connected=True)
    m.sip = FakeBackend(registered=True)
    assert m._choose_backend() == "sip"
    m.sip.registered = False
    assert m._choose_backend() is None


def test_hybrid_prefers_bt_then_sip(tmp_path):
    m = _machine(tmp_path, "hybrid")
    m.bt = FakeBackend(connected=True)
    m.sip = FakeBackend(registered=True)
    assert m._choose_backend() == "bt"
    m.bt.connected = False
    assert m._choose_backend() == "sip"   # ripiego su SIP
    m.sip.registered = False
    assert m._choose_backend() is None


def test_hybrid_without_backends(tmp_path):
    m = _machine(tmp_path, "hybrid")
    m.bt = None
    m.sip = None
    assert m._choose_backend() is None
