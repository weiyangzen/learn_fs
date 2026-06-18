# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fmemopen.c

Read completely: 240 lines.

This file implements `fmemopen` using a custom cookie with `head`, `tail`, current position, and end-of-buffer pointers. It provides memory read, write, seek, and close hooks, allocates backing storage when `buf == NULL` for read-write modes, initializes append/truncate behavior, and returns a `FILE` from `__sfp`.

Important interactions: uses `__sflags` and stdio custom-cookie hook fields.

Security/reliability notes: size zero and read/write modes without caller storage are invalid. Writes always maintain a NUL terminator when possible and stop before overflowing the memory region.
