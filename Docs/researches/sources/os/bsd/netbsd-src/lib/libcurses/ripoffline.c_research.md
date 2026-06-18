# File Research: sources/os/bsd/netbsd-src/lib/libcurses/ripoffline.c

Implements ripoff-line reservation and lifecycle.

`ripoffline` records pre-initialization top or bottom line reservations and callbacks. `__ripoffscreen` creates windows for recorded reservations during screen setup, calls each callback, and stores them in `SCREEN.ripped`; `__rippedlines` reports reserved line counts. Resize/touch helpers keep ripoff windows positioned and refreshed, while `__unripoffline` lets soft-label initialization cancel a reservation when terminal-native labels are available.
