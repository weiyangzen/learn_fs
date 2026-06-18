# File Research: sources/os/bsd/netbsd-src/lib/libwrap/expandm.c

## Purpose
Expands `%m` in syslog-style format strings to the current `strerror(errno)` text.

## Key Details
- Preserves original `errno`.
- Handles escaped percent sequences so only odd `%m` occurrences expand.
- Optionally appends suffix string `sf`.
- Returns allocated expanded buffer through `rbuf` when requested.
- On allocation/size failure, returns original format string and sets `*rbuf=NULL`.

## Dependencies and Role
- Used by `diag.c` before `vasprintf`.
