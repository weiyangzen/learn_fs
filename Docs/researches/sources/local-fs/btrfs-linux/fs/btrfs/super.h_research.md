# File Research: sources/local-fs/btrfs-linux/fs/btrfs/super.h

This header exposes the small public interface from `super.c` needed by other Btrfs code and defines inline helpers for accessing Btrfs filesystem state from a VFS superblock.

Declared API:
- `btrfs_check_options()` validates mount option bits against filesystem state and requested superblock flags.
- `btrfs_sync_fs()` is the Btrfs sync-super operation and can also be called directly by internal code.
- `btrfs_get_subvol_name_from_objectid()` resolves a subvolume root objectid to a path string.
- `btrfs_set_free_space_cache_settings()` initializes free-space-cache/free-space-tree mount policy from on-disk state and mount options.

Inline helpers:
- `btrfs_sb()` returns `sb->s_fs_info` as `struct btrfs_fs_info *`.
- `btrfs_set_sb_rdonly()` sets VFS `SB_RDONLY` and Btrfs `BTRFS_FS_STATE_RO`.
- `btrfs_clear_sb_rdonly()` clears both the VFS readonly flag and the Btrfs readonly state bit.

Cross-file relationships:
- Implemented by `super.c`.
- Included by mount, disk I/O, transaction, and filesystem-state code that needs access to `btrfs_fs_info` or needs to coordinate VFS readonly state with Btrfs internal state.
- Includes `fs.h` for `BTRFS_FS_STATE_RO` and the `btrfs_fs_info` state-bit definitions.

Important invariants:
- Readonly transitions must update both `sb->s_flags` and `fs_info->fs_state`; callers should use the inline helpers rather than setting one side manually.
- `btrfs_sb()` assumes `s_fs_info` has already been initialized with a valid Btrfs filesystem info object.
