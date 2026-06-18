# File Research: sources/os/linux/linux-stable/fs/affs/super.c

This file implements AFFS superblock setup, mount option parsing, remount handling, statfs, delayed superblock updates, inode cache lifecycle, and module registration.

Major responsibilities:
- Defines AFFS `super_operations`, file-system type, fs-context operations, and inode slab cache.
- Parses mount options such as `bs`, `mode`, `mufs`, `nofilenametruncate`, `prefix`, `protect`, `reserved`, `root`, `setgid`, `setuid`, `verbose`, and `volume`.
- Finds and validates the AFFS root block across plausible block sizes and root locations.
- Reads the boot block signature to determine OFS/FFS, international, dircache, and MUFS behavior.
- Initializes bitmap state, root inode, dentry operations, export operations, and superblock flags.
- Supports remount/reconfigure by syncing, flushing delayed superblock work, updating mutable options, and allocating/freeing bitmaps as read-write state changes.

Mount probing:
- Starts with device size in 512-byte sectors, sets a large temporary block size, then tries logical block size through page size unless `bs=` fixes it.
- Computes default root block as the middle of the partition after reserved blocks.
- Tries the computed root and one adjacent block to handle odd partition-size rounding.
- Valid root blocks require checksum success, root head primary type `T_SHORT`, and root tail secondary type `ST_ROOT`.

Filesystem variant handling:
- Dircache AFFS variants are forced read-only for writes.
- OFS variants set `SF_OFS` and `SB_NOEXEC`; their data block size is reduced by the OFS data header size.
- International variants set `SF_INTL` and use international dentry operations.
- MUFS variants set `SF_MUFS` and alter UID/GID interpretation.

Superblock writes:
- `affs_commit_super()` updates the root block disk-change timestamp, fixes checksum, marks it dirty, and optionally waits.
- `affs_mark_sb_dirty()` queues delayed writeback using `dirty_writeback_interval`.
- `affs_sync_fs()` commits the root block synchronously or asynchronously depending on VFS request.

Cleanup:
- `affs_kill_sb()` kills the block super, frees bitmap state, releases root buffer, frees symlink prefix, destroys locks, and RCU-frees `sbi`.
- Inode cache creation/destruction is handled at module init/exit.
