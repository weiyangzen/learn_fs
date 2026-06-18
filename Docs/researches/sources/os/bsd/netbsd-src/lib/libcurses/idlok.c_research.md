# File Research: sources/os/bsd/netbsd-src/lib/libcurses/idlok.c

Read completely: 60 lines.

This file implements `idlok(WINDOW *win, bool bf)`, toggling the `__IDLINE` flag for insert/delete-line sequence use during refresh.

Important interactions: refresh and line-update code can use `__IDLINE` to decide whether terminal insert/delete-line capabilities may be used.

Reliability notes: null windows return `ERR`.
