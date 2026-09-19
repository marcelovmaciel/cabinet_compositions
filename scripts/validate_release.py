#!/usr/bin/env python3
"""Validate evidence, scientific invariants, all calendars and exact publication reproduction."""
import argparse
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(PROJECT / 'src'))
from paths import BUILD, PUBLISHED, build_path
from validate import validate, validate_sources, compare_public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True, help='Completed reconstruction directory')
    args = parser.parse_args()
    root = build_path(args.build)
    print(json.dumps(validate_sources(), sort_keys=True), flush=True)
    print(json.dumps(validate(root / 'historical', require_primary_coverage=True), sort_keys=True), flush=True)
    print(json.dumps(compare_public(root / 'release', PUBLISHED), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
