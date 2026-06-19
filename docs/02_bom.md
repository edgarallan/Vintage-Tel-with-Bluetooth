# 02 — Bill of Materials (BOM)

Prezzi indicativi 2026 in EUR, IVA inclusa. Acquisto consigliato: Mouser/RS/Digi-Key per qualità, AliExpress per economia. Per i componenti hobby (Pi, moduli) Amazon e PiMoroni vanno benissimo.

## Cervello e connettività

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 1 | Raspberry Pi Zero 2 W | 1 | 20 | Con header GPIO saldato |
| 2 | MicroSD 32GB Classe 10 (A1) | 1 | 8 | Per OS + rubrica |
| 3 | Cavo USB-C → USB-A per setup | 1 | 5 | Solo prima installazione |

## Audio

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 4 | Ampli I2S **MAX98357A** (breakout, es. Adafruit 3006) | 1 | 6 | Uscita speaker cornetta; speaker su **morsetto a vite** |
| 5 | Mic MEMS I2S **SPH0645** (breakout, es. Adafruit 3421) | 1 | 7 | Microfono, montato **nella cornetta** |

**Audio — due breakout I2S (minima saldatura).** Mic e speaker sono due moduli I2S
separati, collegati **a jumper** (solo saldature through-hole degli header, niente SMD):

- **MAX98357A** — ampli Class-D: lo speaker della cornetta (50-200 Ω) va sul morsetto a vite. Pin `GAIN` lasciato libero = +9 dB (regolabile).
- **SPH0645** — microfono MEMS digitale, piccolo: montato nella cornetta al posto della capsula a carbone (pin `SEL` → GND = canale sinistro).
- Usano **solo l'I2S** (GPIO 18/19/20/21), full-duplex con overlay mainline `googlevoicehat-soundcard` (card `sndrpigooglevoi`); nessun codec/I2C audio, l'I2C resta libero per il display.

## Alimentazione

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 8 | Cella 18650 protetta 3500mAh (Samsung/LG) | 2 | 16 | In parallelo per autonomia |
| 9 | **DFRobot DFR0969** — 2-Way 18650 Battery Holder | 1 | 11 | **All-in-one**: portacelle 2×18650 + caricabatterie (micro-USB/USB-C) + protezione + **uscita 5V/2A regolata** (e 3.3V). Sostituisce TP4056 + DW01 + MT3608 + portacelle |
| 10 | Interruttore on/off (vintage style) | 1 | 4 | Nascosto sul fondo |

> Il DFR0969 fornisce già i **5 V regolati** per Pi e moduli: **non serve un boost** sul rail logico.
> **Limite**: carica *oppure* scarica (niente pass-through/UPS) → non alimenta mentre è in carica;
> verifica sul tuo esemplare. Budget uscita **2 A** (max 3 A sconsigliato): attenzione ai picchi del campanello.
> Il boost del **campanello** (5V→~30V) resta separato (vedi sotto, XL6009).

## Driver campanello

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 13 | Boost converter regolabile XL6009 | 1 | 4 | 5V → ~30V DC |
| 14 | H-bridge L9110S oppure DRV8833 | 1 | 3 | Genera AC per il campanello |
| 15 | Trasformatore alternativo 5V → 24V AC (opzione B) | 1 | 8 | Soluzione più "pulita" |

Vedi `hardware/bell_driver.md` per le due opzioni dettagliate.

## Disco e gancio

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 16 | Optoaccoppiatore PC817 | 2 | 1 | Isolamento e debouncing HW |
| 17 | Resistori 10kΩ pull-up | 4 | <1 | Per GPIO disco e hook |
| 18 | Condensatori 100nF cer + 10µF elettr | 6 | 1 | Filtri e bypass |

## Display e interazione (opzionali ma raccomandati)

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 19 | Display OLED 0.96" 128x64 I2C (SSD1306) | 1 | 5 | Mostra numero, stato, rubrica |
| 20 | LED RGB diffuso 5mm (status) | 1 | 1 | Stato sistema (idle/call/error) |
| 21 | Microswitch piccolo (button rubrica) | 1 | 1 | Nascosto sotto il piano |

## Cablaggio e meccanica

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 22 | PCB perfboard 7x9cm | 2 | 3 | Per le interfacce |
| 23 | Connettori JST-XH 2-4 pin | 10 | 4 | Cablaggi modulari |
| 24 | Cavetto 26AWG flessibile (vari colori) | 5m | 5 | Cablaggio interno |
| 25 | Stagno + flussante | - | 5 | |
| 26 | Termorestringente vari diametri | - | 3 | |
| 27 | Distanziali in nylon M2.5 | 10 | 3 | Per montare il Pi |
| 28 | Velcro biadesivo industriale | 1 | 4 | Fissaggio batterie |

## Totale stimato

| Configurazione | Costo |
|----------------|-------|
| **Minimo** (BT + disco + hook) | ~80 € |
| **Medio** (+ campanello + LED) | ~100 € |
| **Massimo** (+ display + rubrica) | ~120 € |

Esclusi spese di spedizione e il telefono SIP stesso (sui mercatini italiani 20-50 €).

## Strumenti necessari

- Saldatore a temperatura regolabile (T18 o JBC)
- Multimetro
- Oscilloscopio (raccomandato per debug disco)
- Cacciaviti specifici Siemens (testa cilindrica)
- Stampante 3D (opzionale, per supporti interni custom)

## Fornitori consigliati

- **PiMoroni / The Pi Hut** — Raspberry Pi e moduli HAT
- **Mouser / RS Components** — componenti elettronici qualità
- **DFRobot** — modulo alimentazione DFR0969 (anche via rivenditori/Mouser)
- **AliExpress** — moduli generici (XL6009, L9110S, ecc.)
- **18650.it** — celle di qualità verificata
- **Subito.it / eBay.it** — telefoni SIP vintage italiani
