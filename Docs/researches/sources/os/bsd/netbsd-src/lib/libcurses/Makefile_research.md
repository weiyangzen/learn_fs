# File Research: sources/os/bsd/netbsd-src/lib/libcurses/Makefile

Read completely: 226 lines.

Main NetBSD `libcurses` build file. It defines `LIB=curses`, warning level, include paths, optional `DEBUG_CURSES` and `SMALL` flags, dependency on `libterminfo`, installed headers `curses.h` and `unctrl.h`, and the large source list for the curses implementation.

Wide-character support is enabled unless `DISABLE_WCHAR` is defined, adding `cchar.c`, `add_wch.c`, `add_wchstr.c`, `addwstr.c`, `echo_wchar.c`, `ins_wch.c`, `ins_wstr.c`, `get_wch.c`, `get_wstr.c`, `in_wch.c`, `in_wchstr.c`, and `inwstr.c`. Otherwise it defines `DISABLE_WCHAR`.

Most of the file is manual-page `MLINKS`, mapping curses family pages to individual function names. It also builds `fileio.h` from `shlib_version` through `genfileioh.awk` and includes the `PSD.doc` documentation subdirectory.
