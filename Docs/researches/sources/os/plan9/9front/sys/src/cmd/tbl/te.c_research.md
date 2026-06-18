# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/te.c

Implements error reporting and low-level input handling for `tbl`.

Key points:
- `error` prints the active input file and line, announces `tbl quits`, and exits.
- `gets1` reads one logical line from `tabin`, increments `iline`, swaps input files when needed, bounds-checks the caller buffer, strips the newline, and folds escaped newlines while inside a table.
- `un1getc` implements a small pushback buffer and adjusts `iline` for pushed-back newlines.
- `get1char` reads from pushback or `tabin`, swaps input files on EOF, errors on unexpected EOF, and increments `iline` for newline characters.

Dependencies and interactions:
- Uses Plan 9 `Biobuf` routines `Brdline`, `Blinelen`, and `Bgetc`.
- Calls `swapin` for multi-file input sequencing.

Research relevance:
- This is the shared input/error layer used by the parser and text-block reader.
