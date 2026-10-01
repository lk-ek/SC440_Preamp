# Third-party notices

## Texas Instruments OPA167x TINA-TI model

The root KiCad simulation is designed to use Texas Instruments' OPA167x
TINA-TI macro-model (download package `SBOMAC5D`). The TI model itself, and the
ngspice-adapted file generated from it, are **not included in this repository**.

Users obtain the model directly from Texas Instruments and locally run
`tools/prepare_ti_model.py`. The resulting `vendor/OPA167x_ngspice.LIB` remains
a derivative/adapted copy of the TI model and is Git-ignored.

The conversion script is project-authored and contains only the compatibility
transformation logic. It does not contain a copy of the TI macro-model.

Texas Instruments and OPA167x/OPA1678 are identifiers/trademarks of their
respective owner. This project is not affiliated with or endorsed by Texas
Instruments.

## Simplified AC model

`AC_SIM/vendor/OPA1678_AC_ngspice.lib` is a project-authored simplified
small-signal model based on publicly documented typical device parameters. It
is not a Texas Instruments macro-model and must not be used as a substitute for
vendor-accurate large-signal, noise, clipping, or protection behavior.
