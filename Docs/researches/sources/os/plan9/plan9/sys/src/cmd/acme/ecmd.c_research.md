# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/ecmd.c

This file executes Acme `Edit` language commands after parsing.

Key behavior:
- `cmdexec()` resolves default/current addresses, maps commands to handlers, and executes command blocks.
- Implements edit commands: append/insert/change/delete, file switch/open/delete, read/write, print, substitute, move/copy, undo/redo, global/looping commands, pipe commands, address reporting, and file matching.
- `runpipe()` integrates `<`, `|`, `>` edit commands with external process execution and `editout`.
- `looper()`, `linelooper()`, and `filelooper()` implement `x/y` and `X/Y` iteration over ranges or files.
- `cmdaddress()` evaluates parsed `Addr` trees against current `Address`.
- `cmdname()` resolves and optionally sets file names, warning on duplicate window names.

Important details:
- Edit commands log changes into `Elog` first, so command addresses refer to the original buffer state.
- `filelooper()` protects windows with refs and `globalincref` during cross-window edits.
- `runpipe()` temporarily changes global `editing` state to collect or insert command output, unlocks row/window around external execution, then relocks.
- Substitute supports `&` and `\1`-`\9` replacement captures with size checks.
- `e_cmd()` treats full same-file replacement as clean if the file content was re-read successfully.

Filesystem relevance:
- High: implements editor commands that read/write real files, open named buffers, and pipe selections through Acme’s mounted namespace.
