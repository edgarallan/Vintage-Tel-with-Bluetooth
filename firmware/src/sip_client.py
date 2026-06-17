"""
sip_client.py — Client VoIP SIP basato su PJSIP

Permette di usare il telefono come SIP phone autonomo via Wi-Fi.

Note implementative:
- I callback PJSIP (onIncomingCall, onCallState, onCallMediaState) girano nei
  thread interni di PJSIP: ogni rientro in asyncio passa per il loop catturato
  in start() (self._loop) e mai per asyncio.get_event_loop(), che nel thread
  PJSIP fallirebbe su Python 3.12.
- L'audio della chiamata viene connesso esplicitamente in onCallMediaState:
  senza questo, la chiamata si stabilisce ma non passa voce.
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
        self._call_cls = None  # sottoclasse pj.Call costruita in _init_pjsip

        self.on_incoming_call: Optional[Callable] = None
        self.on_call_ended: Optional[Callable] = None

        # Event loop asyncio catturato in start() per i callback dai thread PJSIP.
        self._loop: asyncio.AbstractEventLoop | None = None

    async def start(self):
        if not self.config.get("enabled", False):
            log.info("SIP disabilitato in config")
            return

        try:
            import pjsua2 as pj  # noqa: F401
        except ImportError:
            log.warning("PJSIP non installato — SIP disabilitato. "
                       "Installa con: pip install pjsua2")
            return

        log.info("Inizializzazione PJSIP…")
        self._loop = asyncio.get_running_loop()
        try:
            await self._loop.run_in_executor(None, self._init_pjsip)
        except Exception as e:
            # SIP degrada come gli altri backend: un errore di init/registrazione
            # non deve abbattere l'intera app.
            log.error("Init PJSIP fallito — SIP disabilitato: %s", e)
            self.registered = False

    def _notify_call_ended(self):
        """Inoltra la fine chiamata al loop asyncio (chiamato dai thread PJSIP)."""
        self._current_call = None
        if self.on_call_ended and self._loop:
            asyncio.run_coroutine_threadsafe(self.on_call_ended(), self._loop)

    def _connect_call_audio(self, call):
        """Collega il media audio della chiamata al device di cattura/riproduzione."""
        import pjsua2 as pj

        ci = call.getInfo()
        for mi in ci.media:
            if (mi.type == pj.PJMEDIA_TYPE_AUDIO
                    and mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE):
                call_media = call.getAudioMedia(mi.index)
                adm = pj.Endpoint.instance().audDevManager()
                # Microfono → remoto, remoto → altoparlante
                adm.getCaptureDevMedia().startTransmit(call_media)
                call_media.startTransmit(adm.getPlaybackDevMedia())
                log.info("Audio chiamata SIP connesso (media #%d)", mi.index)

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

        outer = self

        # Call custom: gestisce media audio e fine chiamata.
        class MyCall(pj.Call):
            def onCallState(self_call, prm):
                ci = self_call.getInfo()
                if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
                    log.info("Chiamata SIP terminata")
                    outer._notify_call_ended()

            def onCallMediaState(self_call, prm):
                try:
                    outer._connect_call_audio(self_call)
                except Exception as e:
                    log.error("Errore connessione audio SIP: %s", e)

        self._call_cls = MyCall

        # Account custom per callback
        class MyAccount(pj.Account):
            def onIncomingCall(self_acc, prm):
                call = MyCall(self_acc, prm.callId)
                ci = call.getInfo()
                caller = ci.remoteUri
                log.info("Chiamata SIP in arrivo: %s", caller)
                outer._current_call = call
                if outer.on_incoming_call and outer._loop:
                    asyncio.run_coroutine_threadsafe(
                        outer.on_incoming_call(caller),
                        outer._loop,
                    )

            def onRegState(self_acc, prm):
                ai = self_acc.getInfo()
                outer.registered = ai.regIsActive
                log.info("SIP register state: %s", "OK" if outer.registered else "OFFLINE")

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
        if not self._account or not self.registered or not self._call_cls:
            log.error("Account SIP non registrato")
            return False
        try:
            import pjsua2 as pj
            uri = f"sip:{number}@{self.config['domain']}"
            call = self._call_cls(self._account)
            prm = pj.CallOpParam(True)
            loop = self._loop or asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: call.makeCall(uri, prm))
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
        # La fine chiamata (e on_call_ended) viene notificata da onCallState
        # quando lo stato passa a DISCONNECTED, coerentemente col backend BT.
        if self._current_call:
            import pjsua2 as pj
            prm = pj.CallOpParam()
            prm.statusCode = 200
            self._current_call.hangup(prm)

    async def send_dtmf(self, digit: str):
        if self._current_call:
            self._current_call.dialDtmf(digit)
