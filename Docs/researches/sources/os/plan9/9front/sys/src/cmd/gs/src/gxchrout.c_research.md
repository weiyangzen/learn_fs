# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.c

Implements the shared outline-character flatness heuristic.

Key behavior:
- `gs_char_flatness` inspects the absolute CTM scale/skew terms and chooses the smallest non-zero effective scale component.
- Corrects the scale by the font's default scale, using 0.001 as the Type 1 baseline.
- Caps the result at the imager state's current flatness so character rendering is never coarser than requested.
- Forces flatness to zero for tiny characters below the 0.2 threshold, yielding more accurate curves.

Dependencies:
- Uses math helpers, fixed-arithmetic helpers, `gxistate.h`, and the declaration in `gxchrout.h`.

Research notes:
- This is a quality heuristic: small glyphs get extra curve accuracy, while larger glyphs remain bounded by graphics-state flatness.
