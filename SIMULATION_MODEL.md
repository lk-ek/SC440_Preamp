# TI OPA167x transient model setup

The root schematic and `SC440_Preamp_fallback.cir` reference the locally
generated `vendor/OPA167x_ngspice.LIB`. The Texas Instruments **OPA167x TINA-TI
Spice Model (SBOMAC5D)** is not included in this repository.

Download it from the [TI OPA1678 product page](https://www.ti.com/product/OPA1678),
then run from the project root:

```sh
python3 tools/prepare_ti_model.py /path/to/sbomac5d.zip
```

The converter expects this source:

- OPA167x model version Final 1.6.
- SHA-256 `c130cbd159cc72e36dc9fb368c2491cee6329a5312ed3c85641c7b8492433391`.
- Subcircuit order `OPA167x IN+ IN- VCC VEE OUT`.

`--allow-untested` bypasses the source-hash check; it does not make a different
model compatible. Inspect the generated changes before using that option.

## What the included converter actually does

`tools/prepare_ti_model.py` currently:

- removes TINA/PSpice `PARAMS:` markers;
- translates the expected `VSWITCH` models into ngspice `SW` models;
- translates the overload-sense boolean OR syntax;
- replaces the TINA noiseless-resistor declaration with a generic resistor model;
- replaces the named self-controlled ESD switch subcircuits with diode clamps.

These edits are syntax/convergence adaptations, not a guarantee that every
nested behavioral subcircuit works with every ngspice compatibility mode.
In particular, a “Too many parameters for subcircuit” error must be resolved
before treating simulation output as valid; removing `PARAMS:` alone is not
proof of parameter compatibility. The script itself was not changed during
this documentation/AC synchronization update.

## Current root wiring

The five-pin virtual symbol has pin 1 OUT, 2 VEE, 3 +IN, 4 −IN, 5 VCC.
Its TI-model mapping is `1=OUT 2=VEE 3=IN+ 4=IN- 5=VCC`. Intended model calls:

```spice
XREF1 VREF_RAW VREF VCC_A 0 VREF OPA167x
XAMP1 IN_AC FB VCC_A 0 PREAMP_OUT OPA167x
```

Root hardware values are R8 = 2.2 kΩ and R9 = 1 kΩ, C2 = 1 µF, with R4/C5,
C9 = 330 pF, and R10/C7 present. The fallback netlist now has the same topology
and component references. No external source/cable/ADC impedance is modeled.

This adapted model is not an official TI model. Its noise and ESD/protection
behavior are not vendor-accurate. No new TI-model transient run is claimed.
For a self-contained current-topology AC simulation, use `AC_SIM/`; see
[SIMULATION_SPLIT.md](SIMULATION_SPLIT.md).
