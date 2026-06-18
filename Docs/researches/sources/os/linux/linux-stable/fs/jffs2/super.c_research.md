# File Research: sources/os/linux/linux-stable/fs/jffs2/super.c

This file registers JFFS2 with the Linux VFS/MTD mount layer and manages superblock lifecycle, mount options, inode cache allocation, NFS export hooks, sync, and module init/exit.

Key responsibilities:
- Creates and destroys the `jffs2_i` inode slab cache and initializes per-inode mutex/VFS fields.
- Implements inode allocation/free, including freeing cached symlink target strings.
- Parses `compr=` and `rp_size=` mount options through the `fs_context` parser and displays them through `show_options`.
- Updates remount options under `alloc_sem`, syncs the filesystem before reconfigure, and delegates remount work to `jffs2_do_remount_fs()`.
- Fills the superblock in `jffs2_fill_super()`: attaches MTD and OS private pointers, validates reserved-pool size, initializes locks/wait queues, installs super/export/xattr operations, sets `SB_NOATIME`, and enables POSIX ACL flag when configured.
- Provides NFS export helpers using inode-number file handles and parent lookup via directory `pino_nlink`.
- Flushes the write buffer on sync and put-super.
- Tears down summary, inode caches, raw refs, block arrays, flash resources, xattrs, and MTD state in `jffs2_put_super()`.
- Stops the GC thread before killing writable superblocks in `jffs2_kill_sb()`.
- Registers/unregisters the `jffs2` filesystem and initializes compressors and JFFS2 slab caches in module init/exit.

Important interactions:
- Uses `get_tree_mtd()`/`kill_mtd_super()` for MTD-backed mounting.
- Delegates full filesystem construction to `jffs2_do_fill_super()` in `fs.c`.
- Installs `jffs2_super_operations`, `jffs2_export_ops`, and `jffs2_xattr_handlers`.

Notable invariants and risks:
- `rp_size` is specified in KiB but stored in bytes and must not exceed the MTD size.
- Inode numbers are not protected by generation checks for NFS export; comments state flash lifetime/inode reuse semantics are relied on.
- Write-buffer delayed work is cancelled during sync for write-buffered media before padding/flushing.
