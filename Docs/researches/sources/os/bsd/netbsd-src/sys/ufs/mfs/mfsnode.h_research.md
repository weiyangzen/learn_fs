# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfsnode.h

This header defines MFS per-device state.

Key contents:
- `struct mfsnode` stores associated vnode, backing memory base, size, servicing process, shutdown flag, condition variable, reference count, and buffer queue.
- Defines `VTOMFS(vp)` and `MFSTOV(mfsp)` conversion macros under `_KERNEL`.

Role:
- The control object that binds a synthetic block vnode to a memory range and service loop.
