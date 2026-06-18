# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_parent.h

## Role
`xfs_parent.h` declares parent pointer validation, hashing, update, decode, lookup, and repair interfaces, plus the parent pointer operation context object.

## Main Definitions
- `xfs_parent_rec_init` initializes an on-disk parent record from inode number and generation.
- `xfs_inode_to_parent_rec` builds a parent record from a directory inode.
- `struct xfs_parent_args` carries old parent record, new parent record, and embedded `xfs_da_args` for deferred/logged attr update machinery.
- `xfs_parent_start` allocates a parent args object only when the parent pointer feature is enabled.
- `xfs_parent_finish` frees that object when present.

## Exported API
- Validators and hashing: `xfs_parent_namecheck`, `xfs_parent_valuecheck`, `xfs_parent_hashval`, and `xfs_parent_hashattr`.
- Directory operation hooks: `xfs_parent_addname`, `xfs_parent_removename`, and `xfs_parent_replacename`.
- Raw attr decode: `xfs_parent_from_attr`.
- Repair helpers: `xfs_parent_lookup`, `xfs_parent_set`, and `xfs_parent_unset`.

## Dependencies
The header depends on `struct xfs_parent_rec` from on-disk DA format definitions, attr/DA args, mount feature checks, inode generation access, and the parent args slab cache.

## Research Notes
This header makes parent pointer updates optional at runtime: callers can always call `xfs_parent_start`, and non-parent filesystems simply receive a null context.
