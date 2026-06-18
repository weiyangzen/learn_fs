# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_fifoops.c

Read completely: 117 lines.

This defines the tmpfs vnode operation vector for FIFOs. Most FIFO behavior comes from `GENFS_FIFOOP_ENTRIES` and calls through `fifo_vnodeop_p`; tmpfs overrides close/read/write plus common metadata operations.

`tmpfs_fifo_read` updates atime before delegating to fifofs read, and `tmpfs_fifo_write` updates mtime before delegating to fifofs write.

Important interactions: included in the tmpfs VFS operation-vector list and selected by `tmpfs_init_vnode` for `VFIFO` nodes.

Security/reliability notes: wrappers are thin and rely on fifofs for FIFO semantics. Metadata updates preserve tmpfs timestamps around delegated operations.
