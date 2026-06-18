# File Research: sources/os/bsd/netbsd-src/lib/libc/compat-43/creat.c

## Scope

Compatibility implementation of `creat()`.

## Behavior

- Validates `path` with `_DIAGASSERT`.
- Calls `open(path, O_WRONLY | O_CREAT | O_TRUNC, mode)` and returns its result.

## Dependencies And Invariants

- Depends on `<fcntl.h>` `open()` flags.
- Preserves historical `creat()` semantics as a thin `open()` wrapper.
