# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.h

Read completely: 50 lines.

This private header defines `struct __siov` and `struct __suio`, the lightweight vector I/O descriptors consumed by `__sfvwrite`, and declares `__sfvwrite`.

Important interactions: included by output functions that batch memory regions into the stdio write engine.

Security/reliability notes: no logic here; callers must keep `uio_resid` consistent with the vector lengths.
