# File Research: sources/os/bsd/netbsd-src/lib/libcurses/flushok.c

Read completely: 55 lines.

This file implements `flushok(WINDOW *win, bool bf)`. It validates the window and sets or clears `__FLUSH`, controlling whether refresh should flush output after updating the window.

Important interactions: refresh code consumes the flag; this file only toggles it.

Reliability notes: null windows return `ERR`.
