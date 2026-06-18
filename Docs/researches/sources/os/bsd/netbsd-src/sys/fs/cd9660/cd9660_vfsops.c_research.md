# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_vfsops.c

Read completely: 931 lines.

Implements cd9660 VFS operations and module registration. `cd9660_vfsops` wires mount, unmount, root, statvfs, vnode-cache loading, file-handle conversion, init/done, and mountroot operations, and the module attaches/detaches the filesystem with `vfs_attach()`/`vfs_detach()`.

Mounting is strictly read-only. `cd9660_mount()` validates mount arguments, supports legacy mount data size, handles `MNT_GETARGS`, rejects writable mounts, resolves and authorizes the block device, opens it for reading, and delegates initial filesystem parsing to `iso_mountfs()`. Updates are limited to verifying the same device and unchanged uid/gid/mask policy.

`iso_mountfs()` invalidates old buffers, reads ISO volume descriptors from sector 16 onward, accepts a primary descriptor and optional supplementary descriptor, builds `struct iso_mnt`, records block size/shift/root metadata, detects Rock Ridge through `cd9660_rrip_offset()`, and only falls back to Joliet when Rock Ridge is disabled or unavailable. It also handles session offsets from disklabel or CD-ROM multisession ioctl.

`cd9660_loadvnode()` allocates an `iso_node`, finds the directory record by inode-number-as-directory-record-offset, validates block boundaries, reads ISO/RRIP attributes and timestamps, assigns vnode type and operation vector, initializes spec/fifo nodes when needed, and marks the root vnode. NFS file handles carry inode offsets without generation validation beyond checking mode presence.
