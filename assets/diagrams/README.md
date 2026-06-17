# Diagrammi di montaggio

Otto diagrammi **SVG** che guidano nel retrofit hardware del telefono SIP S62.

Gli SVG sono **autoportanti**: stili e palette inline, nessuna dipendenza
esterna, font di sistema. Si visualizzano correttamente su GitHub (light **e**
dark mode, tramite `@media (prefers-color-scheme)`) e aprendoli nel browser.

| # | File | Cosa mostra | Usato in |
|---|------|-------------|----------|
| 1 | [`01_opening_phone.svg`](01_opening_phone.svg) | Apertura del telefono — le due viti sul fondo | [docs/04](../../docs/04_installation.md) · Step 1 |
| 2 | [`02_contacts_map.svg`](02_contacts_map.svg) | Mappa dei componenti originali (disco, gancio, campanello, cornetta) | [docs/04](../../docs/04_installation.md) · Step 2 |
| 3 | [`03_dial_wires_identification.svg`](03_dial_wires_identification.svg) | Identificazione fili del disco col multimetro (NSI vs impulsi) | [docs/04](../../docs/04_installation.md) · Step 2 |
| 4 | [`04_general_wiring.svg`](04_general_wiring.svg) | Schema generale di cablaggio (tutti i blocchi) | [docs/03](../../docs/03_wiring.md) |
| 5 | [`05_internal_layout.svg`](05_internal_layout.svg) | Layout fisico interno dei moduli | [docs/04](../../docs/04_installation.md) · Step 5 |
| 6 | [`06_bell_driver_schematic.svg`](06_bell_driver_schematic.svg) | Driver del campanello (boost + H-bridge) | [docs/04](../../docs/04_installation.md) · Step 7 · [hardware](../../hardware/bell_driver.md) |
| 7 | [`07_audio_wiring.svg`](07_audio_wiring.svg) | Connessioni audio I2S (DAC/ADC, cornetta) | [docs/04](../../docs/04_installation.md) · Step 8 |
| 8 | [`08_oled_placement_options.svg`](08_oled_placement_options.svg) | Tre opzioni per il display OLED | [docs/04](../../docs/04_installation.md) · Step 9 |

## Diagrammi vs foto reali

Questi SVG sono **schematici idealizzati** (vista pulita, sempre validi per il
modello). Per la conversione su **foto reale della cassetta** — cosa
togliere/tenere/aggiungere con marker colorati — vedi
[`../retrofit/`](../retrofit/) e [`docs/07`](../../docs/07_retrofit_layout.md).
I due si completano: lo schematico spiega *cosa va dove*, la foto annotata
mostra *com'è davvero il tuo apparecchio*.

## Convenzioni

- **viewBox** `0 0 680 480–620` (larghezza fissa 680, altezza variabile): scalano senza distorsioni.
- **Palette semantica** coerente tra i diagrammi: viola = logica/Pi, ambra = alimentazione, corallo = interfacce, verde = campanello, blu = audio.
- Ogni file ha `<title>` e `<desc>` per l'accessibilità (screen reader).

## Modifica / verifica

Gli SVG si editano a mano (testo) o con Inkscape/Figma. Dopo una modifica,
controlla che il file resti XML ben formato:

```bash
python3 -c "import xml.dom.minidom as M; M.parse('05_internal_layout.svg')"
```
