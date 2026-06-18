# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/utmpx.h

Read completely: 101 lines.

This header defines legacy `utmpx50` and `lastlogx50` records using `timeval50`, plus inline conversion between current `utmpx` and old `utmpx50`. It declares compatibility wrappers for utmpx iteration, lookup, update, lastlog, and utmp/utmpx conversion functions.

Important interactions: relies on `compat/sys/time.h` conversion helpers and current utmpx layouts. Most fields are copied wholesale, with only embedded time values converted.

Security/reliability notes: ABI-only surface. Timestamp narrowing to 32-bit seconds is the primary correctness limit.
