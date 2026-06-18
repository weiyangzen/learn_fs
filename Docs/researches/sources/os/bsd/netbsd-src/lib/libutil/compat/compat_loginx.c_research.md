# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_loginx.c

## Purpose
Legacy `loginx()` wrapper for old `struct utmpx50`.

## Key Details
- Converts `utmpx50` to current `struct utmpx`.
- Calls `__pututxline50`.
- Appends to `_PATH_WTMPX` with `__updwtmpx50`.

## Dependencies and Role
- Compatibility equivalent of `loginx.c`.
- Handles extended login accounting records for old ABI consumers.
