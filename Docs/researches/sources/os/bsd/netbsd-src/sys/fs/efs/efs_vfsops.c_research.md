# File Research: sources/os/bsd/netbsd-src/sys/fs/efs/efs_vfsops.c

Read completely: 595 lines.

Implements EFS VFS operations and module registration. The module registers `efs_vfsops`, malloc types, vnode operation vectors, and the inode pool lifecycle.

`efs_mount()` rejects updates, resolves and locks the block device, authorizes read access, opens it read-only, and calls `efs_mount_common()`. Common mount code reads the superblock, validates checksum and geometry, warns on dirty filesystems, verifies replicated superblocks when present, checks the last filesystem block is accessible, fills mount flags/stat data, and records the device vnode.

`efs_loadvnode()` allocates an in-core inode, reads the disk inode, converts it to host order, validates that the root inode is a directory, selects vnode type and operation vector for fifo/device/dir/reg/symlink/socket, initializes genfs state, and sets the vnode size. Device vnodes use decoded device metadata later in getattr, though the load path initializes spec nodes with `ei_dev`.

File handles include inode and generation; `efs_fhtovp()` rejects stale handles when mode is zero or generation mismatches. `efs_statvfs()` reports block counts and inode capacity from the superblock, and unmount flushes vnodes, closes the device, and frees the mount.
