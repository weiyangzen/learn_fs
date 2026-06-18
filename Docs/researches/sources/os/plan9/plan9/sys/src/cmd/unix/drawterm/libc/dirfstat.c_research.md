# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/dirfstat.c

This file returns allocated `Dir` data for an open fd.

Key behavior:
- `dirfstat` calls `fstat`, decodes with `convM2D`, allocates enough space for `Dir` plus strings, and returns it.

Important details:
- Uses a stack stat buffer sized for common cases.
- Returns `nil` on syscall or decoding failure.
