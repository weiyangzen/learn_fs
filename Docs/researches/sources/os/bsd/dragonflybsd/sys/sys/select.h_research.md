# File Research: sources/os/bsd/dragonflybsd/sys/sys/select.h

This header defines the userland `select()`/`pselect()` ABI and pulls in the fd, signal, timeval, and timespec types needed by those interfaces.

Key responsibilities:
- Includes:
  - `sys/_fd_set.h`
  - `sys/_sigset.h`
  - `sys/_timespec.h`
  - `sys/_timeval.h`
- Defines `sigset_t` from `struct __sigset` if not already declared.
- Declares:
  - `select()`
  - `pselect()`

Important invariants:
- The prototypes use `restrict` annotations through `__restrict`.
- `pselect()` takes `const struct timespec *` and `const sigset_t *`.
- `select()` takes a mutable `struct timeval *`, matching traditional timeout modification semantics.

Research notes:
- This is a compact user ABI forwarding header.
