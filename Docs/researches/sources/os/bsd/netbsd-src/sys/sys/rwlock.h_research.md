# File Research: sources/os/bsd/netbsd-src/sys/sys/rwlock.h

Read completely: 120 lines.

This header defines the kernel reader/writer lock type and interface. `krw_t` distinguishes `RW_READER` and `RW_WRITER`, and `struct krwlock` contains the volatile owner word.

When `__RWLOCK_PRIVATE` is set, the file exposes packed owner-word bits for waiters, write-wanted, write-locked, debug disable, reader-count shift/increment, owner/count extraction, and vector fallback functions. Kernel APIs cover init/destroy, enter/exit, tryenter, upgrade/downgrade, ownership tests, lock operation query, and reference-counted lock object allocation/free.

Risks: the private encoding packs owner pointer or reader count with state bits. Architecture stubs and generic vector paths must agree on this layout.
