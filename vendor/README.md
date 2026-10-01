# Vendor model directory

The Texas Instruments OPA167x TINA-TI macro-model is intentionally **not**
redistributed with this project.

To enable the root-project transient simulation:

1. Download **OPA167x TINA-TI Spice Model (SBOMAC5D)** from the OPA1678 product
   page on Texas Instruments' website.
2. Run from the repository root:

   ```sh
   python3 tools/prepare_ti_model.py ~/Downloads/sbomac5d.zip
   ```

3. The script writes `vendor/OPA167x_ngspice.LIB`, which is ignored by Git.

The converter was tested against TI model `OPA167x.LIB`, model version Final 1.6,
with SHA-256:

`c130cbd159cc72e36dc9fb368c2491cee6329a5312ed3c85641c7b8492433391`

The generated model is an ngspice compatibility adaptation of TI's model and is
not an official TI model. Do not commit or redistribute it unless you have
separately confirmed that you have the necessary rights to do so.
