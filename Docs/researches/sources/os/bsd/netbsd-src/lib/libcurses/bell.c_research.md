# File Research: sources/os/bsd/netbsd-src/lib/libcurses/bell.c

Read completely: 72 lines.

This file implements `beep()` and `flash()`. `beep` prefers the terminal `bell` capability and falls back to `flash_screen`; `flash` does the reverse. Both emit the selected terminfo string with `tputs(..., __cputchar)` and return `OK` even if neither capability exists.

Important interactions: uses terminfo globals `bell` and `flash_screen`, output helper `__cputchar`, and tracing area `__CTRACE_MISC`.

Reliability notes: no error is reported for terminals without either audible or visible alert capability.
