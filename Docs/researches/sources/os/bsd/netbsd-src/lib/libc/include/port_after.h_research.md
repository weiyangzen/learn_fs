# File Research: sources/os/bsd/netbsd-src/lib/libc/include/port_after.h

Small ISC porting macro header for safe string assembly.

Defines:
- `ADDC(C)`: appends one character to `dst`, NUL-terminates, and jumps to `emsgsize` if there is insufficient space.
- `ADDS(S)`: calls an appending expression, validates its length against remaining buffer, and advances index `t`.

Used by inet conversion routines for consistent `EMSGSIZE` handling.
