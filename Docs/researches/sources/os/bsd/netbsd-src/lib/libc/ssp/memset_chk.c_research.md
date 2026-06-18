# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/memset_chk.c

Read completely: 49 lines.

This file implements `__memset_chk`. It checks `len > slen` and calls `__chk_fail()` on overflow, otherwise delegates to `memset`.

Important interactions: fortified `memset` backend.

Security/reliability notes: the only policy is destination-size enforcement; value and pointer validity remain normal `memset` responsibilities.
