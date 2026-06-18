# File Research: sources/os/plan9/9front/sys/src/cmd/acme/scrl.c

This file implements text scrollbar drawing and mouse-driven scrolling.

Key responsibilities:
- `scrpos()` maps visible text range (`p0..p1`) onto a scrollbar rectangle within total text length.
- `scrlresize()` allocates a temporary image buffer sized for scroll drawing.
- `textscrdraw()` redraws a body's scrollbar if its position changed.
- `scrsleep()` sleeps for a duration but cancels early on mouse input.
- `textscroll()` handles button-based scrolling:
  - button 2 jumps proportionally through the file.
  - button 1 scrolls backward.
  - button 3 scrolls forward.
  - debounces initial repeated scrolling.

Important dependencies:
- Uses `Text`, draw images, timer API, mouse channel, `textbacknl()`, `frcharofpt()`, and `textsetorigin()`.

Filesystem/storage relevance:
- Indirect: scroll position controls visible ranges over file-backed `Text` buffers.

Notes:
- Large totals are shifted down to avoid arithmetic overflow in scrollbar scaling.
- Scrollbar drawing is only for window bodies, not tags.
