# File Research: sources/os/linux/linux-stable/fs/freevxfs/vxfs_super.c

This file implements FreeVxFS module setup, filesystem registration, superblock probing, mount initialization, statfs, inode cache management, and unmount cleanup.

Major responsibilities:
- Register the `vxfs` filesystem type and module aliases.
- Create and destroy the `vxfs_inode` slab cache.
- Allocate and free VxFS inodes through superblock operations.
- Release superblock-private resources on unmount.
- Report basic filesystem stats through `statfs`.
- Force mounts and reconfigurations to read-only.
- Probe possible VxFS superblock locations and byte orders.
- Read the OLT, fileset headers, inode lists, and root inode during mount.
- Create the root dentry.

Important design points:
- The driver probes block 1 for little-endian UnixWare-style VxFS and block 8 for big-endian HP-UX-style VxFS.
- The initial block size is set to the kernel minimum, then the final block size is taken from the VxFS superblock.
- Mount setup proceeds in dependency order: superblock, OLT, fileset headers, inode lists, root inode.
- `vxfs_reconfigure()` syncs the filesystem and forces `SB_RDONLY`.
- The inode cache is created with a usercopy-safe region covering inline immediate data.

Key invariants:
- The mounted filesystem is always read-only.
- Supported VxFS versions are 2 through 4.
- `sbp->s_fs_info` must contain a valid `vxfs_sb_info` before OLT and fileset header parsing.
- On mount failure, buffer heads, private superblock memory, and any acquired metadata inodes are released.
- Module cleanup unregisters the filesystem and waits for RCU inode frees before destroying the inode cache.

External interfaces:
- Registers filesystem type `vxfs`.
- Provides module init/exit functions and superblock operations used by VFS mount/unmount paths.
