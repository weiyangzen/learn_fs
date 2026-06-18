# File Research: sources/os/bsd/netbsd-src/lib/libcurses/mvwin.c

Implements window relocation: `mvderwin` and `mvwin`.

`mvderwin` changes a derived window’s source offset within its parent and marks the parent source area dirty. `mvwin` moves parent windows and their circular subwindow list together, or validates and rebinds a child window inside its parent through `__set_subwin`; it recalculates flags with `__swflags` and touches the moved window.
