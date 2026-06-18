# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ftell.c

Read completely: 106 lines.

This file implements `ftell`. It flushes pending writes, obtains the underlying offset from cached `__SOFF` or the seek hook, adjusts for unread buffered and ungetc bytes or unwritten buffered bytes, checks for `long` overflow, and returns the position.

Important interactions: legacy `long` API counterpart to `ftello`.

Security/reliability notes: non-seekable streams fail with `ESPIPE`; offsets too large for `long` fail with `EOVERFLOW`.
