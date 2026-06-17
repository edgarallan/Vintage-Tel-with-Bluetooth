# 📞 Vintage Tel BL

> Trasforma un telefono SIP Siemens grigio anni '70 in un telefono Bluetooth + VoIP, mantenendo cornetta, disco combinatore e campanello elettromeccanico originali.

![status](https://img.shields.io/badge/status-WIP-orange)
![hardware](https://img.shields.io/badge/hardware-RPi%20Zero%202W-red)
![license](https://img.shields.io/badge/license-MIT-blue)

## Cos'è

Un retrofit hardware/software che porta un telefono SIP italiano degli anni '70 nel 2026, conservando l'estetica e la meccanica originali:

- 📱 **Funziona come vivavoce Bluetooth** per il cellulare (HFP)
- ☎️ **Disco combinatore funzionante** — gira il disco, parte la chiamata
- 🔔 **Campanello elettromeccanico originale** che squilla davvero
- 🌐 **VoIP SIP integrato** — può funzionare anche come telefono IP autonomo
- 📓 **Rubrica** con display OLED nascosto sotto il piano (opzionale, a scomparsa)
- 🔋 **Alimentazione a batteria** (2x 18650) con ricarica USB-C

## Telefono target

**Siemens/FATME S62** (o equivalente SIP grigio anni '70-'80) — quello classico con cornetta grigia, disco a 10 fori e cifre dorate. Il progetto è adattabile a qualsiasi telefono pulse-dial con minime modifiche.

## Struttura del repository

```
vintage_tel_bl/
├── README.md                    ← sei qui
├── docs/
│   ├── 01_overview.md           ← visione d'insieme e architettura
│   ├── 02_bom.md                ← bill of materials (componenti)
│   ├── 03_wiring.md             ← schema di cablaggio
│   ├── 04_installation.md       ← guida montaggio passo-passo
│   ├── 05_software_setup.md     ← installazione e configurazione software
│   ├── 06_troubleshooting.md    ← problemi comuni
│   └── 07_retrofit_layout.md    ← mappa conversione cassetta (foto annotata)
├── hardware/
│   ├── schematic.md             ← schema elettrico testuale
│   ├── pinout.md                ← mappatura GPIO
│   ├── bell_driver.md           ← circuito driver campanello 24VAC
│   └── retrofit_layout.md       ← cosa togliere/tenere/aggiungere nella cassetta
├── firmware/
│   ├── src/
│   │   ├── main.py              ← orchestratore principale
│   │   ├── dial_reader.py       ← lettura impulsi disco
│   │   ├── hook_switch.py       ← gestione gancio
│   │   ├── bell_driver.py       ← controllo campanello
│   │   ├── bt_phone.py          ← Bluetooth HFP via oFono
│   │   ├── sip_client.py        ← client VoIP SIP
│   │   ├── display.py           ← display OLED
│   │   ├── phonebook.py         ← rubrica
│   │   └── audio.py             ← gestione audio I2S
│   ├── config/
│   │   ├── config.yaml          ← configurazione utente
│   │   └── asound.conf          ← configurazione ALSA
│   ├── systemd/
│   │   └── vintage-tel.service  ← servizio systemd
│   ├── tests/                  ← suite pytest (off-Pi)
│   ├── requirements.txt
│   └── requirements-dev.txt    ← dipendenze test
└── assets/
    ├── architecture.md          ← diagramma architettura
    └── retrofit/                ← foto S62 + cassetta annotata (mappa conversione)
```

## Guida visiva al montaggio

Otto diagrammi tecnici step-by-step in [`assets/diagrams/`](assets/diagrams/):

| # | Diagramma | Step |
|---|---|---|
| 1 | [Apertura del telefono](assets/diagrams/01_opening_phone.svg) | Le viti sul fondo |
| 2 | [Mappa dei contatti originali](assets/diagrams/02_contacts_map.svg) | Disco, hook, campanello, cornetta |
| 3 | [Identificazione fili disco](assets/diagrams/03_dial_wires_identification.svg) | NSI vs Pulse col multimetro |
| 4 | [Schema generale cablaggio](assets/diagrams/04_general_wiring.svg) | Tutti i blocchi connessi |
| 5 | [Layout fisico interno](assets/diagrams/05_internal_layout.svg) | Dove posizionare ogni componente |
| 6 | [Driver campanello](assets/diagrams/06_bell_driver_schematic.svg) | Boost + H-bridge → bobine |
| 7 | [Connessioni audio](assets/diagrams/07_audio_wiring.svg) | DAC, ADC e cornetta |
| 8 | [Posizionamento display OLED](assets/diagrams/08_oled_placement_options.svg) | Tre opzioni di montaggio |

📷 **Mappa di conversione su foto reale + procedura ordinata**: [`docs/07_retrofit_layout.md`](docs/07_retrofit_layout.md) — cosa togliere/tenere/aggiungere nella cassetta S62 (verde/rosso/blu) e in che ordine smontare e montare, con collaudo a ogni passo.

## Quick start

```bash
# Su Raspberry Pi Zero 2 W con Raspberry Pi OS Lite (64-bit)
git clone https://github.com/edgarallan/vintage_tel_bl.git
cd vintage_tel_bl
sudo bash docs/install.sh    # vedi docs/05_software_setup.md
```

Poi:
1. Accoppia il tuo smartphone via Bluetooth
2. Solleva la cornetta
3. Componi un numero girando il disco
4. Riaggancia per terminare

## Sicurezza ⚠️

Questo progetto include un circuito che genera **24V AC** per il campanello originale. Non è pericoloso ma richiede attenzione nel cablaggio. Il resto è a bassissima tensione (3.3V/5V).

## Licenza

MIT — vedi [LICENSE](LICENSE)

## Crediti

Progetto ideato per portare nuova vita ai telefoni SIP italiani anni '70.
Costruito con ❤️ in Italia.
