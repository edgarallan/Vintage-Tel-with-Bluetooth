# Schema Elettrico Completo

```
                                  VINTAGE TEL BL — Schema generale
                                  ═══════════════════════════════════

  USB-C / micro-USB ──┐
  (ricarica)          │
                      ▼
    ┌──────────────────────────────┐
    │  DFRobot DFR0969             │  2×18650 + charger +
    │  holder+charger+prot.+5V/2A  │  protezione + 5V regolato
    └──────────────┬───────────────┘  (carica O scarica, no UPS)
         5V        │
         ├─────────┴──┬────────────────────┐
         │            │                    │
         ▼            ▼                    ▼
    (Raspberry   ┌─────────┐          ┌──────────┐
     Pi + moduli │ Boost   │          │  Switch  │
     a 5V)       │ 5→~24V  │          │  ON/OFF  │
                 │ (modulo)│          │  vintage │
                 └────┬────┘          └──────────┘
                  24V │
                      ▼
                 ┌──────────┐                  ┌──────────────┐
                 │ DRV8871  │── OUT1 ──────────┤ BOBINE       │
                 │ H-bridge │                  │ CAMPANELLO   │
                 │ (≤45V)   │── OUT2 ──────────┤ ORIGINALI    │
                 └──┬───────┘                  └──────────────┘
                    │ IN1 ◄── GPIO 22 (BELL_IN1)
                    │ IN2 ◄── GPIO 23 (BELL_IN2)
                    │ (alternati via software a ~22Hz; IN1=IN2=0 = silenzio)
                    │
                    ▼
    ┌────────────────────────────────────┐
    │       RASPBERRY PI ZERO 2 W        │
    │                                    │
    │  GPIO 4  ◄────[10kΩ]── DIAL_PULSE  │
    │            └─[100nF]── GND          │
    │  GPIO 17 ◄────[10kΩ]── DIAL_NSI    │
    │            └─[100nF]── GND          │
    │  GPIO 27 ◄────[10kΩ]── HOOK_SW     │
    │            └─[100nF]── GND          │
    │                                    │
    │  GPIO 24 ◄────[10kΩ]── BTN_PHONEBOOK│
    │                                    │
    │  GPIO 25 ────[330Ω]──► LED R       │
    │  GPIO 8  ────[330Ω]──► LED G       │
    │  GPIO 7  ────[330Ω]──► LED B       │
    │  (common cathode to GND)           │
    │                                    │
    │  I2C bus (GPIO 2,3) ── Display OLED│
    │                                    │
    │  I2S bus (GPIO 18,19,20,21):       │
    │   ├─ MAX98357A → SPEAKER cornetta (ampli I2S)
    │   └─ SPH0645 (mic MEMS I2S) → MIC cornetta
    │                                    │
    └────────────────────────────────────┘
            ▲
            │ Power 5V dal DFR0969
            │
   ┌────────┴────────┐
   │  Disco SIP      │ ── 4 fili
   │  (Pulse + NSI)  │
   └─────────────────┘
   ┌─────────────────┐
   │  Hook switch    │ ── 2 fili
   └─────────────────┘
   ┌─────────────────┐
   │  Cornetta       │ ── 4 fili (mic + speaker)
   └─────────────────┘
   ┌─────────────────┐
   │  Campanello     │ ── 2 fili
   └─────────────────┘
```

## Tabella connessioni complete

### Bus I2C (display)
| Segnale | Pin Pi (BCM) | Verso |
|---------|--------------|-------|
| SDA | GPIO 2 | Display OLED SDA |
| SCL | GPIO 3 | Display OLED SCL |
| 3V3 | pin 1 | Display VCC |
| GND | pin 9 | Display GND |

### Bus I2S (audio)
| Segnale | Pin Pi (BCM) | Verso |
|---------|--------------|-------|
| BCK | GPIO 18 | MAX98357A BCLK + SPH0645 BCLK |
| LRCK | GPIO 19 | MAX98357A LRC + SPH0645 WS |
| DOUT | GPIO 21 | MAX98357A DIN (Pi → speaker) |
| DIN | GPIO 20 | SPH0645 DOUT (mic → Pi) |

### GPIO digitali
| Segnale | Pin Pi (BCM) | Direzione | Verso |
|---------|--------------|-----------|-------|
| DIAL_PULSE | GPIO 4 | IN (pull-up) | Disco contact 1 |
| DIAL_NSI | GPIO 17 | IN (pull-up) | Disco contact 2 |
| HOOK_SW | GPIO 27 | IN (pull-up) | Hook switch |
| BTN_PHONEBOOK | GPIO 24 | IN (pull-up) | Button rubrica |
| BELL_IN1 | GPIO 22 | OUT | DRV8871 IN1 |
| BELL_IN2 | GPIO 23 | OUT | DRV8871 IN2 |
| LED_R | GPIO 25 | OUT (PWM) | LED rosso |
| LED_G | GPIO 8 | OUT (PWM) | LED verde |
| LED_B | GPIO 7 | OUT (PWM) | LED blu |

### Alimentazione
| Da | A | Tensione |
|----|---|----------|
| USB-C / micro-USB | DFR0969 (ricarica) | 5V |
| DFR0969 (2×18650 interne) | — | 3.0-4.2V (gestite dal modulo) |
| DFR0969 OUT 5V | Pi 5V (pin 2) | 5V regolato |
| DFR0969 OUT 5V | Tutti moduli VCC | 5V |
| DFR0969 OUT 5V | Boost IN | 5V |
| Boost OUT | DRV8871 VM | ~24V (silenzio via coast IN1=IN2=0) |
