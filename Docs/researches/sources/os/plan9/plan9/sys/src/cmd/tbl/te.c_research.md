# File Research: sources/os/plan9/plan9/sys/src/cmd/tbl/te.c

Error handling and character/line input support.

Key functions:
- `error` prints `file:line` diagnostics, says `tbl quits`, and exits.
- `gets1` reads a full line with `Brdline`, swaps input files at EOF, strips newline, tracks `iline`, and folds escaped newlines while inside a table.
- `un1getc` pushes one character into a fixed backup buffer and decrements line number for newlines.
- `get1char` returns backed-up characters before reading from `tabin`, swapping files on EOF.

Notable behavior:
- Backup buffer is fixed at 500 characters.
- A NUL read from `Bgetc` is treated as EOF in this code.
