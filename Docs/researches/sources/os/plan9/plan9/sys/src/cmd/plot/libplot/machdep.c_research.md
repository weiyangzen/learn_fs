# File Research: sources/os/plan9/plan9/sys/src/cmd/plot/libplot/machdep.c

Plan 9 draw/event backend for libplot.

Key responsibilities:
- Initializes the draw display and mouse event handling.
- Sets clipping and square mapping bounds from the screen rectangle.
- Maintains the active drawing target, either `screen` or an offscreen image.
- Draws lines, text, clears rectangles, swaps buffers, and finishes output.
- Parses integer window arguments for older `-W` handling.
- Caches 1x1 color images for repeated draw operations.

Important behavior:
- `m_initialize()` runs draw setup once, then maps the plot square into the window inset by a few pixels.
- `m_dblbuf()` switches `offscreen` to an allocated inset image if possible.
- `m_swapbuf()` copies the offscreen image to the screen and flushes.
- `getcolor()` allocates RGB24 solid images and caches up to 32 entries.

Dependencies:
- Uses Plan 9 `draw`, `event`, `Image`, `screen`, `display`, `font`, `initdraw`, and `flushimage`.

Notable risks:
- `m_text()` measures with `stringsize(font, p)` even when rendering only `p..q`, so multi-line substring sizing can be wrong.
- Color cache never frees images and stops caching after 32 colors.
- Double buffer allocation failure silently falls back to direct screen drawing.
