# Simulation paths and current circuit

The root and AC projects now share the current hardware schematic topology and
reference designators. Both default to **10.10 dB / C2 MLCC**. Both standalone
reference netlists have also been updated. This update does not synchronize
future edits automatically: make subsequent hardware changes in both projects
or derive a fresh AC schematic from the root again.

## Root: TI-based transient model

`SC440_Preamp.kicad_sch` / `SC440_Preamp.wbk` use the locally generated
`vendor/OPA167x_ngspice.LIB`. Generate it with `tools/prepare_ti_model.py` as
shown in the root README. `SC440_Preamp_fallback.cir` is a current-topology
standalone fallback using the same model.

Model order: `OPA167x IN+ IN- VCC VEE OUT`. The intended instance connections
are, allowing for exporter-selected net spelling:

```spice
XREF1 VREF_RAW VREF VCC_A 0 VREF OPA167x
XAMP1 IN_AC FB VCC_A 0 PREAMP_OUT OPA167x
```

The virtual symbol mapping is `1=OUT 2=VEE 3=IN+ 4=IN- 5=VCC`. Its physical
U1 counterpart is excluded from simulation. Use the TI-based path for
operating-point/transient investigations within the adapted model's limits.
The model converter changes syntax and protection/noise cells; it is not a
vendor-accurate noise or ESD model, nor a compatibility guarantee for every
ngspice build. No TI-model transient run was performed for this update because
the vendor model is not included.

## AC_SIM: included small-signal model

`AC_SIM/SC440_Preamp_AC.kicad_sch` / `.wbk` use the included
`vendor/OPA1678_AC_ngspice.lib`. The two virtual op-amp symbols use
**`Sim.Pins = 1=5 2=4 3=1 4=2 5=3`**, matching their current symbol pins to the
subcircuit order `INP INM VCC VEE OUT`.

```spice
XREF1 VREF_RAW VREF VCC_A 0 VREF OPA1678_AC
XAMP1 IN_AC FB VCC_A 0 PREAMP_OUT OPA1678_AC
```

Model assumptions:

- Typical open-loop gain 114 dB (501187 V/V), GBW 16 MHz.
- One dominant pole near 31.9 Hz; 10 Ω output resistance.
- 10 TΩ differential input resistance and tiny supply-reference paths.
- No rail limits, clipping, slew, noise or PSRR model.

The AC source amplitude is 1 V. The workbook sweeps 0.1 Hz to 10 MHz and plots
`V(/ANALOG_OUTPUT)` magnitude/phase and `V(/PREAMP_OUT)` magnitude. Additional
normalized expressions, if desired, are:

```text
db(V(/ANALOG_OUTPUT) / V(/ANALOG_INPUT))
db(V(/PREAMP_OUT) / V(/IN_AC))
```

The model includes the current 22 Ω supply feed, buffered divider, R4/C5 input
filter, R8/R9 feedback, C9, and R10/C7 output filter. Neither the original source
impedance nor cable/ADC loading is modeled. The standalone reference netlist
uses ground `0`; KiCad schematics use power:GND and the exporter's ground
handling. This linear model does not constrain output voltage to the supply
rails, so it cannot assess clipping or DC headroom.

## Validation

Hardware values/DNP flags, U1 physical pins, and virtual model pin order were
cross-checked between both schematics, the PCB and the standalone netlists.
See [FOOTPRINT_CHECK.md](FOOTPRINT_CHECK.md).

Standalone AC runs and the calculated 6/8/10 dB, MLCC/film assembly comparisons
are documented in [SIMULATION_VALIDATION.md](SIMULATION_VALIDATION.md). KiCad
10.99 GUI/workbook loading and the TI macro-model path were not executed in the
editing environment. Successful standalone AC analysis does not validate
physical EMI performance, noise or ADC loading.
