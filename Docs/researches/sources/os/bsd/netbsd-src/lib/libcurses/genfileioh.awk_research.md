# File Research: sources/os/bsd/netbsd-src/lib/libcurses/genfileioh.awk

Read completely: 66 lines.

This AWK script generates `fileio.h` from `shlib_version`. It extracts and normalizes NetBSD RCS version strings for provenance comments, reads `major=` and `minor=` assignments, and emits `CURSES_LIB_MAJOR` and `CURSES_LIB_MINOR` defines.

Important interactions: `Makefile` uses this script to build `fileio.h`, which `fileio.c` uses to version-check serialized windows.

Reliability notes: if `major` or `minor` is absent from input, the generated macro value is empty.
