<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/handle.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/handle.c

## Purpose

This file implements NULLFS object-handle wrapping and most non-I/O object operations. It turns lower-FSAL handles into `nullfs_fsal_obj_handle` objects, delegates namespace and attribute operations to the lower handle, and translates readdir callbacks so upper layers see NULLFS handles.

## Important APIs, Types, and Functions

- `nullfs_alloc_handle`: allocates a wrapper handle, initializes the public FSAL handle, copies type/fsid/fileid/fs/state state handle from the lower handle, assigns `NULLFS.handle_ops`, and sets `refcnt`.
- `nullfs_alloc_and_check_handle`: wraps a successful lower handle creation result.
- Namespace operations: `lookup`, `makedir`, `makenode`, `makesymlink`, `readsymlink`, `linkfile`, `renamefile`, and `file_unlink`.
- Directory operations: `nullfs_readdir_cb`, `read_dirents`, `compute_readdir_cookie`, and `dirent_cmp`.
- Attribute and wire-handle operations: `getattrs`, `nullfs_setattr2`, `handle_to_wire`, `handle_to_key`, `nullfs_lookup_path`, and `nullfs_create_handle`.
- Lifecycle and special handling: object `release` and `nullfs_is_referral`.
- `nullfs_handle_ops_init`: starts from `fsal_default_obj_ops_init` and installs NULLFS operation wrappers, including file and xattr operations declared elsewhere.

## Control Flow

Creation-style calls set `*new_obj` or `*handle` to NULL, switch to the lower export, call the lower operation, restore NULLFS context, then wrap the returned lower handle on success. Non-creation calls delegate to lower ops and return the lower status. Readdir is special: the lower FSAL receives `nullfs_readdir_cb`, which wraps each lower dirent handle, restores upper NULLFS context for the original callback, then restores lower context before continuing lower readdir.

## State and Persistence Behavior

Each NULLFS handle owns a pointer to the lower `sub_handle` and participates in the FSAL module handle list through `fsal_obj_handle_init(..., true)`. Release delegates lower release, finalizes the wrapper handle, and frees the wrapper. Persistent filesystem data remains lower-FSAL-owned; NULLFS persists only wrapper identity and copied metadata fields.

## Dependencies and Integration Points

This file ties together `NULLFS.handle_ops`, `nullfs_fsal_export`, lower `obj_ops`, common FSAL handle initialization/finalization, NFSv4 ACL headers, and object type helpers. Export-level `lookup_path` and `create_handle` are referenced from `export.c`.

## Risks and Edge Cases

- `nullfs_alloc_and_check_handle` assumes allocation succeeds; `nullfs_alloc_handle` does not check `gsh_calloc` return before dereference.
- If a lower FSAL returns success with `sub_handle == NULL`, wrapper allocation would dereference NULL.
- Some functions cast `obj_hdl` directly to `struct nullfs_fsal_obj_handle *` rather than using `container_of`; this relies on `obj_handle` being the first field.
- Readdir callback returns `false` on wrapper allocation failure although the enum is `enum fsal_dir_result`; this depends on `false` mapping to the intended stop/continue value.
- Context switching around callbacks is subtle and must match the stack direction.

## Test Signals

Tests should cover lookup/create/mkdir/mknode/symlink/link/rename/unlink pass-through, handle serialization round trips, readdir handle wrapping and cookie compare behavior, release ordering, referral detection, and failure injection where lower operations return errors or NULL handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/handle.c -->
