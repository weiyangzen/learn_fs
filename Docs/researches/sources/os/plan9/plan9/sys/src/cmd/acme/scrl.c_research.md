# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/scrl.c

This file implements body scrollbar drawing and mouse scrolling.

Key behavior:
- `scrpos()` computes scrollbar thumb rectangle from visible range and total file length.
- `scrlresize()` allocates a temporary image for scrollbar drawing.
- `textscrdraw()` redraws a body scrollbar only when the position changes.
- `scrsleep()` waits for a timer or mouse activity during scroll repeat.
- `textscroll()` handles button 1, 2, and 3 scrolling: page/back-line style, absolute proportional jump, and forward scrolling.

Important details:
- Large totals are shifted down to avoid integer overflow.
- Scroll thumb is at least two pixels tall.
- Button 2 maps mouse y position proportionally to file character offset.
- Mouse is warped to the scroll bar center during active scrolling.

Filesystem relevance:
- Indirect UI support for navigating file-backed text.
