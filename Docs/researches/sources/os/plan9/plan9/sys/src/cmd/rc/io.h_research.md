# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/io.h

Shared buffered I/O definitions for rc.

Defines:
- `EOF (-1)`;
- `NBUF 512`;
- `struct io` with fd, buffer pointers, optional string pointer, and inline buffer;
- global `err`;
- prototypes for buffered input/output, string/core openers, command/function printers, and formatting primitives.

Risk/notes:
- `strp != nil` distinguishes string/core buffers from fd-backed buffers.
