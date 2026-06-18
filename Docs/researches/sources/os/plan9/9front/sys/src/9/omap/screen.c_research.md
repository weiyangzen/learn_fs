# File Research: sources/os/plan9/9front/sys/src/9/omap/screen.c

OMAP DSS/DISPC framebuffer and text-console implementation.

Key behavior:
- Defines DSS and DISPC register layouts and graphics-plane configuration constants.
- Maintains screen settings, framebuffer `Memimage`, console colors, default font, cursor position, virtual screen buffer, and display window.
- `lcdinit` and `configdispc` program display timings, pixel clock divisors, framebuffer base, graphics attributes, FIFO thresholds, and LCD output.
- `screeninit` allocates framebuffer memory, initializes the display, sets up draw/screen globals, and installs console output.
- `flushmemscreen` writes back framebuffer cache lines for changed rectangles.
- `attachscreen`, `getcolor`, `setcolor`, and `blankscreen` implement generic screen hooks.
- `screenputc`, `scroll`, and `screenwin` implement the kernel text console on the framebuffer.
- `mousectl`, cursor functions, and power hooks are present but minimal/stub-like.

Research notes:
- The file is tightly coupled to OMAP DSS registers and the `OScreen` settings structure.
- Landscape orientation is tracked but much of the console logic assumes fixed framebuffer geometry.
