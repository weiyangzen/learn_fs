# File Research: sources/os/bsd/netbsd-src/lib/libutil/loginx.c

## Purpose
Records an extended login in `utmpx`/`wtmpx`.

## Key Details
- Calls `pututxline`.
- Appends to `_PATH_WTMPX` with `updwtmpx`.

## Dependencies and Role
- Modern login accounting helper.
