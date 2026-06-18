# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_parent.h

This header declares parent pointer validation, hashing, update, extraction, and repair interfaces.

Key contents:
- Validators:
  - `xfs_parent_namecheck`
  - `xfs_parent_valuecheck`
- Hash helpers:
  - `xfs_parent_hashval`
  - `xfs_parent_hashattr`
- Inline record initializers:
  - `xfs_parent_rec_init`
  - `xfs_inode_to_parent_rec`
- Parent args slab cache declaration.
- `struct xfs_parent_args`, carrying old/new parent records and `xfs_da_args`.
- `xfs_parent_start` and `xfs_parent_finish`, which allocate/free update context only when parent pointers are enabled.
- Update APIs for add, remove, and replace.
- `xfs_parent_from_attr` to parse parent pointer xattrs.
- Repair APIs for lookup, set, and unset.

Integration:
- Used by directory operations, metadir updates, attr item logging, scrub/repair paths, and inode creation policy.

Risk notes:
- `xfs_parent_start` returns success with `NULL` args when the feature is disabled, so callers must tolerate no-op parent pointer context.
- Parent pointer updates share attr machinery and must preserve correct owner/name/value state in `xfs_da_args`.
