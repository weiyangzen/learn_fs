# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libdraw/arith.c

Provides foundational Plan 9 geometry and color helpers used throughout drawterm drawing code.

Key functions:
- Constructors: `Pt`, `Rect`, `Rpt`.
- Point/rectangle arithmetic: `addpt`, `subpt`, `insetrect`, `divpt`, `mulpt`, `rectsubpt`, `rectaddpt`.
- Predicates: `eqpt`, `eqrect`, `rectXrect`, `rectinrect`, `ptinrect`.
- Normalization/combination: `canonrect`, `combinerect`.
- `setalpha`: premultiplies RGB channels by an alpha byte and writes the new RGBA value.
- `Rfmt`, `Pfmt`: `Fmt` printers for rectangles and points.

Global data:
- `drawld2chan[]` maps old ldepth values to channel descriptors.
- `log2[]`, `ZP`, and `ZR` provide compatibility utilities and zero geometry constants.
