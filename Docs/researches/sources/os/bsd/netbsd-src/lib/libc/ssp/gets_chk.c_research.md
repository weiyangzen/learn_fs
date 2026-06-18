# File Research: sources/os/bsd/netbsd-src/lib/libc/ssp/gets_chk.c

Read completely: 75 lines.

This file implements `__gets_chk`, a fortified wrapper around legacy `gets` behavior. For bounded objects, it reads into a temporary `malloc(slen + 1)` buffer with `fgets`, strips a trailing newline for length checking, fails if the input would fill or exceed the destination, then copies and terminates the destination.

Important interactions: calls the internal `__gets` fallback when the object size is too large or allocation fails.

Security/reliability notes: this mitigates known object-size overflows but preserves dangerous `gets` compatibility in fallback paths.
