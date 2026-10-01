# AC-only simulation

This directory is a self-contained small-signal AC version of the SC440 preamp
simulation. It does not require the Texas Instruments vendor macro-model.

Use `SC440_Preamp_AC.kicad_sch` for frequency-response work. The included
`vendor/OPA1678_AC_ngspice.lib` is a project-authored simplified model and is
GPL-3.0-only licensed; it is not an official TI SPICE model.
