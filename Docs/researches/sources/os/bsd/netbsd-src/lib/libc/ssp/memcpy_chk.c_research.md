# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/memcpy_chk.c

Read completely: 54 lines.

This file implements `__memcpy_chk`. It fails when `len > slen`, checks source/destination overlap with `__ssp_overlap`, then delegates to `memcpy`.

Important interactions: backs fortified `memcpy` expansion from SSP headers.

Security/reliability notes: unlike plain `memcpy`, this wrapper treats overlap as a checked failure, matching the undefined-overlap contract.
