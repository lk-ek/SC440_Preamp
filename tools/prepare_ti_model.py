#!/usr/bin/env python3
"""Create the local ngspice-compatible OPA167x model used by this project.

This script does not download or contain the Texas Instruments macro-model.
Supply the TINA-TI SBOMAC5D ZIP (or the extracted OPA167x.LIB) yourself.

SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

TESTED_SHA256 = "c130cbd159cc72e36dc9fb368c2491cee6329a5312ed3c85641c7b8492433391"
EXPECTED_SUBCKT = ".SUBCKT OPA167x IN+ IN- VCC VEE OUT"


def read_source(path: Path) -> bytes:
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as zf:
            candidates = [n for n in zf.namelist() if Path(n).name.lower() == "opa167x.lib"]
            if len(candidates) != 1:
                raise RuntimeError(
                    f"Expected exactly one OPA167x.LIB in {path}; found {len(candidates)}"
                )
            return zf.read(candidates[0])
    return path.read_bytes()


def replace_subckt(text: str, name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"(?ims)^\.SUBCKT\s+{re.escape(name)}\b.*?^\.ENDS(?:\s+{re.escape(name)})?\s*$"
    )
    new_text, count = pattern.subn(replacement.rstrip(), text, count=1)
    if count != 1:
        raise RuntimeError(f"Could not uniquely replace subcircuit {name}")
    return new_text


def convert(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if EXPECTED_SUBCKT.lower() not in text.lower():
        raise RuntimeError("Input does not look like the expected OPA167x TINA-TI model")

    # PSpice/TINA subcircuit parameter marker -> ngspice-native parameter syntax.
    text = re.sub(r"\bPARAMS:\s*", "", text, flags=re.IGNORECASE)

    # TINA/PSpice VSWITCH -> ngspice SW with equivalent midpoint and hysteresis.
    substitutions = {
        r"(?im)^\.MODEL\s+_S1\s+VSWITCH\s+ROFF=1E12\s+RON=10M\s+VOFF=0\.0V\s+VON=10MV\s*$":
            ".MODEL _S1 SW(RON=10M ROFF=1E12 VT=5MV VH=5MV)",
        r"(?im)^\.MODEL\s+_S2\s+VSWITCH\s+ROFF=1E12\s+RON=10M\s+VOFF=0\.0V\s+VON=10MV\s*$":
            ".MODEL _S2 SW(RON=10M ROFF=1E12 VT=5MV VH=5MV)",
        r"(?im)^\.MODEL\s+OL_SW\s+VSWITCH\(RON=1E-3\s+ROFF=1E12\s+VON=900E-3\s+VOFF=800E-3\)\s*$":
            ".MODEL OL_SW SW(RON=1E-3 ROFF=1E12 VT=850E-3 VH=50E-3)",
        r"(?im)^\.MODEL\s+R_NOISELESS\s+RES\s*\(T_ABS=-273\.15\)\s*$":
            ".MODEL R_NOISELESS R",
    }
    for pattern, replacement in substitutions.items():
        text, count = re.subn(pattern, replacement, text, count=1)
        if count != 1:
            raise RuntimeError(f"Expected model construct not found: {pattern}")

    # PSpice boolean OR used in the overload-sense expression.
    text, count = re.subn(
        r"(V\(OLN,COM\)>10E-3)\s*\|\s*(V\(OLP,COM\)>10E-3)",
        r"\1 || \2",
        text,
        count=1,
    )
    if count != 1:
        raise RuntimeError("Expected overload-sense OR expression not found")

    # The TINA ESD cells use a voltage switch controlled by the same two nodes it
    # connects. ngspice can become singular at the operating point. Directional
    # diode clamps keep the intended off-state behavior around the normal 0..5 V
    # operating region while allowing the rest of the vendor macro-model to run.
    diode_model = ".MODEL D_ESD_OPA167x D(IS=1e-8 N=1 RS=50 CJO=0.1p)"
    text = replace_subckt(
        text,
        "ESD_BB_OPA167x",
        f"""{diode_model}
.SUBCKT ESD_BB_OPA167x ESDN ESDP
D1 ESDN ESDP D_ESD_OPA167x
D2 ESDP ESDN D_ESD_OPA167x
.ENDS ESD_BB_OPA167x""",
    )
    text = replace_subckt(
        text,
        "ESD_IN_OPA167x",
        """.SUBCKT ESD_IN_OPA167x ESDN ESDP VCC VEE
D1 ESDN VCC D_ESD_OPA167x
D2 ESDP VCC D_ESD_OPA167x
D3 VEE ESDN D_ESD_OPA167x
D4 VEE ESDP D_ESD_OPA167x
.ENDS ESD_IN_OPA167x""",
    )
    text = replace_subckt(
        text,
        "ESD_OUT_OPA167x",
        """.SUBCKT ESD_OUT_OPA167x OUT VCC VEE
D1 OUT VCC D_ESD_OPA167x
D2 VEE OUT D_ESD_OPA167x
.ENDS ESD_OUT_OPA167x""",
    )

    header = """* ngspice compatibility adaptation generated locally by SC440_Preamp/tools/prepare_ti_model.py
* Source macro-model copyright and terms remain with Texas Instruments and its licensors.
* This generated file is intentionally not part of the repository.
*
"""
    return header + text.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="SBOMAC5D ZIP or extracted OPA167x.LIB")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("vendor/OPA167x_ngspice.LIB"),
        help="output path (default: vendor/OPA167x_ngspice.LIB)",
    )
    parser.add_argument(
        "--allow-untested", action="store_true",
        help="allow a source file whose SHA-256 differs from the tested model",
    )
    args = parser.parse_args()

    raw = read_source(args.source)
    digest = hashlib.sha256(raw).hexdigest()
    if digest != TESTED_SHA256 and not args.allow_untested:
        raise RuntimeError(
            "Source model differs from the tested TI OPA167x.LIB.\n"
            f"Expected SHA-256: {TESTED_SHA256}\n"
            f"Actual SHA-256:   {digest}\n"
            "Use --allow-untested only after reviewing the model/version and generated diff."
        )

    try:
        source_text = raw.decode("utf-8")
    except UnicodeDecodeError:
        source_text = raw.decode("latin-1")

    converted = convert(source_text)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(converted, encoding="utf-8", newline="\n")
    print(f"Wrote {args.output}")
    print(f"Source SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
