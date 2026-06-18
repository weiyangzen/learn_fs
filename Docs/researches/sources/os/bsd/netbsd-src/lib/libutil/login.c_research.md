# File Research: sources/os/bsd/netbsd-src/lib/libutil/login.c

## Purpose
Records a login in legacy `utmp` and `wtmp`.

## Key Details
- Uses `ttyslot()` to locate the `utmp` slot.
- Writes the supplied `struct utmp` to `_PATH_UTMP`.
- Appends the same record to `_PATH_WTMP`.
- Ignores open/write failures.

## Dependencies and Role
- Login accounting support.
