# File Research: sources/os/plan9/9front/sys/src/9/imx8/screen.c

Role: Software framebuffer console and draw attachment support for i.MX8 display.

Key responsibilities:
- Maintains `gscreen` as a `Memimage`, raw framebuffer pointer `fbraw`, default font, console colors, screen lock, cursor position, and text window.
- Provides mouse control commands for accelerated/linear mouse mode.
- Uses software cursor helpers for cursor on/off/load and avoids cursor overlap in `hwdraw()`.
- `screeninit()` initializes memdraw, allocates `gscreen`, allocates uncached framebuffer memory, draws the console window, replays kernel message buffer, installs `screenputs`, and initializes software cursor.
- `flushmemscreen()` clips a rectangle and copies changed pixels from `gscreen` to raw framebuffer.
- `attachscreen()` returns the `Memdata` backing `gscreen` for `devdraw` with `softscreen=1`.
- `myscreenputs()` decodes UTF-8 runes under `screenlock` and delegates character rendering.
- `screenwin()` draws a simple Plan 9 console UI and initializes text bounds.
- `screenputc()` handles newline, carriage return, tab, backspace, and glyph rendering with scrolling.

Dependencies:
- Plan 9 draw/memdraw/cursor libraries, `ucalloc`, `kmesg`, software cursor code, and common devdraw hooks.

Notes:
- `hwdraw()` does no acceleration; it only manages software cursor avoidance and returns 0.
- `getcolor()` and `setcolor()` are stubs.
