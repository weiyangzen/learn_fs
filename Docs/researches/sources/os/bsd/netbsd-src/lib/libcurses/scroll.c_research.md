# File Research: sources/os/bsd/netbsd-src/lib/libcurses/scroll.c

Implements logical scrolling and scroll-region APIs.

`wscrl` requires `__SCROLLOK`, preserves cursor position, moves to the top of the scroll region, delegates line movement to `winsdelln`, restores the cursor, and emits a newline when scrolling `curscr`. `wsetscrreg`/`wgetscrreg` manage per-window scroll bounds. `has_ic` and `has_il` report terminal insert/delete character or line capability availability.
