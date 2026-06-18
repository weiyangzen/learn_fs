# File Research: sources/os/bsd/openbsd-src/sys/sys/select.h

Defines `select(2)`/`pselect(2)` fd-set ABI and time structures when not already declared.

Key contents:
- Conditional `struct timeval` and `struct timespec` declarations.
- Default `FD_SETSIZE` of 1024.
- Internal fd mask type `__fd_mask` as `uint32_t`, bit count `__NFDBITS`, and `__howmany`.
- `fd_set` definition.
- Inline helpers and public macros `FD_SET`, `FD_CLR`, `FD_ISSET`, `FD_ZERO`, and BSD-visible `FD_COPY`.
- BSD-visible aliases `NBBY`, `fd_mask`, `NFDBITS`, `howmany`.
- Userland prototypes for `select` and `pselect`.

Risk notes:
- No bounds checks are performed by the fd-set macros; callers must keep fd values below `FD_SETSIZE`.
