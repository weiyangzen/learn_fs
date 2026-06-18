# File Research: sources/os/bsd/netbsd-src/lib/libcurses/mouse.c

Provides minimal mouse API support and coordinate transforms.

`wenclose` tests whether screen-relative coordinates are inside a window, while `mouse_trafo` and `wmouse_trafo` convert between screen and window coordinates. Actual event support is stubbed: `has_mouse` is false, `getmouse`/`ungetmouse` return `ERR`, `mousemask` returns zero, and `mouseinterval` returns the default click interval.
