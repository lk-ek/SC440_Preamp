# Symbol, pad and device cross-check

This document describes the actual root schematic and PCB in the 2026-10-02
revision. Root and AC schematic references are now identical. The checks below
cover pin assignment, nominal pad geometry and assembly flags; they are not a
replacement for a KiCad DRC or an enclosure-fit measurement.

## U1 — Texas Instruments OPA1678IDR

Source: [TI OPA167x datasheet](https://www.ti.com/lit/ds/symlink/opa1678.pdf),
OPA1678 D-package pinout and SOIC drawing. `IDR` is the SOIC-8 version. VSSOP
(`IDGKR`) and SON versions do not fit this PCB.

The embedded `SC440_Preamp:OPA1678` symbol, numbered PCB pads and TI device
pins agree:

| Symbol pin | PCB pad | TI device function | PCB net |
|---:|---:|---|---|
| 1 | 1 | OUT A | PREAMP_OUT |
| 2 | 2 | −IN A | FB |
| 3 | 3 | +IN A | IN_AC |
| 4 | 4 | V− | GND |
| 5 | 5 | +IN B | VREF_RAW |
| 6 | 6 | −IN B | VREF |
| 7 | 7 | OUT B | VREF |
| 8 | 8 | V+ | VCC_A |

Footprint: `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm`. Adjacent pads are spaced
1.27 mm; the nominal body is 3.9 × 4.9 mm. The B amplifier is a follower,
with pads 6 and 7 on the same VREF net. U1's physical units are excluded from
simulation; XAMP1/XREF1 provide the simulated amplifiers and are not BOM parts.

### AC simulation alias pin order

The five-pin `OPA1678_SIM` symbol is a virtual simulation symbol, not U1's
physical package. Its pin map into the included AC model is:

| Virtual symbol pin / function | AC subcircuit position |
|---|---:|
| 1 / OUT | 5 |
| 2 / VEE | 4 |
| 3 / +IN | 1 |
| 4 / −IN | 2 |
| 5 / VCC | 3 |

Thus `Sim.Pins = 1=5 2=4 3=1 4=2 5=3` for the subcircuit order
`INP INM VCC VEE OUT`. Do not reuse the older AC schematic's alias mapping
with the current embedded symbol. The root TI model uses the corresponding
named map `1=OUT 2=VEE 3=IN+ 4=IN- 5=VCC`.

## Connectors — installed on B.Cu

| Symbol / pad number | J1 — digital-board side | J2 — analog-board side |
|---:|---|---|
| 1 | GND | GND |
| 2 | LED | LED |
| 3 | +5V | +5V |
| 4 | ANALOG_OUTPUT | ANALOG_INPUT |

The custom embedded connector symbols use these numbered pins. Both connector
PCB footprints have a square pad 1. Mounting on the back changes the visible
left-to-right order; continuity and pad numbers define wiring.

- **J1:** `Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical`, top-entry,
  2.50 mm pitch, four pads spanning 7.50 mm. Matches the four-circuit top-entry
  **JST B4B-XH-A** in the [JST XH drawing](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf).
  This is not the older side-entry S4B footprint. Mates with XHP-4 and suitable
  XH crimp contacts.
- **J2:** `Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical`, straight
  1×4 generic header, 2.54 mm pitch; pads span 7.62 mm. There is no exact
  manufacturer part assigned. Choose square-pin length and insulator height
  to suit the original microphone PCB and mating connector.
- **Two `REF**` footprints:** back-side 1×2 sockets with 2.54 mm pitch, absent
  from the schematic. All four pads have no electrical net. They are mechanical
  supports/placeholders, not additional signal connectors. Manufacturer and
  required height are not specified.

The original microphone-board footprints are outside this project. In
particular, the new header on the digital board must be checked against its
actual holes; a 2.54 mm original header is not exactly JST XH's 2.50 mm pitch.

## Passive geometry and polarity

| Parts | Actual footprint | Check / assembly |
|---|---|---|
| R1–R10 | `Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder` | 0805 SMD parts; the old Yageo MFR through-hole datasheet links in the schematic are stale metadata, not ordering guidance |
| C2, C4, C5, C7, C8, C9 | `Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder` | Non-polarized 0805; C4 is front-side, C8 back-side; both included in BOM |
| C3 | `Capacitor_THT:CP_Radial_D5.0mm_P2.00mm` | Pad 1 = VREF_RAW (+); pad 2 = GND (−); schematic-linked Aishi ERS1CM470D11OT listing gives Ø5 × 11 mm, 2 mm pitch |
| C6 | Same radial footprint | Pad 1 = VCC_A (+); pad 2 = GND (−); schematic-linked Chengx KM106M016D11RR0VH2FP0 listing gives Ø5 × 11 mm, 2 mm pitch; install lying down for the intended enclosure |
| C1 | Project-local `Faratronic_C241J225_P5.00mm` | Non-polarized; pad 1 via R1 to ANALOG_INPUT; pad 2 via R2 to the input side of R4 |

All components in the gain tables and BOM match these nominal package sizes.
The [Yageo RT 2.2 kΩ part specification](https://www.yageogroup.com/component-documentation/download/specsheet/RT0805BRD072K2L)
confirms the recommended resistor's 0805 dimensions and technology. The
[Murata catalog](https://www.mouser.com/datasheet/2/281/murata_mure-s-a0000034126-1-1740300.pdf)
confirms the selected 330 pF / 1 nF C0G parts' 2.0 × 1.25 mm body size.
Exact electrolytic part specifications are linked in the README; dimensional
checks here use their published supplier listings, not a separately retrieved
manufacturer approval drawing.

### C1 custom footprint

Source: [Faratronic C24 / CL23B manufacturer series drawing](https://datasheet.lcsc.com/datasheet/pdf/98aa4bc32419fc2b11d6d8f0ae52cac7.pdf?productCode=C545501),
pattern II, `C241J225-2S…` (2.2 µF / 63 V): nominal **W = 7.2 mm,
H = 11.0 mm, T = 6.0 mm**, **P = 5.0 mm**, lead diameter **0.6 mm**.
This corresponds to the specified `C241J225J2SC000` family/packaging choice.

The local footprint has pad centers at (0,0) and (5,0), **0.9 mm drills**, and
2 mm pads. Its 13.5 × 8.5 mm fabrication outline and 14.4 × 9.4 mm courtyard
are deliberately larger than the nominal upright body plan. They are not the
actual body dimensions. The 11 mm body height still needs enclosure clearance;
a lying-down arrangement needs a different mechanical envelope. No C1 3D model
is attached, so a rendered film assembly cannot confirm body clearance.

## Assembly variants

- Default MLCC: C2 populated; C1/R1/R2 DNP.
- Film: C2 DNP; C1/R1/R2 populated, with R1/R2 = 0 Ω.
- R9 = 1 kΩ for all gain options; only R8 changes to 1 / 1.5 / 2.2 kΩ.
- C9 = 330 pF is populated in the current design, not a missing optional 100 pF
  part. C4/C8 are included in both the schematic and PCB BOM flags.

No connector geometry, routed track, pad or board outline was changed during
this documentation/simulation update. Only C4/C8 BOM flags were corrected in
the physical design files.
