# File Research: sources/os/bsd/netbsd-src/lib/libcurses/idcok.c

Read completely: 61 lines.

This file implements `idcok(WINDOW *win, bool bf)`, toggling the `__IDCHAR` flag for insert/delete-character sequence use.

The comment notes that insert/delete character capabilities are currently not used, so this function primarily preserves compatibility.

Important interactions: any future refresh optimization for character insert/delete would consume `__IDCHAR`.

Reliability notes: null windows return `ERR`.
