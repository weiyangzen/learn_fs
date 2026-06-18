# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/scroll.c

Implements scrollbar rendering and mouse-driven scrolling for `samterm` flayers.

Key functions:
- `scrtemps` allocates temporary scrollbar backing images sized from `/dev/screen`.
- `scrpos` maps visible text range to scrollbar thumb rectangle.
- `scrmark` and `scrunmark` highlight/unhighlight scroll drag regions.
- `scrdraw` draws the scrollbar track and thumb, using offscreen temporaries when the layer is fully visible.
- `scroll` handles button-specific scroll behavior, drag tracking, and origin requests.

Behavior notes:
- Large totals are scaled down before thumb computation to avoid overflow.
- Thumb height is clamped to at least 2 pixels.
- Scroll interaction delegates actual text origin changes through protocol requests rather than directly loading arbitrary text.
