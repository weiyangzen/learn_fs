# File Research: sources/os/bsd/dragonflybsd/sys/sys/_fd_set.h

Read completely: 86 lines.

This header defines the `fd_set` type and classic `select(2)` bitset macros.

Key contents:
- Default `FD_SETSIZE` of 1024.
- `__fd_mask`, `__NFDBITS`, and `fd_set`.
- `FD_SET`, `FD_CLR`, `FD_ISSET`, `FD_ZERO`, and BSD-visible aliases such as `fd_mask`, `NFDBITS`, `howmany`, and `FD_COPY`.

Security/reliability notes:
- The macros do not bounds-check descriptor indexes; callers must ensure `0 <= fd < FD_SETSIZE`.
- `FD_ZERO` and `FD_COPY` use compiler builtins for fixed-size struct clearing/copying.
