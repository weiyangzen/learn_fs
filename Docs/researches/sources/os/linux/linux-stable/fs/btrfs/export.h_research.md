# File Research: sources/os/linux/linux-stable/fs/btrfs/export.h

## Purpose
Defines Btrfs exportfs public types and declarations.

## Main Types
- Declares `btrfs_export_ops`, the `struct export_operations` instance implemented by `export.c`.
- Defines packed `struct btrfs_fid`, containing:
  - child `objectid`
  - child `root_objectid`
  - child generation
  - parent `objectid`
  - parent generation
  - optional `parent_root_objectid` for cross-subvolume file handles

## Exported Helpers
- `btrfs_get_dentry()` resolves an objectid/root/generation tuple to a dentry.
- `btrfs_get_parent()` resolves a dentry’s parent for exportfs path reconnection.

## Dependency Shape
Includes only exportfs/types headers and forward-declares `dentry` and `super_block`, keeping the header lightweight for users that only need export operation declarations.
