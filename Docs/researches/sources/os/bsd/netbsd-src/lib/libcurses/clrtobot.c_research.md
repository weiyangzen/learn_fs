# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clrtobot.c

Read completely: 121 lines.

This file implements `clrtobot` and `wclrtobot`, clearing from the current cursor position to the bottom of the window.

`wclrtobot` validates the window, chooses the effective background character and attributes, accounts for `__ISPASTEOL` by starting at the next line, then scans all affected cells. Cells that satisfy `__NEED_ERASE` are reset to the background character, marked `CA_BACKGROUND`, stripped of continuation state, assigned background attributes while preserving `__ALTCHARSET`, and, in wide builds, given copied background nonspacing characters and `wcols = 1`. Dirty ranges are touched per line, then `__sync` propagates synchronization.

Important interactions: uses `__NEED_ERASE`, `_cursesi_copy_nsp`, `__touchline`, and `__sync`. Its behavior differs for `curscr`, where background attributes are forced to zero.

Reliability notes: wide erasure can fail if copying background nonspacing characters fails, returning `ERR` after earlier cells may have been modified.
