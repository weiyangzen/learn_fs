# File Research: sources/os/bsd/netbsd-src/lib/libcurses/resize.c

Implements window and terminal resizing: `wresize`, `is_term_resized`, `resizeterm`, and `resize_term`.

`wresize` clamps requested sizes to parent or screen bounds, preserves requested dimensions, resizes `__virtscr` when `curscr` is resized, and delegates storage changes to `__resizewin`. Terminal resizing updates `LINES`/`COLS`, resizes standard/current/virtual screens, recomputes window flags, repositions ripoff windows, marks `curscr` clear, and redraws soft labels. `__resizewin` reallocates line/cell storage, remaps subwindows, clears contents to background, resets hashes/dirty markers, and recursively bounds child windows.
