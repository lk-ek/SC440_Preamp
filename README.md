# SC440 OPA1678 microphone preamp

Small 5 V, single-supply OPA1678 daughterboard for the t.bone SC 440 USB
microphone. The PCB is designed to fit on the back of the original analog PCB.
To install it, remove the original pinheaders. Solder a new set of pinheaders
on the opposite side of the original position to connect the daughter board.

Remove the original pinsockets from the digital board, replace them with JST XH
B4B sockets. Connect the daughter board with a short 4-pin cable with JST XH
connectors, be mindful of the correct pinout.

The preamp AC-couples the microphone/JFET board, rebiases the audio
around a buffered half-supply reference, and drives the original USB/ADC board.

Current nominal gain:

`1 + 22 kΩ / 10 kΩ = 3.2 V/V ≈ +10.1 dB`

## Hardware overview

- OPA1678 dual op-amp on 5 V.
- U1B buffers `VREF_RAW` (10 kΩ / 10 kΩ divider) into the low-impedance virtual
  ground `VREF`.
- C6 = 1 µF is the default input coupling capacitor; R3 = 100 kΩ biases `IN_AC`
  to `VREF`.
- U1A is a non-inverting amplifier with R5 = 22 kΩ and R4 = 10 kΩ.
- R7 = 100 Ω isolates the preamp output from the cable / following input.
- C1 = 2.2 µF film is an optional/DNP alternative to C6.

See `FOOTPRINT_CHECK.md` for the pin/footprint cross-check used for this revision.

![image](img/sc440_preamp-schematic.png)
![PCB layout — front](img/sc440_preamp_pcb_front.png)
![PCB layout — back](img/sc440_preamp_pcb_back.png)
![image](img/sc440_preamp_front.png)
![image](img/sc440_preamp_back.png)

## Simulation

The project deliberately uses two simulation paths.

### Root project — transient / large-signal

`SC440_Preamp.kicad_sch` uses the TI OPA167x TINA-TI macro-model after a local
ngspice compatibility conversion. The vendor model is **not included**.

Download **OPA167x TINA-TI Spice Model (SBOMAC5D)** from the Texas Instruments
OPA1678 product page, then run:

```sh
python3 tools/prepare_ti_model.py ~/Downloads/sbomac5d.zip
```

This writes the Git-ignored file:

```text
vendor/OPA167x_ngspice.LIB
```

The tested source is TI OPA167x model version Final 1.6, SHA-256
`c130cbd159cc72e36dc9fb368c2491cee6329a5312ed3c85641c7b8492433391`.

Use the root project for transient behavior, slew, output swing, and clipping.
The compatibility conversion changes syntax plus the ESD/protection-cell
implementation needed for ngspice convergence, so the generated model is not an
official TI model. Do not treat `.noise` results or ESD/protection behavior as
vendor-accurate.

### `AC_SIM/` — frequency response

`AC_SIM/SC440_Preamp_AC.kicad_sch` is self-contained and uses the included
project-authored `OPA1678_AC_ngspice.lib`. It is a simple small-signal model for
stable ngspice AC analysis, based on 114 dB typical open-loop gain and 16 MHz
GBW. It is **not** the TI macro-model and is not intended for clipping, noise,
slew, or protection behavior.

Expected nominal results are approximately +10.1 dB mid-band gain, an input
high-pass around 1.6 Hz, and closed-loop high-frequency roll-off in the MHz
range.

More detail is in `SIMULATION_MODEL.md` and `SIMULATION_SPLIT.md`.

## Third-party model / redistribution

No Texas Instruments SPICE macro-model is shipped in this repository. See
`THIRD_PARTY_NOTICES.md` and `vendor/README.md`.

## Licensing

Except where noted otherwise, this project is licensed under the GNU General
Public License version 3 only (`GPL-3.0-only`). See `LICENSE.md` and
`LICENSES/GPL-3.0-only.txt`.

Texas Instruments SPICE/model files are not included and are not relicensed by
this project; see `THIRD_PARTY_NOTICES.md`.
