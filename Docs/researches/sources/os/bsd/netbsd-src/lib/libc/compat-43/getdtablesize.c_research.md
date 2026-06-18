# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/getdtablesize.c

## Scope

Compatibility implementation of `getdtablesize()`.

## Behavior

- Returns `(int)sysconf(_SC_OPEN_MAX)`.

## Dependencies And Invariants

- Uses libc namespace setup and `<unistd.h>`.
- Mirrors the old descriptor-table-size API through the modern `sysconf` query.
