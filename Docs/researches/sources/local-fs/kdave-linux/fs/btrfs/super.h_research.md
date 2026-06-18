# File Research: sources/local-fs/kdave-linux/fs/btrfs/super.h

Read coverage: complete file, 38 lines.

This small header exposes Btrfs superblock-facing helpers and declarations used outside `super.c`.

Declared API:
- `btrfs_check_options()` validates mount option state against filesystem features and mount flags.
- `btrfs_sync_fs()` implements the VFS sync callback.
- `btrfs_get_subvol_name_from_objectid()` resolves a subvolume objectid into a path-like name.
- `btrfs_set_free_space_cache_settings()` derives free-space-cache mount behavior after mount options and on-disk feature state are known.

Inline helpers:
- `btrfs_sb()` returns `struct btrfs_fs_info *` from `super_block->s_fs_info`.
- `btrfs_set_sb_rdonly()` sets `SB_RDONLY` and `BTRFS_FS_STATE_RO`.
- `btrfs_clear_sb_rdonly()` clears both the VFS readonly flag and Btrfs readonly state bit.

Integration notes:
- The readonly helpers are used by remount code to keep VFS superblock flags and Btrfs internal state synchronized.
- This header is a narrow bridge between generic VFS superblock code and Btrfs `fs_info` state.

Risk notes:
- Readonly state must be updated through these paired helpers where possible; setting only the VFS flag or only the Btrfs state bit can desynchronize mount behavior.
