# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgets.c

Read completely: 131 lines.

This file implements `fgets`. It locks the stream, sets byte orientation, refills as needed, copies from the internal read buffer up to newline or `n - 1`, NUL-terminates, and returns `NULL` only when no bytes were read or the length is invalid.

Important interactions: depends on `__srefill`, stream buffer fields, and `memchr`/`memcpy`.

Security/reliability notes: `n <= 0` is treated as `EINVAL` and sets stream error; partial lines at EOF are returned.
