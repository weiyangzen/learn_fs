# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/scrl.c

Scrollbar drawing and scrolling behavior for Abaco text frames and rendered pages.

Key responsibilities:
- Allocates temporary vertical/horizontal scrollbar images on resize.
- Computes scrollbar thumb rectangles from visible range and total size.
- Draws `Text` scrollbars and page horizontal/vertical scrollbars.
- Implements mouse-driven text scrolling.
- Implements page scrollbar dragging/page jumps for horizontal and vertical axes.
- Provides pixel delta page scrolling helper `pagescrollxy()` and sleep-with-mouse-interrupt helper.

Important behavior:
- Middle button drags to absolute position; button 1/3 page or pan backward/forward.
- Scrollbar position math scales down very large totals to avoid overflow.
- Page panning accelerates based on pointer movement away from the original point.

Dependencies:
- Uses timer helpers, global mouse controller, draw images, `Text` frame APIs, and page redraw.

Notable risks:
- `pagescrollxy()` can compute negative upper bounds when layout is smaller than viewport; callers rely on max/min clamping behavior.
