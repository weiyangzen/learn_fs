# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/vfs/subfsal_vfs.c

## Purpose

This file supplies the generic VFS sub-FSAL export hooks used by the common FSAL_VFS implementation. It defines the VFS export configuration block, including `fsid_type` parsing and `async_hsm_restore`, and allocates VFS object handles with inline storage for a `vfs_file_handle_t`. The source was read as a complete 113-line file.

## Important APIs, Types, and Functions

Important exported symbols are `vfs_sub_export_param`, `vfs_sub_fini`, `vfs_sub_init_export_ops`, `vfs_sub_init_export`, `vfs_sub_alloc_handle`, `vfs_obj_subops`, and `vfs_sub_init_handle`. `fsid_types` maps text tokens such as `One64`, `Two64`, `Dev`, and `Device` to `enum fsid_type` values. `vfs_obj_subops` installs `vfs_sub_getattrs` and `vfs_sub_setattrs` from the VFS attributes layer.

## Control Flow

Configuration parsing uses `export_param_block` to populate `vfs_fsal_export` fields. Export initialization optionally initializes debug ACL support, then returns success. Handle allocation zeroes one object allocation large enough for `struct vfs_fsal_obj_handle` plus file-handle storage and points `hdl->handle` at the tail. Handle initialization attaches the sub-FSAL attribute ops.

## State and Persistence Behavior

Persistent state is limited to process memory: export config fields, object handle allocations, and optional debug ACL process state. No on-disk state is written here.

## Dependencies and Integration Points

The file integrates with FSAL config parsing, `vfs_methods.h`, `subfsal.h`, and `attrs.h`. It is compiled into the VFS FSAL path and is the generic counterpart to XFS-specific `subfsal_xfs.c`.

## Risks and Edge Cases

The handle allocation assumes `vfs_file_handle_t` tail storage is sufficient for default VFS handles. Config token drift would change exported FSID behavior. Empty fini/export-op hooks are intentional but can hide future sub-FSAL cleanup requirements.

## Test Signals

Useful tests are config parsing for each `fsid_type` token, export creation with `async_hsm_restore` true/false, handle allocation under leak checking, and getattr/setattr smoke tests through the installed sub-ops.
