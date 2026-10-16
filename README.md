# scAIl Photo Scale

**Printer-free, ordinary-object photo measurement for AI agents.** An open-source Agent Skill from **The Kirkwood Consortium**.

Take a photograph with a reference object next to the thing you want to measure. Ask an agent to estimate the length in millimeters. The agent selects reference and segment endpoints; the OpenCV-backed script performs the planar calculation and annotates the original image. This is not a ruler or caliper replacement.

## What to use as a reference

- **No printer:** known-size ID-1 bank card (85.60 × 53.98 mm), measured wallet, rectangle drawn on plain paper using a ruler, or verified grid paper.
- **Available printer:** optional ArUco marker for automatic recognition (generate with OpenCV; confirm physical size with a ruler). The printable PDF is included in the separately packaged beta ZIP, not yet in this GitHub repository.
- **Only a coin:** US quarter (24.26 mm diameter); near-overhead approximation **without perspective correction**.
- **Larger items:** A4 or US Letter paper, check the sheet is untrimmed and not distorted.

## Quick start for a code-capable agent

1. Install/copy the `scail-photo-scale/` directory into the agent's skills folder (see `references/platforms.md`).
2. In a permitted Python environment, install dependencies: `python -m pip install -r requirements.txt`.
3. Send a photo and ask: **“Use scAIl to measure the width of this object.”**
4. For a ruler-only marker: `python scripts/pattern_guide.py --surface-width-mm 85 --surface-height-mm 54`.
5. To save measured personal reference dimensions: `python scripts/create_profile.py --name 'My wallet' --width-mm 88 --height-mm 56 --output wallet.json` (replace sample dimensions with actual measurements).

Detailed CLI examples in [`SKILL.md`](SKILL.md). `scripts/measure.py --help` describes arguments; the agent will need original-image pixel coordinates for user-drawn references, and for the measurement endpoints. **This version does not automatically find arbitrary objects or their endpoints.**

## Accuracy and limitations

- For rectangles or ArUco markers, OpenCV applies a homography to an assumed common flat plane. It cannot recover depth from one photograph.
- Hand-drawn reference patterns are **manually corner-selected**; asymmetric shading makes orientation easier for humans/agents, not an independent fiducial detector.
- Quarter mode uses simple diameter-scale ratio, not perspective correction.
- An initial synthetic test only checks arithmetic/detection, **not real-world accuracy**. Compare with a ruler before depending on a result. Do not use for safety-critical dimensions, fabrication tolerances, or regulated measurements.
- No uploads, telemetry, account, or external service are built into the scripts. The AI platform used to process your photos may have its own privacy handling.

## Compatibility

The skill uses the portable Agent Skills `SKILL.md` layout. Claude, Codex, ChatGPT, Gemini CLI, Cursor, and GitHub Copilot can read skill instructions in supported experiences; **actual script execution depends on platform tools, permissions, and installed Python packages**. See [`references/platforms.md`](references/platforms.md). No platform was end-to-end tested for this release.

## License and attribution

MIT licensed. Copyright © 2026 The Kirkwood Consortium contributors. Independent project; not endorsed by ArUco/OpenCV, PLAUD, or any AI platform. Contributions and issue reports welcome after repository publication.
