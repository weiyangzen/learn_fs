# File Research: sources/os/linux/linux/fs/affs/super.c

Purpose: implements AFFS filesystem registration, superblock lifecycle, mount option parsing, root discovery, remount handling, statfs, inode cache management, and delayed superblock commits.

Key interfaces:
- `affs_sops`: alloc/free inode, write/evict inode, put/sync super, statfs, show_options.
- `affs_context_ops`: parse parameters, get block-device tree, reconfigure, free context.
- `affs_fs_type`: Linux filesystem type registration for `affs`.

Implementation notes:
- `affs_commit_super()` updates root tail disk-change time and checksum, then dirties/syncs the root block.
- `affs_mark_sb_dirty()` schedules delayed root-block commit through `system_long_wq`.
- Mount options include block size, mode, MUFS, no filename truncation, symlink prefix, protect/immutable, reserved blocks, root block, uid/gid overrides, verbose, and volume.
- `affs_fill_super()` probes block sizes/root block positions, validates root block checksum/type, reads the boot signature, and sets flags for FFS/OFS, INTL, MUFS, dircache, and read-only fallback.
- Dircache variants are mounted read-only if write access was requested.
- OFS reduces data block size by 24 bytes and sets `SB_NOEXEC`.
- Initializes bitmap state before reading the root inode; selects international or normal dentry ops.
- Reconfigure preserves only historical remount option behavior and updates prefix/volume under `symlink_lock`.

Dependencies:
- Uses fs_context parser APIs, block device helpers, AFFS bitmap initialization/free, AFFS inode cache, root block macros, and export ops.

Edge cases:
- Several early failure paths return without local cleanup in this file because block-super teardown handles most initialized state later.
- Root block probing compensates for odd partition-size/reserved-block geometry by trying the calculated root and the next block.
