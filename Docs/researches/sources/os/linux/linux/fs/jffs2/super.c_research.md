# File Research: sources/os/linux/linux/fs/jffs2/super.c

## Role

Registers JFFS2 with Linux VFS/MTD mount infrastructure and manages superblock lifecycle, mount options, inode slab allocation, NFS export hooks, sync, and module init/exit.

## Key Responsibilities

- Creates/destroys the `jffs2_i` inode slab cache and initializes per-inode mutex/VFS fields.
- Allocates and frees VFS inodes, including cached symlink targets.
- Parses `compr=` and `rp_size=` mount options through fs_context.
- Displays active options through `jffs2_show_options()`.
- Updates remount options under `alloc_sem`, syncs before reconfigure, and delegates to `jffs2_do_remount_fs()`.
- Fills the superblock in `jffs2_fill_super()`: attaches MTD and OS private pointers, validates reserve-pool size, initializes locks/wait queues, installs super/export/xattr operations, sets `SB_NOATIME`, and enables POSIX ACLs when configured.
- Provides NFS export helpers based on inode-number file handles and parent lookup through directory `pino_nlink`.
- Flushes write buffers in sync and put-super paths.
- Tears down summary state, inode caches, raw refs, block arrays, flash resources, xattrs, and MTD state in `jffs2_put_super()`.
- Initializes compressors, JFFS2 slab caches, and filesystem registration in `init_jffs2_fs()`.

## Important Interactions

- Calls `jffs2_do_fill_super()` for core filesystem initialization after Linux mount setup.
- Uses compressor mode constants from `compr.h`.
- Coordinates write-buffer flushing with `wbuf.c`.
- Stops the GC thread before killing writable superblocks.

## Invariants and Risks

- On-medium structure sizes are asserted at module init.
- `rp_size` must not exceed MTD size.
- Delayed RCU inode frees are flushed before destroying the inode cache.
