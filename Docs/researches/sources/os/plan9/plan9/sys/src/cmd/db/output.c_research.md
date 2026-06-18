# File Research: sources/os/plan9/plan9/sys/src/cmd/db/output.c

This file implements shared I/O plumbing for the Plan 9 `db` debugger: formatted output, output redirection, input redirection stack management, and line-column tracking.

Key behaviors:
- Maintains `printcol`, `infile`, `maxpos`, and a global `Biobuf stdout`.
- `dprint()` formats into a fixed 4096-byte buffer, writes to `stdout`, and updates `printcol` by decoding UTF runes.
- `flushbuf()`, `newline()`, `endline()`, `flush()`, `prints()`, and `printc()` form the debugger’s low-level output API.
- `redirout()` appends to an existing output file or creates a new one, reinitializing the output `Biobuf`.
- `iclose()` manages debugger input nesting for `$<` and `$<<` style command files, with a hard maximum depth of five.
- `outputinit()` initializes output and installs `%t` formatting as a literal tab via `tconv()`.

Notable implementation details:
- `dprint()` suppresses output while `mkfault` is set.
- `iclose(err=1)` unwinds all stacked input files after an error.
- The output redirection path calls `flushbuf()` before replacing the buffered descriptor.
