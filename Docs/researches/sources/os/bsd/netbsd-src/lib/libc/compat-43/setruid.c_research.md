# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/setruid.c

## Scope

Compatibility implementation of deprecated `setruid()`.

## Behavior

- Emits a link-time deprecation warning.
- Calls `setreuid(ruid, (uid_t)-1)` to change only the real user ID.

## Dependencies And Invariants

- Effective UID is intentionally left unchanged with `(uid_t)-1`.
