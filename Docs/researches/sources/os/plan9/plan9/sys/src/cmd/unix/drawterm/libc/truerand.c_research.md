# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/truerand.c

This file returns host-provided random data as an unsigned long.

Key behavior:
- `truerand` calls `randomread` to fill a `ulong`.

Important details:
- Entropy source is provided by the host shim (`posix.c` or `win32.c`).
