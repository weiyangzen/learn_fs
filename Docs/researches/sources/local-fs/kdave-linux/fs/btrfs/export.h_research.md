# File Research: sources/local-fs/kdave-linux/fs/btrfs/export.h

## Role

Declares Btrfs exportfs support: the exported operations table, packed Btrfs file-handle payload, and helper functions used to reconstruct dentries and parents.

## Key Definitions

- `extern const struct export_operations btrfs_export_ops`: operations installed for exportfs/NFS file-handle support.
- `struct btrfs_fid`: packed file-handle layout containing:
  - `objectid`: inode object ID;
  - `root_objectid`: root/subvolume object ID;
  - `gen`: inode generation;
  - `parent_objectid`: optional parent inode object ID;
  - `parent_gen`: optional parent generation;
  - `parent_root_objectid`: optional parent root ID for cross-root parent handles.

## API Surface

- `btrfs_get_dentry()` reconstructs a dentry from superblock, inode object ID, root object ID, and optional generation.
- `btrfs_get_parent()` returns a dentry for the parent of a child dentry.

## Dependencies

Includes Linux exportfs and integer types. It forward declares `dentry` and `super_block` so consumers do not need the full VFS definitions from this header alone.

## Research Notes

The packed file-handle structure mirrors the three encoding modes in `export.c`: non-connectable inode/root/generation, connectable same-root parent information, and connectable cross-root parent information.
