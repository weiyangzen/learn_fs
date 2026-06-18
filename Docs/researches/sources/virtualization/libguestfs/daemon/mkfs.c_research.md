# File Research: sources/virtualization/libguestfs/daemon/mkfs.c

Generic filesystem creation wrapper.

Important behavior:
- Uses `mke2fs` directly for ext filesystems and `mkfs -t` for others.
- Adds filesystem-specific flags for ext, NTFS, reiserfs/jfs/xfs, GFS/GFS2, FAT, btrfs, f2fs, and label handling.
- Validates block size as positive power-of-two.
- Maps FAT block size to sectors-per-cluster using `do_blockdev_getss`.
- Rejects unsupported option/type combinations, such as inode size outside ext or sector size outside ufs.
- Detects whether `mkfs.fat` supports `--mbr=n` and caches the result.
- Calls `wipe_device_before_mkfs(device)` before running mkfs.
- `do_mkfs_b` is a compatibility wrapper setting only the blocksize optarg.

Filesystem relevance: core filesystem formatting entry point across many local filesystem tools.
