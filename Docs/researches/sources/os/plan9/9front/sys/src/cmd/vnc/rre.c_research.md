# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/rre.c

## Role

`rre.c` implements VNC server-side framebuffer rectangle encoders: raw, RRE, CoRRE, and hextile.

## Encoding Paths

- `sendraw()` sends uncompressed pixel data from the backing `Memimage`.
- `sendrre()` and `sendcorre()` split large rectangles into bounded tiles, choose a background color, encode uniform-color subrectangles, and fall back to raw if compressed form would exceed the budget.
- `sendhextile()` splits into 16x16 tiles, selects background/foreground reuse flags, emits raw tiles when compact encoding is not beneficial, and handles colored-subrect hextile mode.
- `count*()` functions estimate how many RFB rectangles each encoding path will emit.

## Core Algorithms

- `findback()` samples pixels to estimate the most common background color.
- `hexcolors()` determines whether a hextile tile has background only, background plus one foreground, or multiple foreground colors.
- `encrre()` greedily finds tall, maximally wide uniform-color rectangles, marks covered pixels, and writes encoder-specific rectangle records.
- `eqpix8()`, `eqpix16()`, and `eqpix32()` compare pixels for supported depths.

## Notable Limitations And Risk Areas

- Only 8, 16, and 32 bpp get compressed encoders; other depths fall back to raw.
- Encoding is heuristic, not optimal.
- Raw fallback is used on allocation failure or when encoded rectangle budgets are exceeded.
- The code assumes image stride can be expressed cleanly in whole pixels for the selected depth.
