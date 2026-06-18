# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/strcat_chk.c

Read completely: 62 lines.

This file implements `__strcat_chk` by manually walking the destination and source while decrementing the known destination capacity. It fails if the existing destination string, appended source, or final terminator would exceed `slen`.

Important interactions: fortified `strcat` backend.

Security/reliability notes: no explicit overlap detection is performed; overflow detection is capacity-driven.
