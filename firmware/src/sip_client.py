"""
sip_client.py — Client VoIP SIP basato su PJSIP

Permette di usare il telefono come SIP phone autonomo via Wi-Fi.
"""

import asyncio
import logging
from typing import Callable, Optional


log = logging.getLogger("sip_client")


class SipClient:
    """Wrapper PJSIP per chiamate SIP."""

    def __init__(self, config: dict):
        self.config = config
        self.registered = False
        self._lib = None
        self._account = None
        self._current_call = None

        self.on_incoming_call: Optional[Callable] = None
        self.on_call_ended: Optional[Callable] = None

    async def start(self):
        if not self.config.get("enabled", False):
            log.info("SIP disabilitato in config")
            return

        try:
            import pjsua2 as pj
        except ImportError:
            log.warning("PJSIP non installato — SIP disabilitato. "
                       "Installa con: pip install pjsua2")
            return

        log.info("Inizializzazione PJSIP…")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._init_pjsip)

    def _init_pjsip(self):
        import pjsua2 as pj

        # Endpoint config
        self._lib = pj.Endpoint()
        self._lib.libCreate()

        ep_cfg = pj.EpConfig()
        ep_cfg.logConfig.level = 3
        self._lib.libInit(ep_cfg)

        # Transport (UDP)
        tp_cfg = pj.TransportConfig()
        tp_cfg.port = self.config.get("port", 5060)
        self._lib.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp_cfg)

        self._lib.libStart()

        # Account
        acc_cfg = pj.AccountConfig()
        acc_cfg.idUri = f"sip:{self.config['username']}@{self.config['domain']}"
        acc_cfg.regConfig.registrarUri = f"sip:{self.config['domain']}"

        cred = pj.AuthCredInfo(
            "digest", "*",
            self.config["username"], 0,
            self.config["password"],
        )
        acc_cfg.sipConfig.authCreds.append(cred)

        # Account custom per callback
        outer = self
        class MyAccount(pj.Account):
            def onIncomingCall(self_acc, prm):
                call = pj.Call(self_acc, prm.callId)
                ci = call.getInfo()
                caller = ci.remoteUri
                log.info("Chiamata SIP in arrivo: %s", caller)
                outer._current_call = call
                if outer.on_incoming_call:
                    asyncio.run_coroutine_threadsafe(
                        outer.on_incoming_call(caller),
                        asyncio.get_event_loop()
                    )

            def onRegState(self_acc, prm):
                ai = self_acc.getInfo()
                outer.registered = ai.regIsActive
                log.info("SIP register state: %s", "OK" if outer.registered else "OFFLINE")

        self._account = MyAccount()
        self._account.create(acc_cfg)
        log.info("PJSIP avviato — account creato per %s", self.config["username"])

    async def stop(self):
        if self._lib:
            try:
                self._lib.libDestroy()
            except Exception as e:
                log.error("Errore destroy PJSIP: %s", e)

    async def place_call(self, number: str) -> bool:
        if not self._account or not self.registered:
            log.error("Account SIP non registrato")
            return False
        try:
            import pjsua2 as pj
            uri = f"sip:{number}@{self.config['domain']}"
            call = pj.Call(self._account)
            prm = pj.CallOpParam(True)
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: call.makeCall(uri, prm)
            )
            self._current_call = call
            log.info("Chiamata SIP avviata: %s", uri)
            return True
        except Exception as e:
            log.error("Errore makeCall: %s", e)
            return False

    async def answer(self):
        if self._current_call:
            import pjsua2 as pj
            prm = pj.CallOpParam()
            prm.statusCode = 200
            self._current_call.answer(prm)

    async def reject(self):
        if self._current_call:
            import pjsua2 as pj
            prm = pj.CallOpParam()
            prm.statusCode = 486  # Busy
            self._current_call.hangup(prm)
            self._current_call = None

    async def hangup(self):
        if self._current_call:
            import pjsua2 as pj
            prm = pj.CallOpParam()
            prm.statusCode = 200
            self._current_call.hangup(prm)
            self._current_call = None
            if self.on_call_ended:
                await self.on_call_ended()

    async def send_dtmf(self, digit: str):
        if self._current_call:
            self._current_call.dialDtmf(digit)
