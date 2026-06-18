# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strcpy_chk.c

Read completely: 55 lines.

This file implements `__strcpy_chk`. It computes `strlen(src) + 1`, fails if that exceeds the destination object size, rejects overlap, and copies the full string with `memcpy`.

Important interactions: fortified `strcpy` backend.

Security/reliability notes: source must still be a valid NUL-terminated string; the wrapper protects only known destination bounds and overlap.
