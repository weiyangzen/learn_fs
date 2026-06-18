# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfsnode.h

Read completely: 53 lines.

Defines the in-core state for an MFS backing device.

Core definitions:
- `struct mfsnode` stores the associated vnode, FIFO buffer queue, base user address, filesystem size, servicing thread id, an unused/legacy buffer-list pointer, and shutdown flag.
- `VTOMFS()` and `MFSTOV()` convert between vnode and mfsnode pointers.

Integration and risks:
- `mfs_baseoff`, `mfs_size`, and `mfs_tid` are consumed directly by strategy and I/O paths.
- Queue lifetime is owned by vnode reclaim, so close/reclaim ordering must keep pending buffers from referencing freed state.
