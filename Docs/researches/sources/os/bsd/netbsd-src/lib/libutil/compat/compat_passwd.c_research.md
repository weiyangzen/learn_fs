# File Research: sources/os/bsd/netbsd-src/lib/libutil/compat/compat_passwd.c

## Purpose
Compatibility wrappers for password database helper APIs using `struct passwd50`.

## Key Details
- Wraps:
  - `pw_scan`
  - `pw_copy`
  - `pw_copyx`
  - `pw_getpwconf`
- Converts between `struct passwd50` and current `struct passwd`.
- Emits warning references for old symbols.

## Dependencies and Role
- Delegates to current `__pw_scan50`, `__pw_copy50`, `__pw_copyx50`, and `__pw_getpwconf50`.
- ABI preservation layer only.
