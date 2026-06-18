# File Research: sources/os/bsd/netbsd-src/lib/libcurses/fileio.c

Read completely: 245 lines.

This file implements window serialization and deserialization with `putwin` and `getwin`, excluding `LIBHACK` builds. It includes generated `fileio.h` for `CURSES_LIB_MAJOR` and `CURSES_LIB_MINOR`.

`putwin` rejects null windows and subwindows, writes the library version, writes the raw `WINDOW` structure, writes the background nonspacing list in wide builds, then writes every cell's character and attributes. `getwin` validates the version, reads a temporary `WINDOW`, allocates a new window with `__newwin`, copies selected fields from the serialized structure, restores flags with `__swflags`, reads background nonspacing state, reads every cell's character and attributes, touches each line, and returns the new window.

Important interactions: depends on `genfileioh.awk` output, `__newwin`, `__swflags`, `delwin`, `__touchline`, and nonspacing helpers from `curses.c`.

Reliability notes: the wide helper `__putnsp` never advances `nsp` inside its loop, so any non-null nonspacing list would cause an infinite write loop. Cell serialization also calls `__putnsp(win->bnsp, fp)` when `sp->nsp != NULL`, which appears to serialize the background list rather than the cell's foreground list. `__getnsp` assumes a non-null list head when appending nodes, making serialized nonspacing data fragile.
