# Simulation split

The project intentionally uses separate transient and AC simulation models.

## Root project: transient / large-signal

`SC440_Preamp.kicad_sch` uses the locally generated ngspice-compatible
adaptation of the TI TINA-TI OPA167x macro-model. Generate it first with
`tools/prepare_ti_model.py` as described in `README.md`.

Use the root project for transient behavior, slew, output swing, clipping, and
working-point checks. The verified subcircuit calls are:

```spice
XREF1 /VREF_RAW /VREF /VCC_A GND /VREF OPA167x
XAMP1 /IN_AC /FB /VCC_A GND /PREAMP_OUT OPA167x
```

The root workbook is transient-only. The adapted TINA behavioral model was not
reliable under ngspice AC linearization.

## `AC_SIM/`: frequency response

Open `AC_SIM/SC440_Preamp_AC.kicad_sch` for AC analysis. It uses the included,
project-authored `vendor/OPA1678_AC_ngspice.lib` with:

- Aol = 114 dB (501187 V/V)
- GBW = 16 MHz
- one dominant pole at about 31.9 Hz
- 10 Ω output resistance
- 10 TΩ differential input resistance

This is deliberately a small-signal model only. It does not model clipping,
slew rate, rail limits, noise, or protection behavior.

The AC workbook sweeps 0.1 Hz to 10 MHz. Useful expressions are:

```text
db(V(/PREAMP_OUT) / V(/IN_AC))
db(V(/PREAMP_OUT) / V(/ANALOG_INPUT))
```
