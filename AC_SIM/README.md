# Current-hardware AC simulation

`SC440_Preamp_AC.kicad_sch` now contains the same hardware topology, component
references and default assembly as the root schematic: **R8 = 2.2 kΩ,
R9 = 1 kΩ, C2 = 1 µF**, input filter R4/C5, output filter R10/C7, and
**C9 = 330 pF** across R8. C1/R1/R2 remain DNP/excluded from simulation.
C4 and C8 are included in the BOM.

The schematic was copied from the current root project; the two virtual
op-amp symbols were changed to the included project-authored
`vendor/OPA1678_AC_ngspice.lib`. No TI macro-model is required. The AC model is
GPL-3.0-only, not a TI model, and does not model clipping, slew, noise,
rail limits or power-supply rejection.

Open this directory's `.kicad_pro`, then the schematic's simulator, and load
`SC440_Preamp_AC.wbk` if necessary. The workbook sweeps **0.1 Hz to 10 MHz** and
shows ANALOG_OUTPUT gain/phase plus PREAMP_OUT gain. The source has **AC = 1 V**,
so output-voltage magnitude in dB directly gives end-to-end gain in dB. Keep that
normalization when comparing traces; the 1 V small-signal AC excitation is not
an intended real microphone amplitude.

The standalone `SC440_Preamp_AC_reference.cir` has the same current topology:

```sh
cd AC_SIM
ngspice SC440_Preamp_AC_reference.cir
```

At the ngspice prompt, run `run`, then for example
`plot vdb(ANALOG_OUTPUT)` or `plot vp(ANALOG_OUTPUT)`. ADC/cable loading and
original-board source impedance are not modeled. The signal generator is ideal.

## Other gain and coupling assemblies

R9 remains 1 kΩ. Change **R8** in the AC schematic or reference netlist:

| R8 | Nominal amplifier gain |
|---:|---:|
| 1 kΩ | +6.02 dB |
| 1.5 kΩ | +7.96 dB |
| 2.2 kΩ | +10.10 dB |

These are amplifier gains; end-to-end gain includes the input/output networks.
Standalone ngspice results for all six assemblies are in
[../SIMULATION_VALIDATION.md](../SIMULATION_VALIDATION.md).

C9 stays 330 pF. To simulate the film assembly in the schematic, exclude C2
from simulation and mark it DNP; enable C1/R1/R2 by clearing both DNP and
“Exclude from simulation”, with C1 = 2.2 µF and R1/R2 = 0 Ω. In the reference
netlist, replace the C2 line with `C1 ANALOG_INPUT COUPLED 2.2u`; this represents
both links as ideal wires. Change both representations if keeping them in sync.

See [../SIMULATION_SPLIT.md](../SIMULATION_SPLIT.md) for model pin maps and
validation scope, and [../README.md](../README.md) for the hardware BOM.
