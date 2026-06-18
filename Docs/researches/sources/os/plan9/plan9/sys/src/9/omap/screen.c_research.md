# File Research: sources/os/plan9/plan9/sys/src/9/omap/screen.c

OMAP35 Display Subsystem framebuffer driver, kernel text console, blanking, and software cursor support.

Key responsibilities:
- Defines DSS/DISPC register layouts and constants for display configuration.
- Provides fixed display mode settings, with default `Res1280x1024`.
- Allocates an aligned 16-bit RGB framebuffer and exposes it as a `Memimage`.
- Programs DSS/DISPC timing, divisor, framebuffer base, FIFO, and graphics attributes.
- Implements screen power/blanking through LCD enable/disable.
- Implements `flushmemscreen()` by writing back framebuffer cache lines.
- Exports framebuffer details to devdraw via `attachscreen()`.
- Provides a software cursor implementation: allocation, load, hide/draw, move, clock update, and `setcursor`.
- Provides an on-screen text console with border/title bar, tab/backspace/newline handling, and scrolling.

Important behavior:
- `screeninit()` shows a blue test screen for three seconds on first initialization, then sets up the console window and cursor.
- Cursor drawing saves/restores the underlying screen region in `swback`.
- Console output avoids deadlock by using `canlock` when called from high interrupt priority.
- `blankscreen(0)` reinitializes display registers before enabling the LCD.
- `attachscreen` reports `softscreen` based on `landscape == 0`.

Dependencies:
- Depends on Plan 9 draw/memdraw, clock callbacks, OMAP clock/GPIO functions, cache writeback, and constants from `screen.h`/`mem.h`.

Notable risks:
- Resolution is effectively fixed to compile-time `Wid`/`Ht`, despite a settings table.
- Several color values are magic 16-bit bytes.
- `flushmemscreen` computes a byte span but passes `end - start`, not including the final pixel fully; this is usually cache-line rounded but imprecise.
