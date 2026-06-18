# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/dev/sdev_vnops.c

This file implements the base vnode operations for the illumos `/dev` filesystem (`sdev`). It is the main behavioral layer for synthetic `/dev` nodes, persistent backing-store nodes, non-global-zone device profiles, and dynamic-directory dispatch.

Core responsibilities:
- Defines `sdev_vnodeops_tbl`, the primary VOP table for `/dev`.
- Handles VDIR, VCHR, VBLK, VLNK, VREG, and VDOOR-style `/dev` entries, with regular-file operations delegated to the backing vnode.
- Maintains the `sdev_node_t` lifecycle rules described in the large file header: `SDEV_INIT`, `SDEV_READY`, and `SDEV_ZOMBIE`.
- Coordinates in-memory `sdev_node_t` entries with optional persistent backing-store vnodes in `sdev_attrvp`.
- Routes non-global-zone operations through profile helpers such as `prof_lookup()` and `prof_filldir()`.
- Routes global-zone lookup and directory enumeration through `devname_lookup_func()` and `devname_readdir_func()`.

Important operations:
- `sdev_open`, `sdev_close`, `sdev_read`, `sdev_write`, and `sdev_ioctl` only support global-zone regular files, delegating to `sdev_attrvp`. Directories are special-cased, and links or unsupported types fail.
- `sdev_getattr` reads attributes from the persistent backing vnode if present, otherwise from the in-memory `sdev_attr`, then merges sdev-specific fields.
- `sdev_setattr` delegates to `devname_setattr_func()`.
- `sdev_getsecattr` and `sdev_setsecattr` support ACL/security attributes, fabricating ACLs for memory-only nodes when possible and creating a shadow node when persistence is required.
- `sdev_access` uses `sdev_self_access`; memory-only access is checked by `sdev_unlocked_access`, while persisted nodes defer to the backing vnode.
- `sdev_lookup` checks execute permission and dispatches either to the zone profile lookup path or global `devname_lookup_func`.
- `sdev_create`, `sdev_mkdir`, and `sdev_symlink` create new in-memory nodes, optionally backed by persistent storage, then unblock waiters on `SDEV_LOOKUP`.
- `sdev_remove`, `sdev_rmdir`, and `sdev_rename` remove nodes from the in-memory cache and perform best-effort cleanup of backing-store entries.
- `sdev_readdir` expects the caller to hold the node contents lock through `sdev_rwlock`; it fills profile directories for non-global zones and otherwise delegates to `devname_readdir_func`.
- `sdev_inactive` delegates final cleanup to `devname_inactive_func`.
- `sdev_fid` exposes `sdev_ino` through an NFS-style fid.
- `sdev_pathconf` reports the ACL flavor via `_PC_ACL_ENABLED`.

Locking and lifecycle model:
- Directory contents are protected by each node’s `sdev_contents` rwlock.
- The file header documents the core ordering: parent before child; vnode `v_lock` before `sdev_contents` when both are needed.
- Removal is two-phase: unlink from the directory cache and mark zombie without changing vnode references; final destruction is left to inactive handling.
- Several operations check parent zombie state by locking the parent’s parent before proceeding.

Research notes:
- This is the authoritative behavioral contract for `/dev` persistence and dynamic-node semantics.
- Dynamic-node directories are expected to override selected VOPs while sharing this common base table.
- Non-global-zone `/dev` is intentionally constrained; create/remove-like operations mostly redirect to profile lookup or return `ENOTSUP`.
- Backing-store operations are best effort in removal/rename paths, with some errors intentionally suppressed to preserve `/dev` semantics.
