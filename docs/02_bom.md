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
| 4 | Codec audio I2S **WM8960 (Seeed Studio)** | 1 | 10 | DAC + ampli speaker **+ preamp/ADC mic**; driver Seeed, collegare a jumper (non impilare la HAT) |
| 5 | Capsula **elettrete 9.7 mm** | 1 | 2 | Microfono cornetta (sostituisce il mic a carbone) |
| 6 | *(alternativa)* PCM5102A + PAM8302 + INMP441 | — | ~17 | Solo se **non** usi il WM8960: 3 moduli separati (DAC + ampli + mic MEMS digitale) |

**Microfono — scelta: elettrete moderno.** Un elettrete è **analogico**, e il Pi non ha
ingresso analogico: serve un codec che faccia bias + preamp + ADC. Il **WM8960** copre
tutto (e in più amplifica l'altoparlante), quindi una sola scheda sostituisce DAC +
ampli + ADC mic. La capsula elettrete 9.7 mm entra nella stessa sede meccanica della
vecchia capsula a carbone Siemens.

- ✅ **Elettrete + WM8960** (scelto): semplice, qualità migliore, un solo modulo audio.
- *Carbone originale*: suono "vintage" ma richiede bias DC + AC coupling + preamp op-amp prima del codec — più complesso.
- *INMP441 (MEMS digitale)*: si collega diretto all'I2S ma non è un elettrete; richiede comunque un DAC/ampli separati per l'uscita.

## Alimentazione

| # | Componente | Quantità | Prezzo (€) | Note |
|---|-----------|----------|-----------|------|
| 8 | Cella 18650 protetta 3500mAh (Samsung/LG) | 2 | 16 | In parallelo per autonomia |
| 9 | Modulo TP4056 con protezione DW01 + USB-C | 1 | 3 | Charger + protezione scarica |
| 10 | Boost converter MT3608 5V (o MP1584) | 1 | 3 | 3.7V → 5V per Pi |
| 11 | Portacelle 2x18650 in parallelo | 1 | 3 | Stampabile in 3D in alternativa |
| 12 | Interruttore on/off (vintage style) | 1 | 4 | Nascosto sul fondo |

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
- **AliExpress** — moduli generici (TP4056, MT3608, ecc.)
- **18650.it** — celle di qualità verificata
- **Subito.it / eBay.it** — telefoni SIP vintage italiani
