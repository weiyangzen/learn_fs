# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/shprint.c

Expands selected mk variables into shell recipe text for printing and execution.

Key functions:
- `shprint()` scans recipe text, expanding `$name` and `${name}` via `vexpand()` while preserving quoted strings through `copyq()`.
- `mygetenv()` only expands internal variables and variables set in the mkfile.
- `front()` shortens a command string for error messages to a few fields.

Behavior notes:
- Variables not internal or mk-set are left intact for the shell.
- `wtos()` output is freed after insertion.
