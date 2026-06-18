# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/scroll.c

Purpose: Implements samterm scrollbar drawing and mouse-driven scrolling.

Key routines:
- `scrtemps`: lazily allocates a temporary narrow image for drawing scrollbars when the layer is fully visible.
- `scrpos`: maps document positions `p0..p1` within `tot` into a scrollbar rectangle, ensuring at least a 2-pixel thumb.
- `scrdraw`: redraws the scrollbar only when its rectangle changes.
- `scrsleep`: sleeps in millisecond increments while polling mouse state, ending early on button changes.
- `scroll`: handles button 1/4 upward, button 5 downward, and button 2 absolute scroll positioning.

Integration: Uses `Flayer`, frame metrics, global `mousectl`, `mousep`, `display`, and helpers `screensize`, `scrtotal`, `forcenter`, `flushdisplay`, and `panic`.

Risks and behavior:
- Uses integer scaling with a shift fallback for documents larger than 1 MiB of runes.
- Wheel buttons return after one movement; mouse buttons auto-repeat with delay.
- Panics if mouse reads fail or if asked to draw without a backing frame image.
