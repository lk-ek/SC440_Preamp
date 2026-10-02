# Current AC simulation validation

Validation date: **2026-10-02**. Engine: **ngspice 42**. Model:
`AC_SIM/vendor/OPA1678_AC_ngspice.lib`, the included project-authored,
linear small-signal model. This is a simulation of nominal components, not a
measurement of the microphone.

## Connectivity and model checks

- Root and AC schematics have matching hardware values, pin connectivity and
  assembly/simulation flags. C4/C8 are included in the BOM.
- Every physical schematic pin was checked against the corresponding PCB pad
  net, including the connectors, U1 supplies and both op-amp channels.
- AC virtual symbols map correctly into the model order `INP INM VCC VEE OUT`:
  `Sim.Pins = 1=5 2=4 3=1 4=2 5=3`.
- A verification netlist derived independently from the AC schematic's symbol
  pins and wires was simulated and compared with the standalone reference.
  Over 0.1 Hz to 10 MHz, the reported output gain and phase agree within
  **0.000001 dB / 0.000001°** (output-file rounding).

## Six assembly variants

Sweeps: **0.1 Hz to 10 MHz, 1000 points/decade**. R9 = 1 kΩ and C9 = 330 pF
in every run. Ideal zero-impedance input source, AC amplitude 1 V. No external
output load. The film run replaces C2 with a 2.2 µF capacitor; R1/R2 are
represented by ideal wires.

| Gain option | Input option | R8 | Gain at 1 kHz | Gain at 20 kHz | Low-frequency −3 dB point |
|---|---|---:|---:|---:|---:|
| 6 dB | MLCC (1 µF) | 1 kΩ | 5.931 dB | 5.917 dB | 1.579 Hz |
| 6 dB | Film (2.2 µF) | 1 kΩ | 5.933 dB | 5.919 dB | 0.718 Hz |
| 8 dB | MLCC (1 µF) | 1.5 kΩ | 7.869 dB | 7.846 dB | 1.579 Hz |
| 8 dB | Film (2.2 µF) | 1.5 kΩ | 7.871 dB | 7.848 dB | 0.718 Hz |
| 10 dB | MLCC (1 µF) | 2.2 kΩ | 10.014 dB | 9.971 dB | 1.579 Hz |
| 10 dB | Film (2.2 µF) | 2.2 kΩ | 10.015 dB | 9.973 dB | 0.718 Hz |

Gain is measured from ANALOG_INPUT to ANALOG_OUTPUT. The low-frequency point
is relative to the same variant's gain at 1 kHz. Reported precision describes
the numerical result; component tolerances and real loading are not included.

R4/R6 introduce approximately `20·log10(100k/101k) = −0.086 dB` before the
amplifier. Coupling capacitance, C5, finite op-amp gain/bandwidth, C9 and R10/C7
also contribute. This explains why the amplifier's nominal +10.10 dB becomes
about +10.01 dB end to end. From 1 to 20 kHz the simulated change is about
−0.014 / −0.023 / −0.043 dB for the 6 / 8 / 10 dB options.

The input high-pass estimates `1/(2π·101k·C)` are 1.576 Hz for 1 µF and
0.716 Hz for 2.2 µF, consistent with the simulated lower cutoffs.

## Reproduce with standalone ngspice

From the project root:

```sh
cd AC_SIM
ngspice SC440_Preamp_AC_reference.cir
```

At the ngspice prompt, the following selects a denser sweep and prints the
default assembly's gain:

```text
ac dec 1000 0.1 10Meg
let output_gain = db(v(ANALOG_OUTPUT))
meas ac gain_1k find output_gain at=1k
meas ac gain_20k find output_gain at=20k
```

For another assembly, first use `alter R8=1k` or `alter R8=1.5k`. To represent
the film coupling electrically, use `alter C2=2.2u`. Then repeat the four
commands above. This command changes the simulation capacitance only; the
physical film assembly uses C1/R1/R2 and leaves C2 unpopulated.

## Scope

The standalone AC runs passed. KiCad 10.99 GUI/workbook loading and a new run
of the separately prepared TI macro-model were **not** performed. No new KiCad
ERC/DRC run is claimed. The linear AC model does not establish noise, clipping,
slew rate, PSRR, EMI immunity or stability with arbitrary real cable/ADC loads.
The input-source impedance and the digital board's coupling capacitor/input
impedance remain outside this simulation.
