<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/nullfs_methods.h -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/nullfs_methods.h

## Purpose

This header defines NULLFS private module, export, handle, readdir state, and method prototypes. It is the internal contract shared by `main.c`, `export.c`, `handle.c`, `file.c`, and `xattrs.c`.

## Important APIs, Types, and Functions

- `struct null_fsal_module`: embeds `struct fsal_module` plus a reusable `struct fsal_obj_ops handle_ops`.
- `extern struct null_fsal_module NULLFS`: process-global module instance.
- `nullfs_create_export` and `nullfs_update_export`: module export lifecycle entry points.
- `struct nullfs_readdir_state`: carries the upper callback, NULLFS export, and caller directory state while the lower FSAL performs readdir.
- `struct nullfs_fsal_export`: wrapper containing `struct fsal_export`.
- Export handle functions: `nullfs_lookup_path`, `nullfs_create_handle`, and `nullfs_alloc_and_check_handle`.
- `struct nullfs_fsal_obj_handle`: wrapper containing public object handle, lower `sub_handle`, and signed debug-friendly `refcnt`.
- `nullfs_unopenable_type`: classifies sockets, character devices, and block devices as unopenable.
- File, multi-FD, lock, fallocate, and xattr prototypes used by operation-vector initialization.

## Control Flow

The header itself has no executable control flow except the inline `nullfs_unopenable_type`, which returns true for socket, character, or block object types. Its main role is compile-time linkage and type sharing between implementation files.

## State and Persistence Behavior

The types define the persistent runtime wrapper state: each export wraps a lower export, each object wraps a lower object handle, and readdir temporarily stores callback translation state. The header does not allocate or free state.

## Dependencies and Integration Points

It depends on FSAL core types being included before or through implementation files. It references `fsal_up_top`, config error types, FSAL object ops, NFS state, async callbacks, xattr entry types, and I/O hint structures.

## Risks and Edge Cases

- Any change to `struct nullfs_fsal_obj_handle` layout affects implementation code that casts from `struct fsal_obj_handle *`.
- `refcnt` is declared but not meaningfully manipulated in the reviewed implementation; future code should avoid assuming it is authoritative unless lifecycle is completed.
- The prototype set must stay synchronized with operation assignments in `nullfs_handle_ops_init`.

## Test Signals

Compile coverage is the main signal for this header. Runtime tests for every operation-vector assignment indirectly validate that prototypes, wrapper structure layout, and linkage remain consistent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_NULL/nullfs_methods.h -->
