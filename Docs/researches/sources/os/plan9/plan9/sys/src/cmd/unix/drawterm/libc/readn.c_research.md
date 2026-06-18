# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/readn.c

This file implements exact-length reads.

Key behavior:
- `readn` loops until it reads the requested byte count, sees EOF, or gets an error.

Important details:
- Returns bytes actually read.
