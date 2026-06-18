# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/draw.c

Provides libpanel color/image initialization and common drawing primitives.

Key behavior:
- Allocates reusable solid images for white/light/dark/scroll/black/blue/highlight and a caret tick image.
- Draws boxes/outlines for panel states, computes box sizes/interiors, and draws icons/text/bitmaps with clipping.
- Draws check/radio controls, slider/scrollbar fills, highlights, ticks, clears/fills, and self-copy operations.
- Implements recursive panel drawing with invisibility/ignore checks.

Important dependencies: Plan 9 draw library, global `display`, `screen`, `font`.

Notable risks:
- `pl_drawinit()` calls `sysfatal` if any image allocation fails.
- Drawing style constants from `pldefs.h` must stay aligned with widget expectations.
