# Driver Campanello — Riportare in vita le campane

Il campanello del SIP è il dettaglio che fa la differenza. È un meccanismo elettromagnetico originariamente alimentato dalla centrale telefonica con corrente alternata a ~25Hz e ~75V RMS. Per ragioni di sicurezza ed efficienza, generiamo qualcosa di simile ma a tensione ridotta — il funzionamento è perfetto a 20-30V AC.

## Come funziona il campanello originale

Due bobine in serie attorno a un nucleo ferromagnetico. Quando ci passa corrente alternata, il martelletto (un pezzo di ferro magnetizzato) viene spinto alternativamente verso una campana, poi verso l'altra. Risultato: il classico "DRIN-DRIN".

```
        ┌──────────┐         ┌──────────┐
        │  Campana │         │  Campana │
        │ sinistra │         │  destra  │
        └──────────┘         └──────────┘
              ║                   ║
              ╠═══[Martelletto]═══╣
              ║                   ║
        ┌─────╨─────┐       ┌─────╨─────┐
        │  Bobina   │       │  Bobina   │
        │  sinistra │═══════│  destra   │
        └───────────┘       └───────────┘
              │                   │
              └────── 2 fili ─────┘
                     ║   ║
                    AC ~24V @ 22Hz
```

## Opzione A — H-bridge + Boost converter (consigliata, economica)

### Schema

```
                                                                  ┌─────────┐
                                                                  │ Bobine  │
                                                                  │ campan. │
   +5V                                                            │ (orig.) │
    │                                                             └────┬────┘
    │     ┌─────────┐         ┌──────────┐                             │
    ├─────┤ XL6009  │── +30V ─┤  L9110S  │── OUT1 ─────────────────────┤
    │     │ boost   │         │  H-bridge│                             │
    │     │ DC-DC   │         │          │── OUT2 ─────────────────────┘
    │     └─────────┘         │          │
    │          │              │   IN1 ◄──┼──── GPIO 23 (BELL_PH)
    │          │              │   IN2 ◄──┼──── GPIO 23 (inverted via NOT gate)
    │     GPIO 22 (BELL_EN)   │          │
    │     enable boost        └──────────┘
    │
   GND
```

### Funzionamento

1. **Pi alza GPIO 22 (BELL_EN)** → il boost converter XL6009 viene alimentato e genera ~30V DC. Quando GPIO 22 = 0, il boost si spegne (zero consumo).
2. **Pi alterna GPIO 23 (BELL_PH)** a ~22Hz (44 transizioni al secondo):
   - GPIO 23 HIGH → IN1=1, IN2=0 → corrente nella bobina in un senso
   - GPIO 23 LOW  → IN1=0, IN2=1 → corrente nella bobina nel senso opposto
3. L'H-bridge L9110S genera ai suoi capi (OUT1, OUT2) un'onda quadra di ±30V → applicata alle bobine fa oscillare il martelletto.

**Trucco GPIO singolo**: per evitare di usare 2 GPIO, si può:
- Mandare GPIO 23 sia a IN1 sia a IN2 tramite un piccolo inverter (74HC04 o transistor NPN) — un solo segnale logico controlla la fase

### Componenti

| Componente | Specifica | Note |
|-----------|-----------|------|
| XL6009 boost | 5V → 30V regolabile | Regola il trimmer a vuoto a 30V |
| L9110S | H-bridge, 800mA continui, 1.5A picco | Sufficiente per le bobine SIP |
| Diodi flyback | 1N4007 o 1N5819 schottky | Opzionali, l'L9110S ha già protezione interna |

### Codice

Vedi `firmware/src/bell_driver.py` — implementazione completa con pattern italiano (1s on, 4s off ciclico, fino a hook up o timeout).

### Pro e contro

✅ Economico (~7€ totali)  
✅ Componenti facilmente reperibili  
✅ Zero rumore in idle (boost completamente spento)  
✅ Frequenza e ampiezza regolabili da software  

⚠️ Onda quadra invece di sinusoidale — il campanello suona leggermente più "secco" rispetto all'originale a 75V sinusoidale, ma rimane gradevolissimo  
⚠️ Picchi induttivi sulle bobine — l'L9110S li gestisce ma per progetti seri meglio aggiungere snubber RC (100nF + 10Ω) in parallelo alle uscite  

## Opzione B — Trasformatore + Oscillatore (più autentica)

### Schema concettuale

```
   +5V ─── Oscillatore (NE555 o GPIO) ── Driver MOSFET ── Trasformatore 5V:24V
                  22Hz                                          │
                                                                │
                                                          ┌─────┴─────┐
                                                          │  Bobine   │
                                                          │ campanello│
                                                          └───────────┘
```

Un trasformatore EI step-up commerciale (5V → 24V) o un piccolo trasformatore di ferrite pilotato a frequenza variabile genera l'onda AC quasi sinusoidale.

### Pro e contro

✅ Suono identico all'originale (sinusoide pura)  
✅ Isolamento galvanico tra logica e campanello  

❌ Trasformatori 5V:24V a bassa frequenza sono ingombranti (~3×3×4cm)  
❌ Più costoso (~12€)  
❌ Pilotaggio meno preciso  

## Quale scegliere?

**Per il 90% dei casi**: Opzione A.

L'orecchio umano non distingue significativamente tra onda quadra e sinusoidale su un trasduttore meccanico come le bobine del campanello — il sistema è naturalmente "filtrante" per la sua inerzia meccanica.

## Pattern di squillo italiano

Il pattern Telecom Italia tradizionale:

```
ON  ████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░████████████░░░...
    1 sec        4 sec di pausa                 1 sec
```

Il file `bell_driver.py` implementa questo pattern. Personalizzabile via `config.yaml`:

```yaml
bell:
  pattern_on_ms: 1000   # 1 secondo squillo
  pattern_off_ms: 4000  # 4 secondi pausa
  max_rings: 30         # massimo 30 squilli (~2.5 minuti)
```

## Verifica meccanica del campanello

Prima di pilotarlo elettronicamente, verifica meccanicamente:

1. Il martelletto deve essere libero di oscillare con le dita, senza attriti
2. Le campane devono essere ben fissate ai loro perni
3. La distanza martelletto-campana a riposo deve essere ~1-2mm da entrambi i lati
4. Spruzza un velo di olio penetrante sul perno del martelletto se mostra resistenza

## ⚠️ Sicurezza

- **30V DC non sono pericolosi al tatto** in condizioni normali
- Le bobine immagazzinano energia: spegni sempre BELL_EN prima di scollegare cavi
- L'H-bridge può scaldare durante squilli prolungati — verifica che non superi 60°C
- **Non far suonare il campanello vicino all'orecchio** — è MOLTO più forte di quanto sembri (~70-75 dB a 30cm)
