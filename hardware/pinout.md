# Pinout Quick Reference

```
                Raspberry Pi Zero 2 W — Pinout 40 pin
                
        3V3  (1) ── (2)  5V     ◄── 5V dal DFR0969
   SDA I2C  (3) ── (4)  5V
   SCL I2C  (5) ── (6)  GND
      DIAL  (7) ── (8)  TXD (debug serial)
       GND  (9) ── (10) RXD (debug serial)
   DIAL_NSI (11)── (12) I2S BCK
                  
       PWM (13) ── (14) GND     HOOK_SW = GPIO 27 (BCM) = pin 13
   BELL_EN (15)── (16) BELL_PH  GPIO 22, 23
       3V3 (17)── (18) BTN_PB   GPIO 24 (button rubrica)
      MOSI (19)── (20) GND
      MISO (21)── (22) LED_R    GPIO 25
      SCLK (23)── (24) LED_G    GPIO 8
       GND (25)── (26) LED_B    GPIO 7
      ID_SD(27)── (28) ID_SC
        -- (29)── (30) GND
        -- (31)── (32) --
   I2S LRCK(33)── (34) GND
   I2S DIN (35)── (36) --
        -- (37)── (38) --
       GND (39)── (40) I2S DOUT
```

| Funzione | Nome BCM | Pin fisico | Tipo |
|---|---|---|---|
| Display I2C SDA | GPIO 2 | 3 | I2C |
| Display I2C SCL | GPIO 3 | 5 | I2C |
| Disco - impulsi | GPIO 4 | 7 | Input, pull-up |
| Disco - NSI | GPIO 17 | 11 | Input, pull-up |
| Hook switch | GPIO 27 | 13 | Input, pull-up |
| Audio I2S BCK | GPIO 18 | 12 | I2S |
| Audio I2S LRCK | GPIO 19 | 35 | I2S |
| Audio I2S DIN | GPIO 20 | 38 | I2S in (mic SPH0645) |
| Audio I2S DOUT | GPIO 21 | 40 | I2S out (ampli MAX98357A) |
| Campanello EN | GPIO 22 | 15 | Output |
| Campanello fase | GPIO 23 | 16 | Output PWM |
| Bottone rubrica | GPIO 24 | 18 | Input, pull-up |
| LED Rosso | GPIO 25 | 22 | Output PWM |
| LED Verde | GPIO 8 | 24 | Output PWM |
| LED Blu | GPIO 7 | 26 | Output PWM |
