# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/xfs/subfsal_xfs.c

## Purpose

This file supplies the XFS-specific sub-FSAL hooks for FSAL_VFS. Compared with the generic VFS sub-FSAL, it only accepts a no-op export name parameter and allocates standard VFS object handles. The source was read as a complete 85-line file.

## Important APIs, Types, and Functions

Important symbols are `vfs_sub_export_param`, `vfs_sub_fini`, `vfs_sub_init_export_ops`, `vfs_sub_init_export`, `vfs_sub_alloc_handle`, and `vfs_sub_init_handle`.

## Control Flow

Config parsing uses `export_param_block`. Init/fini/export-op hooks are no-ops that return success. Handle allocation mirrors the generic VFS path by allocating `struct vfs_fsal_obj_handle` plus `vfs_file_handle_t` storage and pointing `hdl->handle` at the tail.

## State and Persistence Behavior

Only in-memory object handle allocations and the static config block are owned. XFS persistent behavior is handled by the common VFS code and XFS handle syscall layer.

## Dependencies and Integration Points

It includes FSAL types/API, `vfs_methods.h`, and `subfsal.h`, and is compiled into the `fsalxfs` module. XFS-specific handle behavior lives in `handle_syscalls.c`; this file just supplies sub-FSAL lifecycle glue.

## Risks and Edge Cases

The no-op hooks mean XFS-specific export initialization/cleanup cannot be performed here unless implemented later. Unlike generic VFS, this file does not attach `vfs_subfsal_obj_ops`, so behavior relies on common VFS defaults and XFS syscall functions.

## Test Signals

XFS export creation, handle allocation/free leak tests, and regression coverage that verifies XFS object methods still receive valid `vfs_fsal_obj_handle` storage.
