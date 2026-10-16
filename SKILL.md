---
name: scail-photo-scale
description: Measure approximate physical lengths in uploaded photographs using everyday reference objects (bank cards, coins, paper), a user-calibrated wallet or tool, a ruler-drawn no-printer rectangle, or a printed ArUco marker. Use for DIY, workshop, repairs, physical inventories, construction-site photographs, and dimension estimates. Guide custom calibration and produce annotated images with honest plane/depth limits; do not treat measurements as fabrication tolerances.
---

# scAIl Photo Scale

Turn one picture plus a physical scale reference into **an approximate planar measurement**. Ask at most one necessary question at a time; prefer a quick first measurement.

## Choose a reference

1. **Already have a flat object?** Use a measured rectangle: ID-1 card 85.60 × 53.98 mm, US Letter 215.9 × 279.4 mm, A4 210 × 297 mm, or a custom flat item. The visible dimensions must actually correspond to the object's measured face, not a sleeve/case. Pick reference corners TL/TR/BR/BL in that order relative to width/height; rounded corners require extrapolation and more uncertainty.
2. **No printer?** Use a ruler to draw a rectangular outline and an asymmetric corner cue on graph paper, tape, an index card or other rigid surface. `python scripts/pattern_guide.py --surface-width-mm 85 --surface-height-mm 54` gives a tailored step-by-step design; add `--grid-mm 5` for verified 5 mm graph paper. **A hand-drawn pattern is NOT an automatically detectable ArUco marker**; select its four corners using image coordinates.
3. **Coin only?** A US quarter is 24.26 mm diameter. The circle mode is scale-only, **does not correct perspective**, and needs a near-overhead image and the coin in the same plane as the target. For larger measurements choose a rectangle instead.
4. **Printer available?** Use an OpenCV-generated ArUco `DICT_4X4_50` marker ID 23 with a **30 mm physical black square**, and verify its printed size with a ruler. Automatic marker detection is supported. The optional printable PDF is in the beta ZIP archive but is not yet hosted in this repository.
5. **Repeat custom item?** Ask for its actual dimensions in millimeters; create `python scripts/create_profile.py --name 'my wallet' --width-mm 88 --height-mm 56 --output wallet.json` using the user's measurements (example values are NOT defaults). Profiles are local portable JSON; never include private identifiers. A profile stores scale, **not the item's automatic image detection**.

## Measurement procedure

1. Check the **full-resolution original** photo, reference, and exact feature the user wants measured. If endpoints aren't identifiable, ask which two. Place reference *touching the same plane* as those points, not floating in front; use a main camera, sufficient distance/light, and avoid wide-angle edge distortion.
2. Identify endpoint image coordinates and reference quad or circle-diameter endpoints from the original image. Use `scripts/overlay_grid.py` to assist coordinate labeling. Do not run pixel measurements on a scaled chat preview.
3. Execute `scripts/measure.py` with the reference options below and `--annotated output.png`. Inspect overlay and JSON; correct clearly wrong corner order or endpoints before reporting. **Never claim script execution unless actually run in a code-capable environment.** Check dependencies from `requirements.txt`; ask before network installs where approval is required.
4. Report the feature, estimated mm, reference and method (planar-corrected or simple scale), annotated output when available, and the dominant error source. First use: compare a known ruler span in the same photo to determine empirical error. Do not invent an accuracy percentage or use trailing decimals as confidence.
5. If target isn't planar, endpoints and reference differ in depth, reference is occluded, or the perspective is extreme, label the result unreliable and ask for one better photo or direct measurement. For structural, safety-critical, cutting, fit, or fabrication work, require a ruler/calipers/tape measure.

## Commands

```bash
python scripts/measure.py PHOTO.jpg --reference marker --marker-mm 30 --segment 'x1,y1;x2,y2' --annotated measured.png
python scripts/measure.py PHOTO.jpg --reference rectangle --preset id1-card --quad 'TLx,TLy;TRx,TRy;BRx,BRy;BLx,BLy' --segment 'x1,y1;x2,y2' --annotated measured.png
python scripts/measure.py PHOTO.jpg --reference rectangle --size-mm '50,30' --quad 'TLx,TLy;TRx,TRy;BRx,BRy;BLx,BLy' --segment 'x1,y1;x2,y2'
python scripts/measure.py PHOTO.jpg --reference rectangle --profile wallet.json --quad 'TLx,TLy;TRx,TRy;BRx,BRy;BLx,BLy' --segment 'x1,y1;x2,y2'
python scripts/measure.py PHOTO.jpg --reference circle --preset us-quarter --diameter-px 'leftx,y;rightx,y' --segment 'x1,y1;x2,y2'
```

`python -m pip install -r requirements.txt` only in an environment where installing dependencies is permitted. If only visual chat tools are available, give clearly **uncalibrated rough estimates** or explain a code-capable session is required. Never pretend the code has run. No internet API or account is needed.

## Deliverable

Give **one main estimated size in mm**, an annotated image if supported, and a brief note on reference, same-plane assumption and validation state. Keep all originals unchanged. Consult `references/field-guide.md` for printerless layout instructions and `references/platforms.md` for installing and execution caveats.
