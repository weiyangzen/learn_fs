# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vnops.c

Read completely: 263 lines.

Implements vnode operations for the synthetic MFS block device used as backing storage for an FFS filesystem.

Core behavior:
- `mfs_vops` rejects normal filesystem operations with generic badops and provides open, close, ioctl, strategy, inactive, reclaim, print, and generic bmap/bwrite behavior.
- `mfs_strategy()` validates a block vnode, then either services I/O directly if called by the MFS server thread or queues the buffer and wakes the server.
- `mfs_doio()` clamps I/O to the memory filesystem size, translates block number to memory offset, copies data with `copyin()` for reads and `copyout()` for writes, sets `B_ERROR`/`b_resid`, and completes the buffer with `biodone()` under `splbio()`.
- `mfs_close()` drains queued buffers, invalidates in-core buffers with `vinvalbuf()`, marks shutdown, and wakes the server.
- `mfs_inactive()` unlocks the vnode; `mfs_reclaim()` destroys the buffer queue, frees the mfsnode, and clears vnode data.

Integration and risks:
- The apparent block device is backed by user address space, so copy direction and bounds are central.
- Direct self-I/O avoids deadlock when the server thread issues I/O against its own device.
- Shutdown requires queue draining before invalidation and reclaim.
