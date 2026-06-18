# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/vsmprint.c

This file allocates formatted byte strings using a `va_list`.

Key behavior:
- `fmtstrinit` initializes a growable byte formatter.
- `fmtStrFlush` grows the buffer when full.
- `vsmprint` formats and returns the allocated NUL-terminated string.

Important details:
- Byte-string counterpart to `runevsmprint`.
