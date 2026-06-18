# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/ftello.c

Read completely: 101 lines.

This file implements `ftello`. It mirrors `ftell` but returns `off_t`, flushing pending writes, querying current underlying offset, and adjusting for buffered input/output state.

Important interactions: used by `fgetpos`; weak alias `_ftello`.

Security/reliability notes: non-seekable streams fail with `ESPIPE`; no `long` truncation check is needed.
