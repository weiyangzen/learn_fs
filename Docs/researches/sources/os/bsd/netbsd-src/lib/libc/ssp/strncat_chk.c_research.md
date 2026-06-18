# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strncat_chk.c

Read completely: 73 lines.

This file implements `__strncat_chk`. It returns immediately for zero append length, fails if the requested append bound exceeds `slen`, scans the existing destination within capacity, copies at most `len` source bytes, and ensures final NUL termination fits.

Important interactions: fortified `strncat` backend.

Security/reliability notes: the initial `len > slen` check is conservative but the full safety check is the later capacity countdown over existing and appended bytes.
