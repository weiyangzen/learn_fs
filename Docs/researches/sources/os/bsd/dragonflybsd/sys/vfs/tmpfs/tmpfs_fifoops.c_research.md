# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_fifoops.c

This file customizes vnode operations for FIFOs stored in TMPFS while delegating core FIFO behavior to `fifo_vnode_vops`.

`tmpfs_fifo_kqfilter` marks the TMPFS node as accessed for read filters or modified for write filters, then forwards to the FIFO kqfilter operation. `tmpfs_fifo_close` marks access, updates timestamps through `tmpfs_update`, then forwards to FIFO close.

The exported `tmpfs_fifo_vops` uses `fifo_vnoperate` as default and overrides close, reclaim, access, getattr, setattr, and kqfilter with TMPFS-aware operations.
