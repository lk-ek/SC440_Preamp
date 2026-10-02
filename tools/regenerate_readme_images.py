#!/usr/bin/env python3
"""Regenerate SC440 README images from the saved KiCad project.

Place this file in tools/ and run from any working directory:
    python3 tools/regenerate_readme_images.py

Dependencies: a KiCad CLI able to read the project's file format (currently
KiCad 10.99 nightly), Inkscape >= 1.0, and Pillow:
    python3 -m pip install Pillow

Optional overrides:
    --project-dir PATH --kicad-cli PATH --inkscape PATH --models-dir PATH

Source files are never modified. Zone refill and removal of DNP 3D models
happen only in a temporary copy. PNGs are staged and validated before any
README image is replaced. The script uses saved files, not unsaved GUI edits.

SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

LAYERS = "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Fab,B.Fab,F.CrtYd,B.CrtYd,Edge.Cuts,Dwgs.User"
TARGETS = {
    "schematic": "sc440_preamp-schematic.png",
    "pcb": "sc440_preamp_pcb.png",
    "front": "sc440_preamp_front.png",
    "back": "sc440_preamp_back.png",
}


@dataclass
class Node:
    start: int
    end: int = 0
    items: list = field(default_factory=list)

    @property
    def tag(self):
        return self.items[0] if self.items else ""

    def children(self, tag):
        return [x for x in self.items if isinstance(x, Node) and x.tag == tag]


def parse_sexpr(text):
    """Parse with source spans, so only model nodes need to be rewritten."""
    stack, roots = [], []
    for m in re.finditer(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+', text):
        token = m.group()
        if token == "(":
            node = Node(m.start())
            (stack[-1].items if stack else roots).append(node)
            stack.append(node)
        elif token == ")":
            if not stack:
                raise RuntimeError("Unbalanced KiCad file")
            stack.pop().end = m.end()
        else:
            value = json.loads(token) if token.startswith('"') else token
            if not stack:
                raise RuntimeError("Unexpected top-level atom in KiCad file")
            stack[-1].items.append(value)
    if stack or len(roots) != 1:
        raise RuntimeError("Unbalanced or ambiguous KiCad file")
    return roots[0]


def executable(explicit, name, patterns):
    candidates = [explicit] if explicit else [shutil.which(name)]
    if not explicit:
        for pattern in patterns:
            candidates.extend(str(p) for p in sorted(Path('/').glob(pattern),
                              key=lambda p: ("nightly" in str(p).lower(), str(p)), reverse=True))
    for candidate in candidates:
        if candidate:
            path = Path(candidate).expanduser()
            if path.is_file() and os.access(path, os.X_OK):
                return str(path.resolve())
    raise RuntimeError(f"{name} not found; install it or specify --{name} PATH")


def run(command, cwd, env):
    print("  " + " ".join(str(x) for x in command), flush=True)
    result = subprocess.run([str(x) for x in command], cwd=cwd, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}):\n{result.stdout}")
    if result.stdout.strip():
        print(result.stdout.rstrip(), flush=True)
    return result.stdout


def help_text(cli, args, cwd, env):
    # Some KiCad builds return nonzero even for a valid --help request.
    p = subprocess.run([cli, *args, "--help"], cwd=cwd, env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.stdout


def project_root(explicit):
    if explicit:
        return Path(explicit).expanduser().resolve()
    for parent in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents,
                   Path.cwd()]:
        if (parent / "README.md").is_file() and list(parent.glob("*.kicad_pcb")):
            return parent
    raise RuntimeError("Project not found; place script in tools/ or use --project-dir PATH")


def image_targets(root):
    readme = (root / "README.md").read_text(encoding="utf-8")
    refs = re.findall(r'!\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+"[^"]*")?\)', readme)
    outputs = {}
    for kind, filename in TARGETS.items():
        matches = [ref for ref in refs if Path(ref).name == filename]
        if len(set(matches)) != 1:
            raise RuntimeError(f"README must reference exactly one path for {filename}")
        target = (root / matches[0]).resolve()
        if root not in target.parents:
            raise RuntimeError(f"README image path leaves project: {matches[0]}")
        outputs[kind] = target
    return outputs


def model_environment(cli, root, override):
    env = dict(os.environ)
    config_roots = [Path.home() / "Library/Preferences/kicad",
                    Path(env.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "kicad"]
    if env.get("APPDATA"):
        config_roots.append(Path(env["APPDATA"]) / "kicad")
    for base in config_roots:
        for config in sorted(base.glob("*/kicad_common.json"), reverse=True):
            try:
                data = json.loads(config.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    continue
                environment = data.get("environment")
                if not isinstance(environment, dict):
                    continue
                variables = environment.get("vars")
                if not isinstance(variables, dict):
                    continue
                for key, value in variables.items():
                    if isinstance(value, str):
                        env.setdefault(key, value)
            except (OSError, ValueError):
                continue
    env["KIPRJMOD"] = str(root)
    dirs = [Path(override).expanduser()] if override else []
    bundle = Path(cli).parent.parent
    dirs += [bundle / "SharedSupport/3dmodels", Path("/usr/share/kicad/3dmodels")]
    dirs += [Path(v).expanduser() for k, v in env.items()
             if re.fullmatch(r"KICAD\d+_3DMODEL_DIR", k)]
    available = next((p.resolve() for p in dirs if p.is_dir()), None)
    # Current nightly boards may still refer to KICAD10_3DMODEL_DIR.
    names = set(re.findall(r'\$\{(KICAD\d+_3DMODEL_DIR)\}',
                           next(root.glob("*.kicad_pcb")).read_text(encoding="utf-8")))
    for name in names:
        if available and (override or not Path(env.get(name, "/nonexistent")).is_dir()):
            env[name] = str(available)
    return env


def prepare_board(source, destination, env, allow_missing):
    text = source.read_text(encoding="utf-8")
    board = parse_sexpr(text)
    edits, missing = [], []
    for footprint in board.children("footprint"):
        attrs = footprint.children("attr")
        dnp = any("dnp" in a.items for a in attrs)
        ref = next((p.items[2] for p in footprint.children("property")
                    if p.items[1] == "Reference"), "?")
        for model in footprint.children("model"):
            if dnp:
                edits.append((model.start, model.end, ""))
                continue
            if any(n.items[1:] == ["yes"] for n in model.children("hide")):
                continue
            raw = model.items[1]
            resolved = re.sub(r'\$\{([^}]+)\}', lambda m: env.get(m[1], m[0]), raw)
            path = Path(resolved).expanduser()
            if not path.is_absolute():
                path = source.parent / path
            if not path.is_file():
                # KiCad standard libraries often ship WRL instead of STEP.
                alternative = path.with_suffix(".wrl")
                if alternative.is_file():
                    path = alternative
                else:
                    missing.append(f"{ref}: {raw}")
                    if allow_missing:
                        edits.append((model.start, model.end, ""))
                    continue
            node_text = text[model.start:model.end]
            quoted = re.search(r'"(?:\\.|[^"\\])*"', node_text)
            if not quoted:
                raise RuntimeError(f"Invalid model path on {ref}")
            node_text = (node_text[:quoted.start()] + json.dumps(str(path.resolve()), ensure_ascii=False)
                         + node_text[quoted.end():])
            edits.append((model.start, model.end, node_text))
    if missing:
        message = "Missing 3D models:\n  " + "\n  ".join(missing)
        if not allow_missing:
            raise RuntimeError(message + "\nInstall models or use --models-dir PATH. "
                               "--allow-missing-models deliberately permits incomplete images.")
        print("WARNING: " + message, file=sys.stderr)
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    destination.write_text(text, encoding="utf-8")


def finish_png(path, background, padding):
    from PIL import Image, ImageChops
    with Image.open(path) as original:
        rgba = original.convert("RGBA")
        # Alpha cropping handles rendered silhouettes. RGB difference cropping
        # also removes full schematic pages if an exporter supplied a background.
        alpha_bbox = rgba.getchannel("A").getbbox()
        if not alpha_bbox:
            raise RuntimeError(f"Empty image: {path}")
        had_transparency = rgba.getchannel("A").getextrema()[0] < 255
        rgba = rgba.crop(alpha_bbox)
        canvas = Image.new("RGBA", rgba.size, background)
        canvas.alpha_composite(rgba)
        rgb = canvas.convert("RGB")
        if not had_transparency:
            flat = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
            bbox = ImageChops.difference(rgb, flat).getbbox()
            if not bbox:
                raise RuntimeError(f"Blank image: {path}")
            rgb = rgb.crop(bbox)
        framed = Image.new("RGB", (rgb.width + 2*padding, rgb.height + 2*padding), background)
        framed.paste(rgb, (padding, padding))
        framed.save(path, optimize=True)
    with Image.open(path) as check:
        check.verify()


def rasterize(inkscape, svg, png, width, root, env, background, padding):
    run([inkscape, svg, "--export-type=png", "--export-area-drawing",
         f"--export-width={width}", f"--export-filename={png}"], root, env)
    finish_png(png, background, padding)


def publish(staged, targets):
    """Replace only after every export succeeds; roll back on write failures."""
    previous = {kind: p.read_bytes() if p.exists() else None for kind, p in targets.items()}
    replaced = []
    try:
        for kind, target in targets.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=".readme-image-", suffix=".png", dir=target.parent)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(staged[kind].read_bytes())
                os.replace(name, target)
            finally:
                Path(name).unlink(missing_ok=True)
            replaced.append(kind)
    except OSError:
        for kind in replaced:
            if previous[kind] is None:
                targets[kind].unlink(missing_ok=True)
            else:
                targets[kind].write_bytes(previous[kind])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-dir")
    parser.add_argument("--kicad-cli")
    parser.add_argument("--inkscape")
    parser.add_argument("--models-dir", help="KiCad 3dmodels directory")
    parser.add_argument("--allow-missing-models", action="store_true")
    parser.add_argument("--width", type=int, default=2400, help="SVG width / square 3D canvas (default: 2400)")
    parser.add_argument("--padding", type=int, default=40)
    parser.add_argument("--pcb-layers", default=LAYERS)
    args = parser.parse_args()
    if args.width < 200 or args.padding < 0:
        parser.error("width must be >= 200 and padding >= 0")
    try:
        import PIL  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Pillow missing: python3 -m pip install Pillow") from exc
    root = project_root(args.project_dir)
    boards = list(root.glob("*.kicad_pcb"))
    if len(boards) != 1:
        raise RuntimeError("Expected exactly one root-level .kicad_pcb")
    source_board = boards[0]
    source_sch = source_board.with_suffix(".kicad_sch")
    if not source_sch.is_file():
        raise RuntimeError(f"Missing schematic: {source_sch}")
    targets = image_targets(root)
    cli = executable(args.kicad_cli, "kicad-cli", [
        "Applications/KiCad*/KiCad*.app/Contents/MacOS/kicad-cli",
        "Applications/KiCad*.app/Contents/MacOS/kicad-cli",
        "Program Files/KiCad/*/bin/kicad-cli.exe",
    ])
    inkscape = executable(args.inkscape, "inkscape", ["Applications/Inkscape.app/Contents/MacOS/inkscape"])
    env = model_environment(cli, root, args.models_dir)
    run([cli, "version"], root, env)
    for command, required in [(["pcb", "render"], "--side"),
                              (["pcb", "drc"], "--refill-zones")]:
        if required not in help_text(cli, command, root, env):
            raise RuntimeError(f"KiCad lacks {' '.join(command)} {required}; use current KiCad/nightly")
    with tempfile.TemporaryDirectory(prefix="sc440-readme-") as temporary:
        work = Path(temporary)
        board = work / source_board.name
        prepare_board(source_board, board, env, args.allow_missing_models)
        for suffix in [".kicad_pro", ".kicad_dru"]:
            companion = source_board.with_suffix(suffix)
            if companion.is_file():
                shutil.copy2(companion, work / companion.name)
        print("Refilling copper zones in temporary board (DRC is not a release gate).", flush=True)
        run([cli, "pcb", "drc", "--refill-zones", "--save-board", "--format", "json",
             "--output", work / "drc.json", board], root, env)
        report = json.loads((work / "drc.json").read_text(encoding="utf-8"))
        print(f"DRC: {len(report.get('violations', []))} violations; "
              f"{len(report.get('unconnected_items', []))} unconnected items.", flush=True)
        staged = {kind: work / filename for kind, filename in TARGETS.items()}
        sch_dir = work / "schematic"
        sch_dir.mkdir()
        run([cli, "sch", "export", "svg", "--exclude-drawing-sheet", "--no-background-color",
             "--pages", "1", "--output", str(sch_dir) + os.sep, source_sch], root, env)
        svgs = list(sch_dir.glob("*.svg"))
        if len(svgs) != 1:
            raise RuntimeError("Expected one SVG for schematic root page")
        rasterize(inkscape, svgs[0], staged["schematic"], args.width, root, env, "white", args.padding)
        pcb_svg = work / "pcb.svg"
        run([cli, "pcb", "export", "svg", "--mode-single", "--exclude-drawing-sheet",
             "--page-size-mode", "0", "--layers", args.pcb_layers, "--output", pcb_svg, board], root, env)
        rasterize(inkscape, pcb_svg, staged["pcb"], args.width, root, env, "#071629", args.padding)
        for kind, side in [("front", "top"), ("back", "bottom")]:
            # front/back in the render CLI mean edge views, not component sides!
            run([cli, "pcb", "render", "--side", side, "--quality", "high",
                 "--background", "transparent", "--width", args.width, "--height", args.width,
                 "--output", staged[kind], board], root, env)
            finish_png(staged[kind], "#eceef2", args.padding)
        publish(staged, targets)
    print("Updated:")
    for path in targets.values():
        print("  " + str(path.relative_to(root)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
