# File Research: sources/os/bsd/netbsd-src/lib/libwrap/expandm.h

## Purpose
Declares `expandm`.

## Key Details
- Uses `__BEGIN_DECLS`/`__END_DECLS`.
- Marks `expandm` with `__format_arg__(1)` so compilers can understand that its return value is a format string derived from argument 1.

## Dependencies and Role
- Header for `diag.c` and `expandm.c`.
