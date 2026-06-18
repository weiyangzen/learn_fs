# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/life.c

Read completely: 161 lines.

Partial historical Game of Life demonstration listing for the curses documentation. The file defines a doubly linked `LIST` of live cells, global `Head`, initializes curses, gathers an initial board from the user, and repeatedly calls `prboard()` and `update()`.

Visible functions include `main()`, `die()`, `getstart()`, and `prboard()`. `getstart()` lets users move with vi-like surrounding keys, add/remove cells, load a file, and quit setup; then it scans the screen for live cells and adds them to the linked list. `prboard()` erases, boxes the screen, draws live cells, and refreshes.

The listing references functions not present in this file segment, such as `evalargs`, `adjustyx`, `readfile`, `dellist`, `addlist`, and `update`, implying the documentation excerpt is incomplete or split elsewhere. It is old K&R-style demo code.
