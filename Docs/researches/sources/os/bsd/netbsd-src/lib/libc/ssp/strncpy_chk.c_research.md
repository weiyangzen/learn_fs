# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strncpy_chk.c

Read completely: 55 lines.

This file implements `__strncpy_chk`. It validates `len <= slen`, rejects overlap for the requested range, and delegates to `strncpy`.

Important interactions: fortified `strncpy` backend.

Security/reliability notes: preserves `strncpy` semantics, including padding and possible lack of NUL termination.
