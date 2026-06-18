# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/var.c

Small variable utilities for `mk`.

Key functions:
- `setvar(name, value)` installs a variable in `S_VAR` and marks it as `S_MAKEVAR`.
- `dumpv()` prints all variables.
- `print1()` formats one variable’s word list.
- `shname()` returns the first non-shell-word character in a name.

Role:
- Used by parser, environment import, and shell expansion code.
