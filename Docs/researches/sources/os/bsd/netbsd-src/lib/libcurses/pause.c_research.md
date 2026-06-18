# File Research: sources/os/bsd/netbsd-src/lib/libcurses/pause.c

Implements output delay helpers: `napms` and `delay_output`.

`napms` sleeps using `nanosleep` for the requested milliseconds. `delay_output` uses terminal padding when `_cursesi_screen->padchar` exists by passing a millisecond string to `tputs`; otherwise it falls back to `napms`.
