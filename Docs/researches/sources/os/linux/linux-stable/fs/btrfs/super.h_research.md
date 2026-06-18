# File Research: sources/os/linux/linux-stable/fs/btrfs/super.h

This header exposes a small Btrfs superblock-facing API used by other Btrfs files.

Declared functions:
- `btrfs_check_options()` validates parsed mount options against filesystem state and target superblock flags.
- `btrfs_sync_fs()` is the VFS sync implementation exported for use outside `super.c`.
- `btrfs_get_subvol_name_from_objectid()` resolves a subvolume objectid to a path-like subvolume name.
- `btrfs_set_free_space_cache_settings()` initializes effective free-space-cache mount behavior from on-disk state and mount options.

Inline helpers:
- `btrfs_sb()` returns `sb->s_fs_info` as `struct btrfs_fs_info *`.
- `btrfs_set_sb_rdonly()` sets `SB_RDONLY` and the Btrfs internal `BTRFS_FS_STATE_RO` bit.
- `btrfs_clear_sb_rdonly()` clears both the VFS read-only flag and the Btrfs internal read-only state bit.

Role:
- Keeps common superblock helpers available without exposing the full mount implementation in `super.c`.
- Maintains consistency between VFS `sb->s_flags` and Btrfs `fs_state` read-only tracking.
