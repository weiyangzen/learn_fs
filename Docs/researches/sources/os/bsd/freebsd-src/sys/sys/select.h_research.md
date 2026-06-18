# File Research: sources/os/bsd/freebsd-src/sys/sys/select.h

Public `select(2)`/`pselect(2)` ABI header.

Key responsibilities:
- Defines `__fd_mask`, optional BSD-visible `fd_mask`, `FD_SETSIZE`, `_NFDBITS`, and `fd_set`.
- Provides `FD_CLR`, `FD_COPY`, `FD_ISSET`, `FD_SET`, and `FD_ZERO`.
- Declares `pselect()` and `select()` for userspace.
- Pulls in signal-set and time structures needed by `pselect()` and `select()`.

Important patterns:
- `fd_set` is a fixed-size bitset of descriptor bits stored in `unsigned long` words.
- With `_FORTIFY_SOURCE`, `__fdset_idx()` validates the requested descriptor index and object size before indexing.
- `FD_SETSIZE` is user-overridable before inclusion, defaulting to 1024.

Research relevance:
- Defines the classic descriptor readiness bitmap ABI used by filesystem, socket, pipe, and device readiness paths.
- Pairs with kernel `selinfo`/`selrecord` machinery for readiness notification.
