# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_login.c

## Purpose
Legacy `login()` implementation for old `struct utmp50`.

## Key Details
- Converts `utmp50` to current `struct utmp`.
- Updates `_PATH_UTMP` at the current `ttyslot()`.
- Appends the record to `_PATH_WTMP`.
- Emits a warning reference telling callers to include `<util.h>` for the correct reference.

## Dependencies and Role
- Mirrors `login.c` behavior after compatibility conversion.
- Operates directly on legacy utmp/wtmp files.
