# 07 — Mappa di conversione della cassetta

Da consultare **dopo** l'apertura del telefono (Step 1–2 di
[`04_installation.md`](04_installation.md)) e **prima** di rimuovere qualcosa:
cosa togliere, cosa tenere e dove sistemare i componenti nuovi.

![Cassetta S62 annotata](../assets/retrofit/cassetta_annotata.png)

> 🟩 verde = tenere · 🟥 rosso = rimuovere · 🟦 blu = nuovo.
> Le posizioni sono **indicative**: verifica sempre sul tuo esemplare.

## In breve

| Azione | Componenti | Note |
|--------|-----------|------|
| **Tieni** | Disco combinatore, commutatore a gancio, campanello (campane + bobina), morsettiera, altoparlante cornetta | Da ricablare verso il Pi (vedi [`03_wiring.md`](03_wiring.md)) |
| **Rimuovi** | Bobina d'induzione (trasformatore), condensatore + rete analogica (resistori/varistore) | Era il circuito fonia analogico, ora sostituito da Pi + I2S |
| **Aggiungi** | Raspberry Pi Zero 2 W, DAC/ampli I2S, boost + H-bridge campanello, mic INMP441 (in cornetta) | Il Pi va nello spazio centrale liberato |

## Mappatura completa

Tabelle dettagliate (terminali dello schema S62, valori, GPIO) e identificazione
dei contatti col multimetro: vedi [`../hardware/retrofit_layout.md`](../hardware/retrofit_layout.md).

| # | Tieni / Rimuovi / Aggiungi | Componente | GPIO |
|---|----------------------------|-----------|------|
| 1 | Tieni | Commutatore a gancio | GPIO 27 |
| 6 | Tieni | Disco combinatore (impulsi + NSI) | GPIO 4 / GPIO 17 |
| 5 | Tieni | Campanello (bobina ≈ 1700 Ω) | GPIO 22 / GPIO 23 |
| 4 | Tieni | Morsettiera (nodo di cablaggio) | — |
| 2 | Rimuovi | Bobina d'induzione / trasformatore | — |
| 3 | Rimuovi | Condensatore + rete analogica | — |
| 7 | Aggiungi | Raspberry Pi Zero 2 W (zona centrale) | — |
| 8 | Aggiungi | DAC/ampli I2S (vicino auricolare) | I2S |
| 9 | Aggiungi | Boost + H-bridge (vicino campanello) | — |
| 10 | Aggiungi | Mic INMP441 (nella cornetta) | I2S |

## Materiale di riferimento

- Schema originale Siemens S62: [`../assets/retrofit/s62_schema.jpg`](../assets/retrofit/s62_schema.jpg)
- Foto cassetta smontata: [`../assets/retrofit/cassetta_smontata.jpg`](../assets/retrofit/cassetta_smontata.jpg)
- Mappa tecnica completa: [`../hardware/retrofit_layout.md`](../hardware/retrofit_layout.md)
