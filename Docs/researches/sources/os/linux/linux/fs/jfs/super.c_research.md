# File Research: sources/os/linux/linux/fs/jfs/super.c

JFS filesystem module, mount-context, superblock, quota, freeze, export, and lifecycle implementation.

Key responsibilities:
- Declares module metadata, JFS global worker threads, and the JFS inode slab cache.
- Implements `jfs_error()` and error policy handling: continue, remount read-only, or panic.
- Implements inode allocation/free callbacks for JFS private inode structures.
- Implements `jfs_statfs()` from bmap and imap accounting.
- Parses mount/remount options for integrity, charset, resize, errors policy, quota flags, uid/gid/umask, and discard.
- Implements reconfiguration, including online resize, read-only/read-write transitions, quota suspend/resume, and integrity-mode remounts.
- Implements `jfs_fill_super()` to allocate `jfs_sb_info`, set superblock operations, create the direct-mapping inode, mount JFS metadata, mount RW state, and instantiate the root inode.
- Implements freeze/unfreeze by quiescing transactions, shutting down or reinitializing the log, and updating superblock state.
- Implements sync, show-options, NFS export operations, fs-context operations, and file-system-type registration.
- Implements quota file read/write and quota on/off flag management when quota support is enabled.
- Starts and stops JFS I/O, lazy commit, and sync kernel threads at module init/exit.

Important interactions:
- Calls core JFS mount/unmount routines `jfs_mount()`, `jfs_mount_rw()`, `jfs_umount()`, and `jfs_umount_rw()`.
- Uses transaction, metapage, journal, bmap, imap, inode, xattr, ACL, and export subsystems.
- Installs `jfs_super_operations`, `jfs_export_operations`, `jfs_context_ops`, and `jfs_fs_type`.
- Uses `jfs_extendfs()` for remount-time resize.
- Uses quota VFS interfaces and direct block mapping through `jfs_get_block()` for quota file I/O.

Invariants and risks:
- `direct_inode` backs metadata I/O and must be torn down carefully on mount failure and unmount.
- Mount option parsing transfers ownership of loaded NLS tables between fs context and superblock.
- Quota files are made immutable/noatime while enabled and restored when disabled.
- Freeze failure after quiescing must resume transactions to avoid hangs.
- Module init failure unwinds in reverse order across slab, metapage, transaction manager, worker threads, procfs, and filesystem registration.
