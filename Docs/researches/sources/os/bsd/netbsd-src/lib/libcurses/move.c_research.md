# File Research: sources/os/bsd/netbsd-src/lib/libcurses/move.c

Implements cursor movement: `move`, `wmove`, and `wcursyncup`.

`wmove` bounds-checks coordinates, allows `x == maxx` as a past-EOL cursor state, updates `__ISPASTEOL` flags, and records `cury`/`curx`. `wcursyncup` propagates a subwindow cursor position upward through parent windows using screen-relative offsets.
