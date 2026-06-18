# File Research: sources/local-fs/xfsprogs/db/debug.c

Purpose: implements the `debug` command and global debug bit state.

Key behavior:
- Defines global `long debug_state`.
- `debug` with no argument prints the current debug state.
- `debug flagbits` parses a numeric value with `strtol`, updates `debug_state`, and prints it.
- `debug_init` registers the command.

Interactions:
- `flist.c` checks `debug_state & DEBUG_FLIST` to decide whether to dump parsed field-list internals.
- Uses `dbprintf` for command output and validation errors.

Risks/notes:
- Debug flags are process-global and affect subsequent commands until changed.
