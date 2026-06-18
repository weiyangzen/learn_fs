# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/Makefile

Read completely: 32 lines.

Documentation Makefile for the curses paper/manual article. It builds article `curses` in section `reference/ref3` from `Master`, dependencies, and formatted C examples.

The `.c.gr` rule uses `TOOL_VFONTEDPR` and filters out `^'wh` lines to generate troff-ready example listings. `intro.2.tbl` is generated from `intro.2` with `TOOL_TBL`. Comments note that vgrind output should not be regenerated casually because it may require patching.

This is documentation build glue, not runtime curses code.
