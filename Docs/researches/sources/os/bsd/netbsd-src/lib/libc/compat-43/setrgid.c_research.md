# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/setrgid.c

## Scope

Compatibility implementation of deprecated `setrgid()`.

## Behavior

- Emits a link-time deprecation warning.
- Calls `setregid(rgid, (gid_t)-1)` to change only the real group ID.

## Dependencies And Invariants

- Effective GID is intentionally left unchanged with `(gid_t)-1`.
