# Footprint and pin-map check

## U1 — TI OPA1678IDR
TI D-package SOIC-8 top-view pinout:
1 OUT A; 2 -IN A; 3 +IN A; 4 V-; 5 +IN B; 6 -IN B; 7 OUT B; 8 V+.

Schematic symbol uses exactly those pin numbers. Footprint: `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`, appropriate for TI D (SOIC-8).

Connections:
- U1A pin 3 = IN_AC, pin 2 = FB, pin 1 = PREAMP_OUT.
- U1B pin 5 = VREF_RAW, pin 6 = VREF, pin 7 = VREF (unity follower).
- pin 8 = VCC_A; pin 4 = GND.

## J1 — analog board
`Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical`
Pin 1 GND; 2 LED; 3 +5V; 4 OUT.

## J2 — cable to digital board
JST S4B-XH-A-1, 4 positions, 2.50 mm pitch, right-angle/side-entry.
Footprint: `Connector_JST:JST_XH_S4B-XH-A-1_1x04_P2.50mm_Horizontal`.
Pin 1 GND; 2 LED; 3 +5V; 4 IN.

The cable is straight-through for pins 1-3; pin 4 is intentionally interrupted by the preamp.

## Passive footprints
- Yageo MFR-25-style resistors: DIN0207 L6.3 mm, P10.16 mm horizontal.
- OPA supply/reference 100 nF: 0805.
- 10 uF / 47 uF electrolytics: radial D5.0 mm P2.00 mm (verify against exact ordered manufacturer parts before PCB release).
- C1 Faratronic C241J225: project-local 5.00 mm pitch footprint; body courtyard intentionally conservative.
