#!/usr/bin/env python3
"""Measure a segment on a photographed plane against a known reference.

Examples:
  python scripts/measure.py image.jpg --reference marker --marker-mm 30 --segment '10,20;110,20' --annotated result.png
  python scripts/measure.py image.jpg --reference rectangle --preset id1-card --quad 'x,y;x,y;x,y;x,y' --segment 'x,y;x,y'
  python scripts/measure.py image.jpg --reference rectangle --profile profile.json --quad 'x,y;x,y;x,y;x,y' --segment 'x,y;x,y'
  python scripts/measure.py image.jpg --reference circle --preset us-quarter --diameter-px 'x,y;x,y' --segment 'x,y;x,y'

Pixel coordinates refer to the ORIGINAL input image, not a resized preview.
"""
import argparse
import json
import math
import sys
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError as exc:
    sys.exit(f"Missing Python dependency ({exc}). Install requirements.txt in an authorized environment.")

RECT_PRESETS = {
    'id1-card': (85.60, 53.98),
    'a4-paper': (210.0, 297.0),
    'letter-paper': (215.9, 279.4),
}
CIRCLE_PRESETS = {'us-quarter': 24.26}
MARKER_DICT = cv2.aruco.DICT_4X4_50 if hasattr(cv2, 'aruco') else None


def points(text, expected):
    result = []
    for pair in text.split(';'):
        a = [float(z.strip()) for z in pair.split(',')]
        if len(a) != 2 or not all(math.isfinite(v) for v in a):
            raise ValueError('Each coordinate must contain two finite numbers: x,y')
        result.append(a)
    if len(result) != expected:
        raise ValueError(f'Expected {expected} points, got {len(result)}')
    return np.asarray(result, dtype=np.float32)


def rectangle_size(args):
    if args.profile:
        p = json.loads(args.profile.read_text(encoding='utf-8'))
        if p.get('shape') != 'rectangle' or not all(k in p for k in ('width_mm', 'height_mm')):
            raise ValueError('Profile must be a rectangle with width_mm and height_mm')
        w, h = float(p['width_mm']), float(p['height_mm'])
        name = p.get('name', 'custom reference')
    elif args.preset:
        if args.preset not in RECT_PRESETS:
            raise ValueError('Rectangle presets: '+', '.join(RECT_PRESETS))
        w, h = RECT_PRESETS[args.preset]
        name = args.preset
    elif args.size_mm:
        w, h = [float(x) for x in args.size_mm.split(',')]
        name = 'measured rectangle'
    else:
        raise ValueError('Supply --size-mm WIDTH,HEIGHT, --preset, or --profile for rectangle')
    if not (math.isfinite(w) and math.isfinite(h) and w > 0 and h > 0):
        raise ValueError('Reference size must be positive finite mm')
    return w, h, name


