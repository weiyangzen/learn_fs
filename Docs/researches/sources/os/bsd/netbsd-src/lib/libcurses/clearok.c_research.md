# File Research: sources/os/bsd/netbsd-src/lib/libcurses/clearok.c

Read completely: 55 lines.

This file implements `clearok(WINDOW *win, bool bf)`. It validates the window and sets or clears the `__CLEAROK` flag, controlling whether refresh should clear the physical screen before repainting.

Important interactions: refresh logic consumes `__CLEAROK`; this file only toggles the state.

Reliability notes: null windows return `ERR`.
