#!/usr/bin/env python3
"""Store a custom, measured rectangular reference in a portable JSON profile."""
import argparse
import json
import math
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--name', required=True)
    p.add_argument('--width-mm', required=True, type=float)
    p.add_argument('--height-mm', required=True, type=float)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--verified-against', default='user ruler measurement', help='How dimensions were established')
    args = p.parse_args()
    if not all(math.isfinite(v) and v > 0 for v in (args.width_mm, args.height_mm)):
        p.error('Width and height must be finite positive millimeter dimensions')
    if not args.name.strip():
        p.error('Name must not be empty')
    obj = {'schema_version': 1, 'name': args.name.strip(), 'shape': 'rectangle',
           'width_mm': args.width_mm, 'height_mm': args.height_mm,
           'verified_against': args.verified_against,
           'notes': 'Place the measured face against the same physical plane as target; manually select its four corners.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
