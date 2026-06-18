# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sysfatal.c

This file implements fatal error reporting.

Key behavior:
- `sysfatal` formats an error message, appends current error text for `%r`, writes to fd 2, and exits.
- `_sysfatalimpl` contains the shared `va_list` implementation.

Important details:
- Uses `_exits`/`exits`-style termination.
