# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetws.c

Read completely: 88 lines.

This file implements `fgetws`. It validates positive length, sets wide orientation, reads wide characters one at a time with `__fgetwc_unlock`, stops at newline, EOF after some data, or capacity, then NUL-terminates.

Important interactions: wide string input wrapper around the lower-level wide character reader.

Security/reliability notes: `n <= 0` returns `NULL` with `EINVAL`; errors and EOF before any character also return `NULL`.
