# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vfsops.c

This file implements the MFS VFS layer. MFS presents a memory range as a synthetic block device, then mounts FFS over it.

Key responsibilities:
- Registers `mfs_vfsops` as a VFS module depending on FFS.
- Initializes and tears down global MFS state and FFS support.
- Implements `mfs_mountroot` for miniroot boot mounting.
- Implements `mfs_mount` for normal MFS mounts from user-provided base/size arguments.
- Implements `mfs_start`, the service loop that processes queued buffer I/O for the memory-backed block vnode.
- Implements `mfs_statvfs` by delegating to FFS and overriding filesystem type name.

Important behavior:
- Normal mounts allocate synthetic block device minor numbers under major 255.
- MFS disables async and forces synchronous mounting to avoid memory-pressure deadlocks where cleaning pages requires allocating pages.
- `mfs_start` holds an extra `mfsnode` reference, drains its buffer queue, handles signals by attempting unmount, and exits on `mfs_shutdown`.
- Root MFS uses `mfs_proc == NULL` to indicate kernel-space miniroot memory rather than userspace-backed memory.
