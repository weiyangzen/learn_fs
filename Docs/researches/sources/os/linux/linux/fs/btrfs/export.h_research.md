# File Research: sources/os/linux/linux/fs/btrfs/export.h

## Purpose

`export.h` declares Btrfs exportfs support and defines the packed file-handle payload used by `export.c`.

## Public Declarations

- `btrfs_export_ops`: exported `struct export_operations` used by the superblock/exportfs layer.
- `btrfs_get_dentry()`: reconstructs a dentry from objectid, root objectid, and generation.
- `btrfs_get_parent()`: finds a dentry’s parent for exportfs reconnect.

## Data Structure

`struct btrfs_fid` is a packed file identifier containing:

- `objectid`
- `root_objectid`
- `gen`
- `parent_objectid`
- `parent_gen`
- `parent_root_objectid`

The optional parent fields allow Btrfs to encode both ordinary parent relationships and cross-root/subvolume parent relationships.

## Integration Points

Included by `export.c` and any Btrfs code needing direct exportfs helpers.

## Invariants

The structure is packed because file handles are serialized into fixed-size exportfs buffers, and size calculations in `export.c` rely on exact field layout.
