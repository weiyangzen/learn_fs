# File Research: sources/os/plan9/plan9/sys/src/9/bcm/screen.c

BCM framebuffer screen and kernel console implementation.

Key behavior:
- Initializes framebuffer through `fbinit()` and VideoCore mailbox, with optional `vgasize` config override.
- Supports 16, 24, and 32 bpp channel formats.
- Initializes `Memimage` state, default font, console drawing window, and `screenputs`.
- Implements a simple graphical console with title bar, scrolling, tabs, carriage return, backspace, and UTF-8 rune handling.
- Provides draw-device hooks: `attachscreen()`, `flushmemscreen()`, `getcolor()`, `setcolor()`, `blankscreen()`, and `hwdraw()`.
- Implements software cursor allocation, load, move, hide/draw, periodic clock update, and avoidance around draw operations.
- `swcursorinit()` registers cursor clock callback and allocates cursor backing/mask images.

`flushmemscreen()` is empty because the framebuffer memory is directly visible/coherent enough for this port’s assumptions.
