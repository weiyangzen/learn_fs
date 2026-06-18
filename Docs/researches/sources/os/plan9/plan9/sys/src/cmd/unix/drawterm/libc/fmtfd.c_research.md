# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/fmtfd.c

This file initializes `Fmt` output to a file descriptor.

Key behavior:
- `fmtfdinit` configures a `Fmt` with fd, buffer, flush callback, and output pointers.
- `fmtfdflush` flushes buffered bytes by writing to the fd.

Important details:
- Underpins `vfprint`, `fprint`, and related fd-based formatting.
