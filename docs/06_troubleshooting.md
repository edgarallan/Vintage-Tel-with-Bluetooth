# 06 — Troubleshooting

## Il disco compone cifre sbagliate

### Sintomo: compongo 5 e legge 4 (o 6)
**Causa**: bouncing dei contatti meccanici.

**Soluzione**:
1. Aumenta `pulse_bouncetime_ms` in `config.yaml` da 50 a 80
2. Pulisci i contatti del disco con alcool isopropilico + carta da fumo
3. Verifica con oscilloscopio: gli impulsi dovrebbero essere ~50ms larghi a 10Hz

### Sintomo: lo 0 non funziona
**Causa**: il numero di impulsi per lo zero varia per standard nazionale.

**Soluzione**: 
- Italia/Europa: 10 impulsi → cifra 0 (default)
- UK/Svezia: 10 impulsi → cifra 0
- Nuova Zelanda inverso: 10 - N impulsi
- Verifica `zero_pulses` in `config.yaml`

### Sintomo: il disco compone una cifra "fantasma" all'inizio
**Causa**: il contatto NSI rimbalza all'inizio della rotazione e viene letto come pulse.

**Soluzione**: 
- Assicurati che `dial_reader.py` usi NSI come "gate" — gli impulsi pulse contano SOLO quando NSI è attivo
- Verifica che gli interrupt GPIO siano configurati correttamente

## Audio problemi

### Sintomo: speaker non emette suono
1. `aplay -l` deve elencare la scheda HiFiBerry DAC
2. Verifica volume: `alsamixer` → seleziona la scheda → alza tutti i canali
3. Verifica cablaggio I2S: BCK, LRCK, DOUT su pin 12, 35, 40
4. Verifica alimentazione 5V del PCM5102A (misurare con multimetro)

### Sintomo: microfono troppo basso o nessun audio in entrata
1. Se usi mic a carbone: verifica il bias DC (3-5V su Mic+)
2. Se usi INMP441: il pin L/R va a GND (canale sinistro) o VCC (destro)
3. Aumenta `mic_gain_db` in config.yaml fino a 30-40 dB
4. Test diretto: `arecord -D plughw:CARD=sndrpihifiberry -f S16_LE -r 16000 -d 5 test.wav && aplay test.wav`

### Sintomo: eco o microfono che si sente sullo speaker
1. Abilita echo cancellation in PulseAudio:
   ```bash
   pactl load-module module-echo-cancel aec_method=webrtc
   ```
2. Aumenta la distanza fisica tra mic e speaker dentro la cornetta (improbabile)
3. Riduci `speaker_gain_db`

### Sintomo: audio "metallico" o distorto via Bluetooth
1. Il profilo HFP usa codec CVSD (8kHz) o mSBC (16kHz)
2. Forza mSBC: `sudo nano /etc/pulse/default.pa` → aggiungi `load-module module-bluetooth-policy auto_switch=2`
3. Riavvia: `pulseaudio -k && pulseaudio --start`

## Bluetooth

### Sintomo: il cellulare non si accoppia
1. Su cellulare: dimentica vecchi accoppiamenti del telefono SIP
2. Su Pi:
   ```bash
   sudo bluetoothctl
   > remove XX:XX:XX:XX:XX:XX
   > power off
   > power on
   > discoverable on
   > pairable on
   ```
3. Riprova accoppiamento

### Sintomo: si accoppia ma il telefono SIP non appare come vivavoce sul cellulare
1. Verifica che la `Class` in `/etc/bluetooth/main.conf` sia `0x200404`
2. Verifica che oFono sia attivo: `systemctl status ofono`
3. Su Android: vai in dettagli del dispositivo accoppiato e attiva "Audio chiamate"

### Sintomo: chiamate audio funzionano ma non riesco a comporre numeri dal disco
1. Il profilo HFP supporta comandi DTMF AT
2. Verifica che `bt_phone.py` invii i comandi `AT+VTS=N` per ogni cifra
3. Log: `journalctl -u ofono -f` durante la chiamata

## Campanello

### Sintomo: il campanello non suona
1. Verifica che il boost XL6009 generi davvero ~30V (multimetro)
2. Verifica i contatti dell'H-bridge (L9110S): IN1 e IN2 devono alternare
3. Test manuale GPIO:
   ```bash
   python3 -c "
   import RPi.GPIO as GPIO, time
   GPIO.setmode(GPIO.BCM)
   GPIO.setup(22, GPIO.OUT); GPIO.setup(23, GPIO.OUT)
   GPIO.output(22, 1)  # enable boost
   for _ in range(100):
       GPIO.output(23, 1); time.sleep(0.022)
       GPIO.output(23, 0); time.sleep(0.022)
   GPIO.output(22, 0)
   GPIO.cleanup()
   "
   ```

### Sintomo: il campanello suona ma il suono è "fiacco"
1. La tensione deve essere ~24-30V AC peak-to-peak
2. La frequenza ottimale dipende dalla risonanza meccanica delle bobine — prova 18, 20, 22, 25 Hz
3. Verifica che il martelletto colpisca centralmente entrambe le campane

### Sintomo: il campanello tintinna ma non suona pulito
1. Lubrifica il perno del martelletto
2. Regola la posizione del martelletto a riposo (deve essere equidistante)
3. Pulisci le campane

## Sistema generale

### Sintomo: il servizio crasha continuamente
```bash
journalctl -u vintage-tel -n 100 --no-pager
```
Cerca traceback Python. I problemi più comuni:
- Permessi GPIO → assicurati che l'utente del servizio sia in gruppo `gpio` e `i2c`
- Permessi audio → gruppo `audio`
- PJSIP non trovato → reinstalla in venv

### Sintomo: batteria si scarica troppo in fretta
1. Wi-Fi power management ON: `sudo iwconfig wlan0 power on`
2. Display OLED spento quando in idle (vedi `display.py`)
3. CPU governor su `powersave`:
   ```bash
   echo powersave | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```
4. Disabilita servizi non necessari (HDMI, ecc.)

### Sintomo: il telefono si scalda
- Normale: il Pi Zero 2W in idle scalda ~5-10°C sopra l'ambiente
- Boost converter caldo è normale durante lo squillo (alta corrente)
- Se scalda molto durante chiamate: aggiungi piccolo dissipatore sul Pi

## Debugging

### Live monitoring di tutti i GPIO
```bash
cd ~/vintage_tel_bl/firmware
python3 -m src.test_hardware --monitor
```

Output in tempo reale di hook, disco, batteria, stato chiamata.

### Modalità verbose
In `config.yaml`:
```yaml
logging:
  level: DEBUG
  log_file: /var/log/vintage-tel.log
```

### Reset di fabbrica software
```bash
sudo systemctl stop vintage-tel
rm ~/vintage_tel_bl/firmware/config/config.yaml
cp ~/vintage_tel_bl/firmware/config/config.example.yaml ~/vintage_tel_bl/firmware/config/config.yaml
sudo systemctl start vintage-tel
```
