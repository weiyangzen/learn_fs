# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/sprint.c

This file formats into an unbounded byte buffer.

Key behavior:
- `sprint` initializes a formatter over the supplied buffer and formats with no practical bound.

Important details:
- Caller must provide enough storage.
