# File Research: sources/os/plan9/plan9/sys/src/cmd/idiff.c

`idiff.c` is an interactive diff merger inspired by Kernighan and Pike.

Key behavior:
- Usage: `idiff [-bw] file1 file2`.
- Validates both inputs are non-directories, opens them with `Biobuf`, and runs `/bin/diff -n`.
- Stores diff output and merged result in temporary ORCLOSE files.
- `idiff` walks normal diff hunks and prompts the user:
  - `<` keeps file1 side.
  - `>` takes file2 side.
  - `=` inserts diff text.
  - `q<`, `q>`, `q=` select a default for all remaining hunks.
  - `!cmd` runs a shell command.
- Copies selected line ranges into output, then writes final merged output to stdout.

Important dependencies:
- Relies on Plan 9 `/bin/diff -n` output format and Biobuf line helpers.

Notable risks/quirks:
- Temporary creation loops over `mktemp` up to 10 tries.
- Diff parser is strict and fatal on unexpected format.
