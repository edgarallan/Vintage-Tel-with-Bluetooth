# 05 — Setup Software

## Preparazione microSD

### Su Linux/Mac
```bash
# Scarica Raspberry Pi OS Lite 64-bit (Bookworm)
wget https://downloads.raspberrypi.org/raspios_lite_arm64_latest

# Usa Raspberry Pi Imager per flashare
# Durante il flash, attiva "Edit Settings" e configura:
# - Hostname: vintagetel
# - Username/password
# - Wi-Fi
# - SSH abilitato
```

## Primo boot e setup base

```bash
ssh pi@vintagetel.local

# Update sistema
sudo apt update && sudo apt full-upgrade -y

# Pacchetti base
sudo apt install -y \
  git python3-pip python3-venv python3-dev \
  i2c-tools \
  bluez bluez-tools pulseaudio pulseaudio-module-bluetooth \
  ofono \
  libasound2-dev portaudio19-dev \
  python3-rpi.gpio python3-gpiozero \
  sqlite3 \
  build-essential cmake pkg-config
```

## Abilita interfacce hardware

```bash
sudo raspi-config nonint do_i2c 0      # I2C ON
sudo raspi-config nonint do_spi 0      # SPI ON (riserva)
```

Edita `/boot/firmware/config.txt`:
```bash
sudo nano /boot/firmware/config.txt
```

Aggiungi in fondo:
```ini
# Disabilita audio integrato (non c'è jack sul Pi Zero)
dtparam=audio=off

# Abilita I2S
dtparam=i2s=on

# DAC PCM5102A (output speaker)
dtoverlay=hifiberry-dac

# Wi-Fi power management off (chiamate stabili)
# Aggiungere riga in /etc/rc.local: iwconfig wlan0 power off
```

## Configurazione PJSIP (VoIP SIP)

PJSIP è il client SIP più solido. Lo compiliamo per supporto Python:

```bash
cd ~
wget https://github.com/pjsip/pjproject/archive/refs/tags/2.14.tar.gz
tar xzf 2.14.tar.gz
cd pjproject-2.14

./configure --enable-shared CFLAGS="-fPIC"
make dep && make -j4
sudo make install
sudo ldconfig

cd pjsip-apps/src/swig
make python
cd python
sudo python3 setup.py install
```

In alternativa più semplice usare **baresip** o **linphone-cli**, ma PJSIP è più controllabile da codice.

## Configurazione oFono per Bluetooth HFP

oFono gestisce il profilo Hands-Free Profile, che permette al Pi di "essere" un vivavoce per il cellulare:

```bash
sudo systemctl enable ofono
sudo systemctl start ofono

# Modifica configurazione BlueZ per HFP server mode
sudo nano /etc/bluetooth/main.conf
```

Aggiungi/modifica:
```ini
[General]
Class = 0x200404           # Audio - Wearable Headset
Enable = Source,Sink,Media,Socket
ControllerMode = bredr
JustWorksRepairing = always
FastConnectable = true
```

```bash
sudo systemctl restart bluetooth
```

## Accoppiamento con smartphone

```bash
sudo bluetoothctl
> power on
> agent on
> default-agent
> discoverable on
> pairable on
# Sul cellulare: cerca "vintagetel" e accoppia
> trust XX:XX:XX:XX:XX:XX   # MAC del cellulare
> exit
```

## Installazione del firmware Vintage Tel BL

```bash
cd ~
git clone https://github.com/edgarallan/vintage_tel_bl.git
cd vintage_tel_bl/firmware

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dipendenze Python
pip install -r requirements.txt

# Configurazione utente
cp config/config.example.yaml config/config.yaml
nano config/config.yaml   # modifica SIP credentials, BT device, ecc.
```

## Configurazione ALSA

Edita `/etc/asound.conf`:
```bash
sudo cp config/asound.conf /etc/asound.conf
```

Test audio:
```bash
# Test playback
speaker-test -D plughw:CARD=sndrpihifiberry -t sine -f 440 -c 1

# Test recording (se hai INMP441)
arecord -D plughw:CARD=sndrpihifiberry -f S16_LE -r 16000 -c 1 -d 5 test.wav
aplay -D plughw:CARD=sndrpihifiberry test.wav
```

## Configurazione `config.yaml`

```yaml
# Modalità: bt_only | sip_only | hybrid
mode: hybrid

# Account SIP (per modalità sip o hybrid)
sip:
  enabled: true
  username: "your_sip_user"
  password: "your_sip_password"
  domain: "sip.provider.com"
  port: 5060
  transport: udp

# Bluetooth
bluetooth:
  enabled: true
  device_name: "Vintage SIP 1970"
  auto_reconnect_mac: "AA:BB:CC:DD:EE:FF"  # MAC del tuo cellulare

# Disco combinatore
dial:
  pulse_bouncetime_ms: 50
  digit_timeout_s: 0.4    # tempo per fine cifra
  dial_timeout_s: 8        # timeout per fine numero (silenzio)
  zero_pulses: 10          # alcuni dischi italiani usano 10 impulsi per lo 0

# Hook switch (gancio)
hook:
  inverted: false   # se LOW = cornetta su (default), se inverted = HIGH = cornetta su
  debounce_ms: 100

# Campanello
bell:
  enabled: true
  frequency_hz: 22         # frequenza squillo (20-25Hz tipico)
  pattern_on_ms: 1000      # squillo: 1s on
  pattern_off_ms: 4000     # poi 4s off (pattern Telecom IT)
  
# Audio
audio:
  sample_rate: 16000
  mic_gain_db: 20
  speaker_gain_db: 0

# Display OLED
display:
  enabled: true
  i2c_address: 0x3C
  show_clock_when_idle: true
  rotation: 0

# LED RGB stato
led:
  enabled: true
  brightness: 50

# Rubrica
phonebook:
  db_path: "/home/pi/vintage_tel_bl/phonebook.db"
  quick_dial:
    1: "+393331234567"   # Mamma — premi 1 dopo aver sollevato per chiamare
    2: "+393339876543"   # Papà
    9: "112"             # Emergenze (sempre componibile)
```

## Avvio automatico

```bash
sudo cp systemd/vintage-tel.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vintage-tel
sudo systemctl start vintage-tel

# Log live
journalctl -u vintage-tel -f
```

## Aggiornamento

```bash
cd ~/vintage_tel_bl
git pull
sudo systemctl restart vintage-tel
```
