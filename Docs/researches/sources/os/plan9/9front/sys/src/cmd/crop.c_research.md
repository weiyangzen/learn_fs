# File Research: sources/os/plan9/9front/sys/src/cmd/crop.c

Plan 9 image crop utility using `draw`/`memdraw`. It reads an image, computes or applies a rectangle transform, fills a new image, draws the selected region, adjusts origin, and writes the result.

Important behavior:
- Options support background fill color, automatic blank-color crop, uniform inset, x/y insets, absolute rectangle, and translation.
- Auto crop converts non-`RGBA32` images to temporary RGBA for simple pixel comparison.
- The crop color and background color are encoded as `R<<24|G<<16|B<<8|0xFF`.
- Output origin is shifted by adjusting `new->r` and `new->zero`.
- Fatal errors use `sysfatal()`.
