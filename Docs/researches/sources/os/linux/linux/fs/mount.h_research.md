# File Research: sources/os/linux/linux/fs/mount.h

## Purpose
Private VFS mount header defining internal mount namespace, mount, mountpoint, and helper APIs used by mount and path-walk code.

## Main Responsibilities
- Define `struct mnt_namespace`, `struct mount`, `struct mountpoint`, and per-CPU mount counters.
- Provide internal mount propagation and namespace flags.
- Provide helpers for converting public `vfsmount` to private `mount`.
- Provide helpers for mountpoint detection, namespace attachment, namespace RB-tree removal, fsnotify mount notifications, overmount traversal, and writer-hold flag manipulation.

## Key Structures
- `struct mnt_namespace`
  - Contains namespace identity, root mount, RB-tree of mounts, user namespace, ucounts, poll waitqueue, sequence/event counters, visible mounts, mount counts, passive refcount, and anonymous namespace flag.
- `struct mount`
  - Wraps public `struct vfsmount`.
  - Tracks parent, mountpoint, namespace linkage, child mounts, superblock mount list linkage, propagation lists, expiry, pins, visible namespace linkage, overmount, mount IDs, group ID, flags, and optional fsnotify marks.
- `struct mountpoint`
  - Hash entry for a dentry used as a mountpoint and list of mounts at that point.
- `struct mnt_pcp`
  - Per-CPU mount reference and writer counters on SMP.

## Key Helpers
- `real_mount()` converts `struct vfsmount *` to containing `struct mount *`.
- `mnt_has_parent()` tests whether a mount is not its own parent.
- `is_mounted()` checks whether a mount is attached to a real namespace.
- `__path_is_mountpoint()` tests whether a path has a child mount not undergoing sync unmount.
- `detach_mounts()` calls `__detach_mounts()` only when the dentry is a mountpoint.
- `get_mnt_ns()` increments namespace reference.
- `is_local_mountpoint()` tests local mountpoint state.
- `is_anon_ns()` and `anon_ns_root()` classify anonymous mount namespaces.
- `mnt_ns_attached()` and `mnt_ns_empty()` inspect namespace RB-tree membership.
- `move_from_ns()` removes a mount from its namespace RB-tree and visible list.
- `to_mnt_ns()` converts `ns_common` to `mnt_namespace`.
- `mnt_notify_add()` queues fsnotify namespace transition notification when needed.
- `topmost_overmount()` follows `overmount` pointers.
- `test_write_hold()`, `set_write_hold()`, `clear_write_hold()` use the low bit of `mnt_pprev_for_sb` as `WRITE_HOLD`.

## Important Behaviors and Edge Cases
- `MNT_NS_INTERNAL` is a sentinel error pointer distinct from valid namespaces.
- `move_from_ns()` updates cached first/last RB-tree nodes before erasing.
- `mnt_ns` can be observed locklessly under RCU but is normally protected by `namespace_sem`.
- `mnt_pprev_for_sb` steals its low bit for write-hold state, requiring alignment assumptions.
- Fsnotify fields and helpers compile differently under `CONFIG_FSNOTIFY`.

## Dependencies
- Public mount structures from `linux/mount.h`.
- RB-tree, hlist, list, RCU, namespace, fsnotify, and seqlock infrastructure.
- External mount code provides functions declared here, such as `__lookup_mnt()`, `__legitimize_mnt()`, `__detach_mounts()`, and `mnt_ns_from_dentry()`.

## Research Notes
This header exposes the private shape of Linux mount state that `fs/namei.c` depends on for crossing mountpoints, following `..` across mount roots, and enforcing `LOOKUP_NO_XDEV`.
