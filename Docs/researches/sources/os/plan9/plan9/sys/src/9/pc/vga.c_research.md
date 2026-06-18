# File Research: sources/os/plan9/plan9/sys/src/9/pc/vga.c

Generic Plan 9 VGA console drawing support. It creates replicated black/white `Memimage` objects in `vgaimageinit()`, sets a text window with `vgascreenwin()`, and installs `vgascreenputs()` as `screenputs`.

Behavior:
- `vgascreenputc()` handles newline, carriage return, tab, backspace, NUL, and UTF-8 character rendering via `memimagestring()`.
- `vgascroll()` scrolls the console window by eight font rows and clears the exposed area.
- `vgascreenputs()` avoids deadlock from interrupt context by using `canlock()`, opportunistically takes `drawlock`, accumulates a flush rectangle, and calls `flushmemscreen()`.
- `vgablank()` attempts VGA-register DPMS blanking through sequencer and CRTC registers, but comments note it can disturb mode state.
- `addvgaseg()` exports physical VGA/MMIO regions as named physical segments.
- `cornerstring()` draws a string at the screen corner if VGA console output is active.

State is file-static except exported `vgascreenlock` and `drawdebug`. The code depends heavily on Plan 9 draw/memdraw and `screen.h` VGA helpers.
