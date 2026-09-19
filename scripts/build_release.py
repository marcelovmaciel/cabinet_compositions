#!/usr/bin/env python3
"""Reconstruct and export offline into a fresh, atomically completed build directory."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(PROJECT / 'src'))
from paths import BUILD, INPUTS, build_path, safe_path
from build import build
from validate import validate, validate_sources
from export import export


def reconstruct(output):
    output = build_path(output)
    if output.exists():
        raise FileExistsError(f'Build destination must be fresh: {output}')
    safe_path(BUILD).mkdir(exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.reconstruct-', dir=output.parent))
    try:
        validate_sources()
        build(INPUTS, stage / 'historical')
        validate(stage / 'historical', require_primary_coverage=True)
        export(stage / 'historical', stage / 'release')
        # No destination is visible until all construction/validation succeeds.
        if output.exists():
            raise FileExistsError(f'Build destination appeared during reconstruction: {output}')
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(build_path(stage))
    print(f'Completed offline reconstruction: {output}')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='New directory below this project’s build/; never an existing release')
    args = parser.parse_args()
    reconstruct(args.output)
