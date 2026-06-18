# File Research: sources/os/plan9/9front/sys/src/cmd/ed.c

This is the Plan 9 line editor `ed`. It implements address parsing, command execution, file I/O, temporary-file-backed line storage, regular-expression matching, substitution, global commands, marks, shell escapes, browsing, and hangup recovery.

Key responsibilities:
- Maintains the editable buffer as an array of temporary-file line addresses (`zero`, `dot`, `dol`).
- Runs the command loop in `commands`, handling classic `ed` commands including append/change/delete/edit/read/write/substitute/global/move/copy/join/print/quit.
- Parses addresses with `.`, `$`, marks, numeric offsets, and regex searches.
- Uses Plan 9 regex (`regcomp`, `rregexec`) for searches and substitutions.
- Stores line text in a block-cached temp file using `getblock`, `getline`, and `putline`.
- Handles interrupts and hangups with `notifyf`; on hangup it writes `ed.hup`.
- Implements list/numbered output formatting in `putchr`, `putshst`, and `putd`.

Important implementation notes:
- `global` has a special optimized path for `g/.../d`.
- `substitute` supports numbered match selection, global substitution, `&`, and `\1`-style captured substitutions.
- `quit` protects against unsaved changes when verbose mode is active.
- The code uses Rune buffers throughout for Plan 9 Unicode text handling.
