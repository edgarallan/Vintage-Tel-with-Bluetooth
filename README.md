# 📞 Vintage Tel BL

> Trasforma un telefono SIP Siemens grigio anni '70 in un **vivavoce Bluetooth** (con VoIP SIP opzionale), mantenendo cornetta, disco combinatore e campanello elettromeccanico originali.

![status](https://img.shields.io/badge/status-WIP-orange)
![hardware](https://img.shields.io/badge/hardware-RPi%20Zero%202W-red)
![tests](https://img.shields.io/badge/tests-pytest%20(off--Pi)-green)
![license](https://img.shields.io/badge/license-MIT-blue)

## Cos'è

Un retrofit hardware/software che porta un telefono SIP italiano degli anni '70 nel presente, conservando estetica e meccanica originali:

- 📱 **Vivavoce Bluetooth (HFP)** per il cellulare — è il cellulare a telefonare, il vecchio apparecchio è l'interfaccia fisica
- ☎️ **Disco combinatore funzionante** — giri il disco, parte la chiamata
- 🔔 **Campanello elettromeccanico originale** che squilla davvero
- 🌐 **VoIP SIP opzionale** — può funzionare anche come telefono IP autonomo via Wi-Fi
- 📓 **Rubrica** con display OLED nascosto (opzionale)
- 🔋 **Alimentazione a batteria** (2×18650) con ricarica USB-C

**Telefono target:** Siemens/FATME **S62 "Bigrigio"** (o equivalente SIP pulse-dial). Adattabile ad altri telefoni a disco con minime modifiche.

## Come funziona (modalità Bluetooth)

Il Raspberry Pi fa da **vivavoce HFP** accoppiato al tuo cellulare (via oFono): la telefonia vera resta sul cellulare, l'apparecchio vintage è l'interfaccia.

| Azione | Cosa passa sul Bluetooth | Modulo |
|--------|--------------------------|--------|
| Componi col disco | cifre → comando `Dial` HFP → il cellulare chiama | `dial_reader` → `bt_phone` |
| Ricevi (squillo) | chiamata in arrivo sul cellulare → notifica HFP → campanello | `bt_phone` → `bell_driver` |
| Parla/ascolta | audio bidirezionale via Bluetooth SCO (HFP) | oFono / I2S |
| Riaggancia | cornetta giù → `Hangup` HFP | `hook_switch` → `bt_phone` |

**Modalità operative** (`mode` in `config.yaml`): `bt_only` · `sip_only` · `hybrid` (BT se connesso, altrimenti SIP).

## 📚 Documentazione

Guida completa nella cartella [`docs/`](docs/) (italiano, numerata in sequenza di build):

| # | Documento | Contenuto |
|---|-----------|-----------|
| 01 | [Panoramica e architettura](docs/01_overview.md) | Visione d'insieme, stati, moduli |
| 02 | [Bill of Materials](docs/02_bom.md) | Componenti, prezzi indicativi, fornitori, strumenti |
| 03 | [Schema di cablaggio](docs/03_wiring.md) | Pinout, disco, gancio, audio, campanello, alimentazione |
| 04 | [Guida installazione hardware](docs/04_installation.md) | Montaggio passo-passo (Step 1–11) |
| 05 | [Setup software](docs/05_software_setup.md) | OS, pacchetti, overlay I2S, oFono, build PJSIP |
| 06 | [Troubleshooting](docs/06_troubleshooting.md) | Problemi comuni e soluzioni |
| 07 | [Mappa di conversione cassetta](docs/07_retrofit_layout.md) | Cosa togliere/tenere/aggiungere + ordine operazioni |

Riferimenti hardware in [`hardware/`](hardware/):

| File | Contenuto |
|------|-----------|
| [`pinout.md`](hardware/pinout.md) | Mappatura GPIO completa (BCM ↔ pin fisici) |
| [`schematic.md`](hardware/schematic.md) | Schema elettrico testuale + tabelle connessioni |
| [`bell_driver.md`](hardware/bell_driver.md) | Driver campanello 24V AC (boost + H-bridge) |
| [`retrofit_layout.md`](hardware/retrofit_layout.md) | Mappa tecnica conversione cassetta (terminali S62, GPIO) |

## 🖼️ Guida visiva

Nove diagrammi tecnici in [`assets/diagrams/`](assets/diagrams/) (SVG autoportanti, light/dark mode):

| # | Diagramma | Usato in |
|---|-----------|----------|
| 1 | [Apertura del telefono](assets/diagrams/01_opening_phone.svg) | docs/04 · Step 1 |
| 2 | [Mappa dei contatti originali](assets/diagrams/02_contacts_map.svg) | docs/04 · Step 2 |
| 3 | [Identificazione fili disco](assets/diagrams/03_dial_wires_identification.svg) | docs/04 · Step 2 |
| 4 | [Schema generale cablaggio](assets/diagrams/04_general_wiring.svg) | docs/03 |
| 5 | [Layout fisico interno](assets/diagrams/05_internal_layout.svg) | docs/04 · Step 5 |
| 6 | [Driver campanello](assets/diagrams/06_bell_driver_schematic.svg) | docs/04 · Step 7 |
| 7 | [Connessioni audio](assets/diagrams/07_audio_wiring.svg) | docs/04 · Step 8 |
| 8 | [Posizionamento display OLED](assets/diagrams/08_oled_placement_options.svg) | docs/04 · Step 9 |
| 9 | [Mappa di conversione (schematico)](assets/diagrams/09_conversion_map.svg) | docs/07 |

📷 **Mappa di conversione su foto reale + procedura ordinata**: [`docs/07_retrofit_layout.md`](docs/07_retrofit_layout.md) — cosa togliere/tenere/aggiungere nella cassetta S62 (verde/rosso/blu) e in che ordine smontare e montare, con collaudo a ogni passo. Foto in [`assets/retrofit/`](assets/retrofit/).

## 🔧 Montaggio hardware (in sintesi)

Costo stimato **~80–120 €** (vedi [BOM](docs/02_bom.md)); il telefono vintage 20–50 € sui mercatini.

1. **Apri** il telefono e **fotografa/etichetta** i fili originali → [docs/04](docs/04_installation.md)
2. **Mappa i contatti** col multimetro (disco: impulsi + NSI; gancio; campanello ≈1700 Ω) → [docs/03](docs/03_wiring.md)
3. **Svuota** la fascia centrale: rimuovi trasformatore + condensatore/rete analogica → [docs/07](docs/07_retrofit_layout.md)
4. **Monta** Raspberry Pi, DAC/ampli I2S, mic in cornetta, boost + H-bridge per il campanello → [docs/04](docs/04_installation.md)
5. **Collauda un blocco alla volta** prima di richiudere (vedi sotto)

> L'ordine consigliato (smontaggio → montaggio con verifica) è in [docs/07 · Procedura](docs/07_retrofit_layout.md#procedura-consigliata-lordine-conta).

## 💻 Setup software

Guida completa: [docs/05](docs/05_software_setup.md).

```bash
# Su Raspberry Pi Zero 2 W con Raspberry Pi OS Lite (64-bit, Bookworm)
git clone https://github.com/edgarallan/vintage_tel_bl.git
cd vintage_tel_bl
sudo bash docs/install.sh
```

L'installer prepara dipendenze, overlay I2S, oFono/BlueZ, copia `asound.conf` e crea `firmware/config/config.yaml` da `config.example.yaml`.

## ⚙️ Configurazione

`config.yaml` (creato da [`firmware/config/config.example.yaml`](firmware/config/config.example.yaml)) — **non committarlo**, contiene credenziali SIP e MAC del cellulare. Chiavi principali:

| Sezione | Chiave | Significato |
|---------|--------|-------------|
| — | `mode` | `bt_only` / `sip_only` / `hybrid` |
| `bluetooth` | `device_name`, `auto_reconnect_mac` | Nome BT mostrato e MAC del cellulare |
| `dial` | `zero_pulses` | 10 impulsi = `0` (convenzione IT) |
| `dial` | `digit_timeout_s` | Fallback fine-cifra se il rilascio NSI si perde (`0` = off) |
| `dial` | `quick_dial_timeout_s` | Attesa per attivare il quick-dial su singola cifra |
| `hook` | `inverted` | Inverte la logica del gancio se il tuo esemplare differisce |
| `bell` | `frequency_hz`, `pattern_on_ms`, `pattern_off_ms` | Squillo (default 22 Hz, 1s/4s) |
| `audio` | `sample_rate`, `speaker_gain_db`, `mic_gain_db` | I gain pilotano i softvol ALSA (cornetta) |
| `phonebook` | `quick_dial` | Mappa cifra → numero (es. `9: "112"`) |

## ☎️ Uso quotidiano

1. Accoppia lo smartphone via Bluetooth (nome da `device_name`)
2. **Solleva la cornetta** → tono di libero
3. **Componi** girando il disco (oppure singola cifra quick-dial)
4. **Riaggancia** per terminare. In arrivo: il campanello suona, sollevi per rispondere.

## 🛠️ Comandi utili

```bash
# Test hardware di bring-up (PRIMA di richiudere la scocca)
cd firmware && source venv/bin/activate
python -m src.test_hardware              # LED/display/gancio/disco/campanello/audio
python -m src.test_hardware --monitor    # monitor live GPIO (gancio + disco)
python -m src.dial_reader                # test standalone del disco

# Esecuzione manuale (al posto del servizio)
python -m src.main

# Servizio systemd
sudo systemctl {start,stop,restart,status} vintage-tel
journalctl -u vintage-tel -f
```

## 🧪 Test

Suite `pytest` eseguibile **off-Pi** (i driver hardware degradano via `try/except ImportError`):

```bash
cd firmware
python3 -m venv .venv-test
.venv-test/bin/pip install -r requirements-dev.txt
.venv-test/bin/python -m pytest
```

Copre state machine, lettore disco, selezione backend, rubrica e config audio. I driver GPIO/DBus/PJSIP si validano sul Pi con `src/test_hardware.py`.

## 🧯 Troubleshooting

Problemi comuni (audio mono-direzionale, disco che salta cifre, campanello debole, BT che non si accoppia…) in [docs/06](docs/06_troubleshooting.md).

## 🗂️ Struttura del repository

```
vintage_tel_bl/
├── README.md                    ← sei qui
├── docs/                        ← guida di build (01–07) + install.sh
├── hardware/                    ← pinout, schema, driver campanello, retrofit
├── firmware/
│   ├── src/                     ← applicazione asyncio (main + moduli)
│   ├── tests/                   ← suite pytest (off-Pi)
│   ├── config/                  ← config.example.yaml + asound.conf
│   ├── systemd/                 ← vintage-tel.service
│   ├── requirements.txt         ← dipendenze runtime
│   └── requirements-dev.txt     ← dipendenze test
└── assets/
    ├── architecture.md          ← diagramma architettura
    ├── diagrams/                ← 8 diagrammi SVG di montaggio
    └── retrofit/                ← foto S62 + cassetta annotata (mappa conversione)
```

## ⚠️ Sicurezza

Il circuito del campanello genera **~24V AC**: non pericoloso ma richiede attenzione nel cablaggio. Tutto il resto è a bassissima tensione (3.3V/5V). Verifica sempre i collegamenti prima di alimentare.

## Licenza

MIT — vedi [LICENSE](LICENSE)

## Crediti

Progetto ideato per portare nuova vita ai telefoni SIP italiani anni '70. Costruito con ❤️ in Italia.
