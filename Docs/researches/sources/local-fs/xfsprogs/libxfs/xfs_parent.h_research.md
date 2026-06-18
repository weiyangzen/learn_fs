# File Research: sources/local-fs/xfsprogs/libxfs/xfs_parent.h

## Role

This header declares parent pointer validation, hashing, transactional update, parsing, lookup, and repair APIs. It also defines the parent pointer update context wrapper.

## Main Contents

- `xfs_parent_namecheck` and `xfs_parent_valuecheck` validate parent pointer xattr fields.
- `xfs_parent_hashval` and `xfs_parent_hashattr` compute parent pointer attr hashes.
- `xfs_parent_rec_init` and `xfs_inode_to_parent_rec` initialize parent records from inode number and generation.
- `struct xfs_parent_args` stores old/new parent records plus `xfs_da_args`.
- `xfs_parent_start` allocates parent args only when the parent feature is enabled.
- `xfs_parent_finish` frees parent args.
- `xfs_parent_addname`, `xfs_parent_removename`, and `xfs_parent_replacename` update parent pointers for directory operations.
- `xfs_parent_from_attr` parses parent pointer xattrs.
- `xfs_parent_lookup`, `xfs_parent_set`, and `xfs_parent_unset` support repair paths.

## Dependencies

This header depends on parent feature checks, kmem caches, inode generation access, da args, xfs names, and parent record format definitions.

## Research Notes

The inline allocation helpers make parent pointer support cheap to call from generic directory code: callers can request a context unconditionally and get `NULL` when the feature is off.
