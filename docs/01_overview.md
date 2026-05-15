# 01 — Overview e Architettura

## Visione d'insieme

Il telefono SIP Siemens grigio degli anni '70 è un capolavoro di ingegneria elettromeccanica. L'obiettivo di questo progetto è **non snaturarlo**: il disco gira come prima, il campanello suona come prima, la cornetta pesa come prima. Cambia solo cosa c'è dentro.

## Architettura logica

```
┌─────────────────────────────────────────────────────────────────┐
│                    TELEFONO SIP (scocca)                        │
│                                                                 │
│  ┌──────────────┐    ┌─────────────────┐    ┌───────────────┐ │
│  │   CORNETTA   │    │  DISCO COMBIN.  │    │  CAMPANELLO   │ │
│  │              │    │                 │    │  (24V AC)     │ │
│  │ • Mic carbone│    │ • Contatto      │    │               │ │
│  │ • Speaker    │    │   pulse (NSI)   │    │               │ │
│  │ • Hook switch│    │ • Contatto      │    │               │ │
│  │              │    │   off-normal    │    │               │ │
│  └──────┬───────┘    └────────┬────────┘    └───────┬───────┘ │
│         │                     │                     │         │
│         │ analog audio        │ pulses              │ AC      │
│         │                     │                     │         │
│  ┌──────▼─────────────────────▼─────────────────────▼───────┐ │
│  │                  CIRCUITO DI INTERFACCIA                  │ │
│  │  ┌──────────┐  ┌─────────┐  ┌────────────┐  ┌─────────┐  │ │
│  │  │ Pre-amp  │  │ Amp     │  │ GPIO       │  │ Driver  │  │ │
│  │  │ mic      │  │ speaker │  │ debouncing │  │ relay + │  │ │
│  │  │ + bias   │  │ I2S DAC │  │            │  │ boost   │  │ │
│  │  └────┬─────┘  └────▲────┘  └─────┬──────┘  └────▲────┘  │ │
│  └───────┼─────────────┼─────────────┼──────────────┼───────┘ │
│          │             │             │              │         │
│  ┌───────▼─────────────┴─────────────▼──────────────┴───────┐ │
│  │              RASPBERRY PI ZERO 2 W                        │ │
│  │                                                           │ │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │ │
│  │  │ oFono   │  │ PJSIP    │  │ Dial     │  │ Display  │   │ │
│  │  │ (BT HFP)│  │ (VoIP)   │  │ reader   │  │ OLED I2C │   │ │
│  │  └────┬────┘  └─────┬────┘  └────┬─────┘  └────┬─────┘   │ │
│  │       │             │            │             │         │ │
│  │       └──────┬──────┴────────────┴─────────────┘         │ │
│  │              │                                            │ │
│  │       ┌──────▼──────────┐                                 │ │
│  │       │   main.py       │  ← orchestratore stati          │ │
│  │       │  (state machine)│                                 │ │
│  │       └──────┬──────────┘                                 │ │
│  │              │                                            │ │
│  │       ┌──────▼──────────┐                                 │ │
│  │       │   phonebook     │                                 │ │
│  │       │   (sqlite)      │                                 │ │
│  │       └─────────────────┘                                 │ │
│  └───────────────────┬───────────────────────────────────────┘ │
│                      │                                          │
│              ┌───────▼────────┐                                 │
│              │  ALIMENTAZIONE │                                 │
│              │  2x 18650 +    │                                 │
│              │  TP4056 + boost│                                 │
│              │  + 24VAC gen.  │                                 │
│              └────────────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Bluetooth / Wi-Fi
                              ▼
                    ┌──────────────────┐
                    │   SMARTPHONE     │
                    │   (HFP profile)  │
                    └──────────────────┘
```

## State machine

Il telefono ha 5 stati principali:

```
        ┌─────────────┐
        │    IDLE     │  ← cornetta giù, niente chiamate
        └──────┬──────┘
               │ hook up
               ▼
        ┌─────────────┐
        │   DIALING   │  ← cornetta su, in attesa cifre
        │ (collect    │     dal disco
        │  digits)    │
        └──────┬──────┘
               │ timeout dial / # / numero rubrica match
               ▼
        ┌─────────────┐
        │   CALLING   │  ← chiamata in corso
        └──────┬──────┘    via BT-HFP o SIP
               │
               │ hook down / remote hangup
               ▼
        ┌─────────────┐
        │    IDLE     │
        └─────────────┘

        ┌─────────────┐
        │  RINGING    │  ← chiamata in arrivo
        │ (bell on)   │     campanello suona
        └──────┬──────┘
               │ hook up
               ▼
        ┌─────────────┐
        │  IN_CALL    │
        └─────────────┘
```

## Scelte tecniche

### Perché Raspberry Pi Zero 2 W e non ESP32?
Le funzionalità "Massimo" richiedono:
- Stack Bluetooth completo con HFP/HSP (oFono + BlueZ)
- Client SIP completo (PJSIP)
- Database rubrica (SQLite)
- Multitasking reale tra audio, GPIO, networking

L'ESP32 può fare BT audio ma non SIP + HFP + rubrica contemporaneamente in modo affidabile.

### Perché I2S e non l'audio analogico del Pi?
Il Pi Zero non ha jack audio. L'I2S con un DAC dedicato (PCM5102A) dà qualità audio molto migliore e bassa latenza — fondamentale per le chiamate.

### Perché conservare il microfono a carbone?
Per fedeltà vintage. Suona "telefonico" in modo autentico. Richiede però un bias DC e un preamp.
*Alternativa:* sostituire con elettrete da 9.7mm che entra nella stessa sede meccanica.

### Perché tenere il campanello originale?
Perché è bellissimo. Richiede un boost converter che generi ~24V AC a 20-25Hz, oppure una soluzione più semplice con due bobine pilotate in alternanza da un H-bridge.

## Profili di funzionamento

Il dispositivo opera in 3 modalità (selezionabili da config):

1. **BT-only**: solo vivavoce Bluetooth per cellulare accoppiato
2. **SIP-only**: telefono VoIP autonomo via Wi-Fi
3. **Hybrid** (default): se cellulare BT presente → BT; altrimenti SIP
