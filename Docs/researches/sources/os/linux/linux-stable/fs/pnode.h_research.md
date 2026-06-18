# File Research: sources/os/linux/linux-stable/fs/pnode.h

## Purpose

Declares mount propagation helpers, propagation state macros, clone flags, and cross-file VFS mount helper prototypes used by `pnode.c` and mount code.

## Main Contents

- Propagation state macros:
  - `IS_MNT_SHARED()`, `IS_MNT_SLAVE()`, `IS_MNT_NEW()`, `IS_MNT_UNBINDABLE()`.
  - `CLEAR_MNT_SHARED()`, `IS_MNT_MARKED()`, `SET_MNT_MARK()`, `CLEAR_MNT_MARK()`.
  - `IS_MNT_LOCKED()`.
- Clone/propagation flags:
  - `CL_EXPIRE`, `CL_SLAVE`, `CL_COPY_UNBINDABLE`, `CL_MAKE_SHARED`, `CL_PRIVATE`, `CL_COPY_MNT_NS_FILE`.
- Inline helpers:
  - `set_mnt_shared()` clears shared mask bits and sets `T_SHARED`.
  - `peers()` compares nonzero mount group ids.
- Declares propagation API:
  - `change_mnt_propagation()`, `bulk_make_private()`, `propagate_mnt()`, `propagate_umount()`.
  - `propagate_mount_busy()`, `propagate_mount_unlock()`, `propagation_would_overmount()`.
- Declares supporting mount helpers from other VFS files:
  - `mnt_release_group_id()`, `mnt_get_count()`, `mnt_set_mountpoint()`, `mnt_change_mountpoint()`, `copy_tree()`, `is_path_reachable()`, `count_mounts()`.

## Notes

This header is tightly coupled to internal `struct mount` fields and is not a public API. It encodes the state bits and traversal predicates that `pnode.c` depends on.
