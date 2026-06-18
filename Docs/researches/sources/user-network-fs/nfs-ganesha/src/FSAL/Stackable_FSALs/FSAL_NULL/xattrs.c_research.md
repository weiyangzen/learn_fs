<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/xattrs.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/xattrs.c

## Purpose

This file implements NULLFS legacy extended-attribute object operations. Like the rest of NULLFS, it delegates each xattr call to the lower FSAL after switching request context to the lower export.

## Important APIs, Types, and Functions

- `nullfs_list_ext_attrs`
- `nullfs_getextattr_id_by_name`
- `nullfs_getextattr_value_by_id`
- `nullfs_getextattr_value_by_name`
- `nullfs_setextattr_value`
- `nullfs_setextattr_value_by_id`
- `nullfs_remove_extattr_by_id`
- `nullfs_remove_extattr_by_name`
- `struct nullfs_fsal_obj_handle` and `struct nullfs_fsal_export` are recovered from public handles/context.

## Control Flow

Every function extracts the lower `sub_handle`, recovers the current NULLFS export from `op_ctx->fsal_export`, sets `op_ctx->fsal_export` to `export->export.sub_export`, calls the corresponding lower `obj_ops` function, restores the NULLFS export, and returns the lower status.

## State and Persistence Behavior

NULLFS stores no xattr data and does no xattr caching. All persistence, ID interpretation, permissions, and buffer-size behavior are delegated to the lower FSAL.

## Dependencies and Integration Points

The functions are installed into the NULLFS object ops vector in `handle.c`. The file depends on `os/xattr.h`, FSAL common types, and `nullfs_methods.h`. It only covers the older FSAL xattr API; NFSv4-style xattr methods are not implemented here for NULLFS.

## Risks and Edge Cases

- Optional xattr support must be reflected by lower FSAL ops/default ops; this layer does not check method availability.
- Context restoration must be maintained if additional error handling is added.
- ID-based xattr APIs can be unstable across lower FSAL implementations.

## Test Signals

Tests should run list/get/set/remove by name and ID through a NULLFS-stacked export, include unsupported lower-FSAL behavior, verify errors pass through unchanged, and confirm follow-up operations see lower-FSAL state changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/xattrs.c -->
