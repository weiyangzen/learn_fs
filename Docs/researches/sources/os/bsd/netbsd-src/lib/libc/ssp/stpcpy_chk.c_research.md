# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/stpcpy_chk.c

Read completely: 58 lines.

This file implements `__stpcpy_chk`. It computes `strlen(src)`, fails if the string plus terminator cannot fit in `slen`, rejects overlap, copies with `memcpy`, and returns the pointer to the copied terminator position.

Important interactions: fortified `stpcpy` backend, with a compatibility declaration for older GCC.

Security/reliability notes: it checks overlap only across `len` bytes, while copying `len + 1`; the size check still protects the terminator from overflowing the destination.
