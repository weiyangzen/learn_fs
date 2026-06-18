# File Research: sources/os/linux/linux-stable/fs/hpfs/super.c

This file implements HPFS filesystem registration, mount/remount parsing, superblock initialization, dirty-state management, statfs, trim ioctl handling, and HPFS inode slab setup.

Key responsibilities:
- Manages HPFS dirty/chkdsk state through sector 17 spare block updates in `mark_dirty()` and `unmark_dirty()`.
- Centralizes HPFS error policy in `hpfs_error()`, supporting continue, remount-readonly, and panic behavior.
- Provides cycle detection helper `hpfs_stop_cycles()` for corrupted on-disk graph structures.
- Counts free blocks and free dnodes by scanning HPFS bitmap sectors for `hpfs_statfs()`.
- Implements `FITRIM` in `hpfs_ioctl()` with `CAP_SYS_ADMIN` enforcement and sector-size conversion.
- Defines an HPFS-specific inode slab cache with `hpfs_alloc_inode()` and `hpfs_free_inode()`.
- Parses mount options via the modern `fs_context` API: `uid`, `gid`, `umask`, `case`, `check`, `errors`, `eas`, `chkdsk`, and `timeshift`.
- Handles remount/reconfigure in `hpfs_reconfigure()`, including rejecting `timeshift` changes.
- Initializes the superblock in `hpfs_fill_super()` by reading boot, super, and spare blocks, validating magic/version fields, loading hotfix maps, bitmap directories, optional code pages, and the root inode.

Important interactions:
- Uses HPFS helpers from `hpfs_fn.h` for sector mapping, bitmap loading, hotfix handling, root dnode lookup, inode initialization, and HPFS locking.
- Integrates with VFS through `super_operations`, `file_system_type`, `get_tree_bdev()`, `kill_block_super`, and `fs_context_operations`.
- Updates root inode timestamps and HPFS inode-private fields from the root directory entry after mounting.

Notable invariants and risks:
- HPFS uses 512-byte filesystem blocks and rejects superblock sizes at or above `0x80000000`.
- Dirty-state writes are synchronous to improve OS/2 chkdsk visibility.
- Mount error behavior is user-configurable and can intentionally continue on suspected corruption.
- `hpfs_fill_super()` has multiple buffer-head cleanup labels; correctness depends on each mapped sector being released on the matching failure path.
- Root inode setup depends on both `hpfs_read_inode()` and later root dirent lookup to finish timestamp and parent metadata.

Research notes:
- This is the operational entry point for HPFS in Linux: other HPFS files implement the metadata mechanics, while this file establishes the VFS contract, mount policy, and corruption response.
