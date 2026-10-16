#!/usr/bin/env python3
"""Generate ruler-only, printer-free visual reference instructions.

Grid paper: tell --grid-mm the measured spacing, e.g. 5 or 6.35.
The rectangle remains a manually selected calibration object, NOT an ArUco.
"""
import argparse
import json
import math


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--surface-width-mm', type=float, required=True)
    p.add_argument('--surface-height-mm', type=float, required=True)
    p.add_argument('--grid-mm', type=float, help='Measured square-grid spacing; omit for ruler-only')
    p.add_argument('--margin-mm', type=float, default=5.0)
    a = p.parse_args()
    if not all(math.isfinite(v) and v > 0 for v in (a.surface_width_mm, a.surface_height_mm, a.margin_mm)):
        p.error('Surface dimensions and margins must be positive finite mm')
    available_w = a.surface_width_mm - 2*a.margin_mm
    available_h = a.surface_height_mm - 2*a.margin_mm
    if a.grid_mm is not None:
        if not (math.isfinite(a.grid_mm) and 0.5 <= a.grid_mm <= 25):
            p.error('Grid spacing must be in [0.5, 25] mm')
        step = a.grid_mm
        w = math.floor(available_w / step) * step
        h = math.floor(available_h / step) * step
        step_text = f'Count {round(w / step)} grid cells horizontally and {round(h / step)} vertically; measured grid spacing = {step:g} mm.'
    else:
        w = math.floor(available_w / 5) * 5
        h = math.floor(available_h / 5) * 5
        step_text = 'Mark the dimensions with a ruler, and connect marks using straight horizontal and vertical strokes.'
    if w < 20 or h < 15:
        p.error('Surface too small for the suggested simple rectangle; use a larger surface or measured rigid object')
    pattern = {
        'pattern': 'asymmetric_four_corner_rectangle',
        'surface_mm': [a.surface_width_mm, a.surface_height_mm],
        'reference_rectangle_mm': [round(w,3), round(h,3)],
        'diagonal_check_mm': round(math.hypot(w,h), 2),
        'instructions': [
            f'Leave about {a.margin_mm:g} mm margin on all sides.',
            f'Draw a {w:g} mm wide by {h:g} mm tall outline. '+step_text,
            'Shade a small square INSIDE the top-left corner (do not hide the actual corner intersection).',
            'Add one short line INSIDE the top-right corner to tell orientation; keep other corners unshaded.',
            f'Check width and height and, if possible, both diagonals (~{math.hypot(w,h):.2f} mm).',
            'Photograph the entire rectangle on the same flat plane as the target.',
        ],
        'use': f"python scripts/measure.py PHOTO.jpg --reference rectangle --size-mm '{w:g},{h:g}' --quad 'TLx,TLy;TRx,TRy;BRx,BRy;BLx,BLy' --segment 'Ax,Ay;Bx,By'",
        'warning': 'Manual four-corner selection required; pattern is NOT automatically ArUco-detectable.'
    }
    print(json.dumps(pattern, indent=2))


if __name__ == '__main__':
    main()
