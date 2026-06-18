# File Research: sources/os/linux/linux-stable/fs/mount.h

## Purpose

Defines internal VFS mount and mount-namespace structures plus helper routines shared by mount and pathname-walking code.

## API Surface

- `struct mnt_namespace`: namespace root, mount rbtree, user namespace, poll/event state, fsnotify marks, mount counts, and anonymous namespace state.
- `struct mount`: internal wrapper around `vfsmount`, including parent/child topology, namespace membership, propagation lists, per-superblock linkage, refcounts/writer counts, mountpoint state, fsnotify state, IDs, pins, and overmount pointer.
- `struct mountpoint`: hash/list node for dentries used as mountpoints.
- Helpers include `real_mount()`, `mnt_has_parent()`, `is_mounted()`, `detach_mounts()`, mount lock guards, namespace rbtree helpers, fsnotify queueing, `topmost_overmount()`, and write-hold flag manipulation.

## Control Flow And State

Mount namespaces keep mounts in an rbtree with cached first/last nodes and maintain passive references separate from active mount pins. Mounts maintain both tree topology and namespace membership, plus shared/slave propagation lists. The header exposes mount traversal and lookup hooks used by `fs/namei.c` when crossing mountpoints or following `..`.

The per-superblock previous pointer steals the low bit for `WRITE_HOLD`, with helpers to test, set, and clear that state. Several helpers are intended for use under `namespace_sem`, `mount_lock`, RCU, or fsnotify-specific conditions.

## Dependencies

Depends on Linux mount, namespace, seq_file, poll, fs_pin, fsnotify, rbtree, hlist/list, seqlock, and internal VFS mount functions implemented elsewhere.

## Risks

This is private infrastructure with tight locking and lifetime rules. Misusing RCU-visible namespace pointers, rbtree membership checks, or the low-bit write-hold encoding can corrupt mount topology or writer accounting. Path walking depends on these helpers accurately distinguishing detached, internal, mounted, and anonymous namespace states.
