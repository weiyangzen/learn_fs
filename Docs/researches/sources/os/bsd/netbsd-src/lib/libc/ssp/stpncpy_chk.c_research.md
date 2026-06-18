# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/stpncpy_chk.c

Read completely: 56 lines.

This file implements `__stpncpy_chk`. It fails if `len` exceeds the destination object size, rejects overlap for the specified range, and delegates to `stpncpy`.

Important interactions: fortified `stpncpy` backend.

Security/reliability notes: behavior follows bounded-copy semantics, including possible non-NUL-terminated output.
