# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/scrl.c

Scrollbar rendering and scrolling logic for text widgets and pages.

Key responsibilities:
- Resizes scrollbar scratch resources.
- Converts content positions to scrollbar rectangles.
- Draws text and page scrollbars.
- Sleeps while preserving UI responsiveness.
- Implements mouse-button scrolling for text frames.
- Implements vertical and horizontal page scrolling, including panning.
- Scrolls pages to absolute x/y positions.

Dependencies:
- Uses global mouse state, `Text`, `Page`, `Frame`, and Plan 9 draw APIs.
- Coordinates with `textsetorigin`, `textshow`, `pageredraw`, and `pagescrldraw`.

Notable risks:
- Scroll behavior is button-driven and depends on Plan 9 mouse semantics.
- Page and text scrolling use different coordinate models.
