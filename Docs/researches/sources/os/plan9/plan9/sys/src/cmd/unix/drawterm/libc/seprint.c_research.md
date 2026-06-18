# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/seprint.c

This file formats into a bounded byte buffer ending at a pointer.

Key behavior:
- `seprint` wraps `vseprint` with varargs.

Important details:
- Returns the end pointer after formatted output.
