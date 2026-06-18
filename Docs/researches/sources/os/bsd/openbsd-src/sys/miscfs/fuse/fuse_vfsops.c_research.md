# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fuse/fuse_vfsops.c

Purpose: Implements FUSE filesystem mount-level operations and initialization.

Key behavior:
- Defines `fusefs_vfsops` for mount, start, unmount, root, quotactl, statfs, sync, vget, file-handle conversions, init, sysctl, and export checks.
- `fusefs_mount()` validates the supplied file descriptor as a character vnode, enforces root-only `allow_other`, allocates `fusefs_mnt`, records mount names, associates the FUSE device, and queues `FBT_INIT`.
- `fusefs_unmount()` flushes vnodes, sends `FBT_DESTROY` when the session is live, cleans device queues, detaches the mount, and frees mount state.
- `fusefs_root()` returns vnode for `FUSE_ROOTINO` as a directory and marks it root through `fusefs_vget()`.
- `fusefs_statfs()` enforces `allow_other`, returns dummy stats before init completes to avoid mount-time deadlock, otherwise sends `FBT_STATFS`.
- `fusefs_vget()` reuses hash-cached nodes or creates new vnodes/nodes, initializes recursive vnode locks and file-handle slots, inserts into the inode hash, marks root vnodes, and initializes file size from attributes for non-root nodes.
- `fusefs_init()` initializes the `fusebuf` pool and inode hash.
- Sysctl exposes opened FUSE device count, inbound/waiting request counts, and pool page count.

Limitations:
- Quotas, file-handle export/import, and NFS export checks are unsupported.
