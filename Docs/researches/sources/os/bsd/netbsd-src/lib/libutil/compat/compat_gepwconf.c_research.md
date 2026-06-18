# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_gepwconf.c

## Purpose
Compatibility wrapper for old `pw_getpwconf` using `struct passwd50`.

## Key Details
- Defines `__LIBC12_SOURCE__`.
- Emits `__warn_references` for callers binding the old symbol.
- Converts `struct passwd50` to current `struct passwd` with `passwd50_to_passwd`.
- Calls `__pw_getpwconf50`.

## Dependencies and Role
- Depends on `<compat/include/pwd.h>` and `<compat/util.h>`.
- Narrow ABI shim; no independent password configuration parsing.
