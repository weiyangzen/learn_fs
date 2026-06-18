# File Research: sources/os/plan9/9front/sys/src/9/bcm/screen.c

BCM framebuffer console and draw attachment support.

Key responsibilities:
- Requests/configures framebuffer geometry through VideoCore mailbox helpers.
- Initializes Plan 9 draw screen state and software cursor support.
- Provides `attachscreen()` for `devdraw`.
- Flushes dirty framebuffer rectangles with cache maintenance.
- Implements console text rendering, scrolling, cursor positioning, and screen blanking.
- Provides color get/set stubs for true-color framebuffer usage.

Important behavior:
- Tracks window text area and cursor position manually for early console output.
- Uses `fbinit()`, `fbblank()`, and framebuffer physical/virtual mapping data from mailbox calls.
- Hardware acceleration is not implemented; `hwdraw()` returns failure.

Dependencies:
- `memdraw`, `devdraw`, framebuffer mailbox support, cache maintenance, and soft cursor routines.