def marker_corners(img, marker_id):
    if MARKER_DICT is None:
        raise RuntimeError('OpenCV ArUco module unavailable; use opencv-contrib-python')
    dictionary = cv2.aruco.getPredefinedDictionary(MARKER_DICT)
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    corners, ids, _ = detector.detectMarkers(img)
    if ids is None:
        raise RuntimeError('No ArUco detected; ensure correct physical marker, clarity and white border')
    matches = [i for i, ident in enumerate(ids.flatten()) if int(ident) == marker_id]
    if not matches:
        raise RuntimeError(f'Marker {marker_id} not detected; seen {ids.flatten().tolist()}')
    return corners[matches[0]].reshape(4, 2).astype(np.float32)


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('image', type=Path)
    a.add_argument('--reference', choices=['marker', 'rectangle', 'circle'], default='marker')
    a.add_argument('--segment', required=True, help='Desired image endpoints x1,y1;x2,y2')
    a.add_argument('--quad', help='Reference rectangle corners TL;TR;BR;BL (clockwise on photographed face)')
    a.add_argument('--size-mm', help='Measured rectangle width,height (mm)')
    a.add_argument('--profile', type=Path, help='Saved custom rectangle profile JSON')
    a.add_argument('--preset', choices=list(RECT_PRESETS)+list(CIRCLE_PRESETS))
    a.add_argument('--diameter-px', help='Circle diameter endpoints x1,y1;x2,y2')
    a.add_argument('--diameter-mm', type=float, help='Known circular reference diameter in mm')
    a.add_argument('--marker-mm', type=float, default=30.0)
    a.add_argument('--marker-id', type=int, default=23)
    a.add_argument('--annotated', type=Path)
    a.add_argument('--json-out', type=Path)
    args = a.parse_args()
    if not args.image.exists():
        a.error(f'Image not found: {args.image}')
    img = cv2.imread(str(args.image))
    if img is None:
        raise RuntimeError('Cannot decode image')
    endpoints = points(args.segment, 2)
    label = 'measurement'
    warnings = ['Endpoints manually chosen or agent-selected; verify overlay before relying on result.',
                'Valid only when target endpoints and reference lie on the same physical plane.']
    ref_poly = None
    if args.reference in ('marker', 'rectangle'):
        if args.reference == 'marker':
            if not (math.isfinite(args.marker_mm) and args.marker_mm > 0):
                raise ValueError('--marker-mm must be positive')
            ref_poly = marker_corners(img, args.marker_id)
            w = h = args.marker_mm
            label = f'ArUco 4x4_50 ID {args.marker_id}'
        else:
            if not args.quad:
                raise ValueError('--quad required for a rectangle or a hand-drawn reference')
            ref_poly = points(args.quad, 4)
            w, h, label = rectangle_size(args)
        if abs(cv2.contourArea(ref_poly)) < 32:
            raise ValueError('Reference corners too small or degenerate')
        physical = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        H = cv2.getPerspectiveTransform(ref_poly, physical)
        if not np.isfinite(H).all():
            raise ValueError('Invalid planar calibration')
        measured = cv2.perspectiveTransform(endpoints.reshape(-1, 1, 2), H).reshape(2, 2)
        distance = float(np.linalg.norm(measured[1] - measured[0]))
        if not math.isfinite(distance):
            raise ValueError('Invalid transformed measurement')
        result = {'mode': 'planar_homography', 'reference': label, 'reference_mm': [w, h],
                  'reference_corners_px': ref_poly.tolist(), 'endpoints_in_reference_frame_mm': measured.tolist(),
                  'distance_mm': round(distance, 3), 'endpoints_px': endpoints.tolist()}
    else:
        if not args.diameter_px:
            raise ValueError('Circular reference requires --diameter-px')
        if args.preset:
            if args.preset not in CIRCLE_PRESETS:
                raise ValueError('Circle presets: '+', '.join(CIRCLE_PRESETS))
            diam_mm = CIRCLE_PRESETS[args.preset]
            label = args.preset
        elif args.diameter_mm is not None:
            diam_mm = args.diameter_mm
            label = 'measured circle'
        else:
            raise ValueError('Use --preset us-quarter or --diameter-mm')
        if not (math.isfinite(diam_mm) and diam_mm > 0):
            raise ValueError('Diameter must be positive')
        ref_d = points(args.diameter_px, 2)
        px_d = float(np.linalg.norm(ref_d[1] - ref_d[0]))
        if px_d < 3:
            raise ValueError('Circle too small for scale')
        distance = float(np.linalg.norm(endpoints[1] - endpoints[0])) * diam_mm / px_d
        warnings.append('Circle method has NO perspective correction; use only with camera nearly perpendicular to plane.')
        result = {'mode': 'simple_scale_no_perspective_correction', 'reference': label,
                  'reference_diameter_mm': diam_mm, 'diameter_endpoints_px': ref_d.tolist(),
                  'endpoints_px': endpoints.tolist(), 'distance_mm': round(distance, 3)}
        ref_poly = ref_d
    result['input_image'] = str(args.image)
    result['warnings'] = warnings
    if args.annotated:
        pic = img.copy()
        if args.reference == 'circle':
            cv2.line(pic, tuple(ref_poly[0].astype(int)), tuple(ref_poly[1].astype(int)), (30, 160, 255), 3)
        else:
            cv2.polylines(pic, [np.round(ref_poly).astype(np.int32)], True, (30, 160, 255), 3)
        p0, p1 = np.round(endpoints).astype(int)
        cv2.line(pic, tuple(p0), tuple(p1), (30, 220, 30), 3)
        for p in (p0, p1):
            cv2.circle(pic, tuple(p), 6, (0, 50, 250), -1)
        text = f'{distance:.1f} mm (estimate)'
        xy = (max(5, min(p0[0], p1[0])), max(30, min(p0[1], p1[1])-14))
        cv2.putText(pic, text, xy, cv2.FONT_HERSHEY_SIMPLEX, .65, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(pic, text, xy, cv2.FONT_HERSHEY_SIMPLEX, .65, (255, 255, 255), 2, cv2.LINE_AA)
        args.annotated.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(args.annotated), pic):
            raise RuntimeError('Could not write annotated image')
        result['annotated'] = str(args.annotated)
    payload = json.dumps(result, indent=2)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(payload+'\n', encoding='utf-8')
    print(payload)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        sys.exit(f'ERROR: {exc}')
