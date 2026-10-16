#!/usr/bin/env python3
"""Make a pixel-coordinate grid on a photo without resizing or changing the original."""
import argparse
from pathlib import Path
import cv2

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('image', type=Path)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--step', type=int, default=100)
a = p.parse_args()
if a.step <= 0:
    p.error('--step must be positive')
im = cv2.imread(str(a.image))
if im is None:
    p.error(f'Cannot read image: {a.image}')
h, w = im.shape[:2]
for x in range(0, w, a.step):
    cv2.line(im, (x, 0), (x, h-1), (255, 180, 0), 1, cv2.LINE_AA)
    cv2.putText(im, str(x), (x + 3, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(im, str(x), (x + 3, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)
for y in range(0, h, a.step):
    cv2.line(im, (0, y), (w-1, y), (255, 180, 0), 1, cv2.LINE_AA)
    cv2.putText(im, str(y), (5, max(40,y+23)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 3, cv2.LINE_AA)
    cv2.putText(im, str(y), (5, max(40,y+23)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)
if not cv2.imwrite(str(a.output), im):
    p.error(f'Cannot save image: {a.output}')
print(f'{a.output} : {w} x {h} original pixels')
