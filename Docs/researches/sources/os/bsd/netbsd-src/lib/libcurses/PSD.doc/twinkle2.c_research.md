# File Research: sources/os/bsd/netbsd-src/lib/libcurses/PSD.doc/twinkle2.c

Read completely: 207 lines.

Variant of the twinkle demo that uses lower-level terminal capabilities for output. It initializes curses only enough to get terminal mode and cursor movement, calls termcap/terminfo-style routines such as `tgetent()`, `tgetflag()`, `tgetstr()`, `tputs()`, and direct `mvcur()`/`putchar()` output.

It requires a terminal on stdin, fetches `am`, `ti`, `vs`, and `cl` capabilities, enters terminal initialization/visual mode, clears the screen, then repeatedly generates patterns and writes stars/spaces in randomized order. `puton()` tracks the last cursor position and avoids auto-margin scrolling at the lower-right cell when needed.

This example contrasts curses window drawing with direct terminal-control output. It relies on fixed 80x24 dimensions, global capability strings, and old terminal APIs.
