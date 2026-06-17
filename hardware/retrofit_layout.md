# Mappa di conversione — cosa togliere, cosa tenere, cosa aggiungere

Riferimento visivo per svuotare la cassetta del **Siemens/FATME S62 "Bigrigio"**
e ripopolarla con l'elettronica del progetto, conservando le parti meccaniche
e il campanello originali.

## Foto annotata

![Cassetta S62 annotata](../assets/retrofit/cassetta_annotata.png)

> Verde = tenere · Rosso = rimuovere · Blu = nuovo. Le posizioni dei riquadri
> sono **indicative**: verifica sempre sul tuo esemplare prima di tagliare.

Materiale di riferimento:
- Schema originale Siemens S62: [`../assets/retrofit/s62_schema.jpg`](../assets/retrofit/s62_schema.jpg)
- Foto cassetta smontata (sorgente): [`../assets/retrofit/cassetta_smontata.jpg`](../assets/retrofit/cassetta_smontata.jpg)

## 1. Cosa TENERE (e ricablare)

| # | Componente | Dove (foto) | Cosa fare | GPIO |
|---|-----------|-------------|-----------|------|
| 1 | **Commutatore a gancio** (contatti `GC` sotto la culla) | centro-alto | Usa **un solo** contatto pulito (SPST), un capo a GPIO, l'altro a GND. Pull-up interno via SW. | **GPIO 27** |
| 6 | **Disco combinatore** (terminali `DISCO 1-5` dello schema) | alto | Servono **due** contatti: impulsi + NSI ("off-normal"). Identificali col tester (vedi sotto). | **GPIO 4** (impulsi), **GPIO 17** (NSI) |
| 5 | **Campanello**: due campane + bobina (≈ **1700 Ω**, lato `S/b 1700` dello schema) | angoli bassi | Scollega dalla linea; pilota la bobina dal nostro driver boost + H-bridge. | **GPIO 22** (EN), **GPIO 23** (fase) |
| 4 | **Morsettiera** linea/cornetta | basso-centro | Riusala come **nodo di cablaggio** interno (GND, 5V/3V3, segnali). | — |

Note:
- L'**altoparlante** della cornetta (capsula `M/R`, 50–200 Ω) si tiene e si pilota dall'ampli I2S (vedi #8).
- La **capsula microfonica a carbone** (`M`) si sostituisce (vedi #10).

## 2. Cosa RIMUOVERE

| # | Componente | Dove (foto) | Perché |
|---|-----------|-------------|--------|
| 2 | **Bobina d'induzione / trasformatore** (blocco verde-giallo) | centro | Era l'ibrido anti-locale analogico: sostituito da Pi + audio digitale I2S. |
| 3 | **Condensatore + rete analogica** (blocco bianco + tubo di vetro; caps `2,2µF / 1µF / 0,1µF`, resistori `47/29/390/100`, varistore `30`) | centro-basso | Circuito fonia/soppressione scintilla del telefono originale: non più necessario. |

Rimuovendo **2** e **3** si libera tutta la fascia centrale della cassetta: è
lì che va il Raspberry Pi.

## 3. Cosa AGGIUNGERE (componenti nuovi)

| # | Componente | Posizione consigliata |
|---|-----------|-----------------------|
| 7 | **Raspberry Pi Zero 2 W** | Spazio centrale liberato da 2+3 (zona più piatta e ampia). |
| 8 | **DAC/ampli I2S** (PCM5102A + PAM8302, o MAX98357A) | Vicino ai morsetti dell'auricolare (lato sinistro), cavo corto verso lo speaker. |
| 9 | **Boost (XL6009) + H-bridge (L9110S)** per il campanello | Vicino alla bobina del campanello (basso), cavi corti. |
| 10 | **Microfono I2S INMP441** | **Nella cornetta**, al posto della capsula a carbone — non in base. |

Alimentazione (vedi [`schematic.md`](schematic.md)): batteria 2×18650 → TP4056 →
MT3608 (5V logica) e XL6009 (alta tensione campanello, attiva solo allo squillo).

## Identificazione contatti col multimetro

**Disco** (continuità):
1. A riposo: NSI chiuso, impulsi chiuso.
2. Inizio rotazione: **NSI apre** → è la coppia NSI (→ GPIO 17).
3. Durante il ritorno: una coppia **apre/chiude N volte** → impulsi (→ GPIO 4).

**Campanello**: misura la resistenza tra i capi della bobina → ≈ 1–2 kΩ
(nominale 1700 Ω). Quei due capi vanno all'uscita dell'H-bridge.

**Gancio**: i contatti sotto la culla; la logica (chiuso = giù / su) può variare
per esemplare → si gestisce con `hook.inverted` in `config.yaml`.

## Riferimenti

- Pinout completo: [`pinout.md`](pinout.md)
- Schema elettrico del retrofit: [`schematic.md`](schematic.md)
- Driver campanello (24V AC): [`bell_driver.md`](bell_driver.md)
- Guida passo-passo: [`../docs/04_installation.md`](../docs/04_installation.md)
