# File Research: sources/os/bsd/openbsd-src/sys/sys/lockf.h

Kernel-only advisory record-locking interface declarations.

Key APIs:
- `lf_init()`: initialize lockf subsystem.
- `lf_advlock()`: implement advisory locking operations over a `struct lockf_state **`.
- `lf_purgelocks()`: remove all locks for a lock state.

Integration:
- Depends on `struct flock`, `off_t`, and vnode/file code using POSIX/BSD byte-range locks.
