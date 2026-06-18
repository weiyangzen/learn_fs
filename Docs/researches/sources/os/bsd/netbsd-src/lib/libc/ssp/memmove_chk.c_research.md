# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/memmove_chk.c

Read completely: 50 lines.

This file implements `__memmove_chk`. It only validates that the requested length fits within the destination object size, then calls `memmove`.

Important interactions: fortified `memmove` backend.

Security/reliability notes: overlap is allowed by design, so this wrapper does not call `__ssp_overlap`.
