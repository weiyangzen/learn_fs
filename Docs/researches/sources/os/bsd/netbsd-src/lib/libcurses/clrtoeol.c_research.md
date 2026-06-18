# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clrtoeol.c

Read completely: 127 lines.

This file implements `clrtoeol` and `wclrtoeol`, clearing from the current cursor position to the end of the current line.

`wclrtoeol` validates the window, handles `__ISPASTEOL` by moving to the next line when possible, then iterates from `curx` to line end. It clears `CA_BACKGROUND` before checking `__NEED_ERASE`, resets changed cells to the background character and attributes, copies background nonspacing data in wide builds, touches the whole line range from the original x coordinate to the right edge, and calls `__sync`.

Important interactions: same erase infrastructure as `clrtobot.c` and `erase.c`.

Reliability notes: the comment notes ncurses compatibility behavior that makes the cleared rest-of-line foreground rather than background. This intentionally affects `CA_BACKGROUND` semantics.
