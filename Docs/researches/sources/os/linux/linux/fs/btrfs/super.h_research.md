# File Research: sources/os/linux/linux/fs/btrfs/super.h

## Scope And Role

`super.h` is the small public header for Btrfs superblock-facing helpers and declarations. It exposes selected functions from `super.c` and inline helpers for converting and changing VFS superblock read-only state.

## Public Declarations

Declared functions:

- `btrfs_check_options()`: validates mount option combinations against filesystem state and requested superblock flags.
- `btrfs_sync_fs()`: VFS `sync_fs` implementation.
- `btrfs_get_subvol_name_from_objectid()`: reconstructs a subvolume path from a root objectid.
- `btrfs_set_free_space_cache_settings()`: derives free-space cache/free-space-tree settings during mount.

Forward declarations:

- `struct super_block`
- `struct btrfs_fs_info`

The header includes `linux/types.h`, `linux/fs.h`, and Btrfs `fs.h`.

## Inline Helpers

`btrfs_sb()` returns `sb->s_fs_info` as `struct btrfs_fs_info *`.

`btrfs_set_sb_rdonly()` sets VFS `SB_RDONLY` and Btrfs `BTRFS_FS_STATE_RO`.

`btrfs_clear_sb_rdonly()` clears both the VFS read-only flag and the Btrfs internal read-only state bit.

These helpers ensure VFS and Btrfs internal read-only state are updated together.

## Integration Points

This header is used by Btrfs files that need superblock conversion, read-only state changes, sync invocation, option validation, or free-space cache setup without depending on the full `super.c` implementation details.

## Concurrency And State Notes

The read-only helpers do not perform locking themselves. Callers must invoke them in contexts where superblock and filesystem state transitions are serialized, such as mount/remount paths.

`btrfs_sb()` assumes `s_fs_info` has been initialized to a valid `btrfs_fs_info`.

## Risks And Edge Cases

Any caller bypassing `btrfs_set_sb_rdonly()` or `btrfs_clear_sb_rdonly()` can desynchronize `SB_RDONLY` from `BTRFS_FS_STATE_RO`.

The declarations expose functions implemented in `super.c`, so signature drift would break cross-file build consistency.

## Testing Signals

Tests should cover:

- Read-only remount paths setting both VFS and Btrfs state.
- Read-write remount paths clearing both state bits.
- Callers of `btrfs_check_options()` rejecting invalid read-write rescue combinations.
- Subvolume name reconstruction through `btrfs_get_subvol_name_from_objectid()`.
