# OPA167x transient model setup

The root project references `vendor/OPA167x_ngspice.LIB`. That file is generated
locally from the Texas Instruments **OPA167x TINA-TI Spice Model (SBOMAC5D)** and
is deliberately excluded from the repository.

Generate it with:

```sh
python3 tools/prepare_ti_model.py /path/to/sbomac5d.zip
```

Tested source model:

- OPA167x model version: Final 1.6
- SHA-256: `c130cbd159cc72e36dc9fb368c2491cee6329a5312ed3c85641c7b8492433391`
- Subcircuit pin order: `OPA167x IN+ IN- VCC VEE OUT`

The compatibility converter performs these transformations:

- removes the TINA/PSpice `PARAMS:` marker in favor of ngspice subcircuit
  parameter syntax;
- converts the involved `VSWITCH` model declarations to native ngspice `SW`
  declarations;
- converts the overload-sense boolean OR to ngspice syntax;
- replaces the TINA-only noiseless-resistor model declaration with a generic
  resistor model;
- replaces only the self-controlled TINA ESD switch cells with directional
  diode clamps to avoid ngspice operating-point singularities.

The final verified KiCad simulation wiring should netlist as:

```spice
XREF1 /VREF_RAW /VREF /VCC_A GND /VREF OPA167x
XAMP1 /IN_AC /FB /VCC_A GND /PREAMP_OUT OPA167x
```

Because the generated model is an adaptation, it is not an official TI model.
The ESD/protection behavior and absolute noise behavior are specifically not
vendor-accurate after conversion.
