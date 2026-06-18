# File Research: sources/os/linux/linux/fs/notify/fsnotify.c

## Role

This file contains the central fsnotify dispatcher and object-deletion hooks. VFS notification helpers eventually call `fsnotify()`, which selects interested marks across inode, parent, mount, superblock, and mount namespace objects and calls the registered backend operations.

## Object Cleanup

The file clears marks for deleted inodes, vfsmounts, mount namespaces, and superblocks. Superblock deletion also unmounts watched inodes, clears sb marks, waits for watched-object counters to drain, and warns if priority watchers remain.

## Parent/Child Handling

`fsnotify_set_children_dentry_flags()` marks children of watched directories with `DCACHE_FSNOTIFY_PARENT_WATCHED`.

`__fsnotify_parent()` is the parent-aware entry path. It fast-exits when no object is watched, decides whether parent/name information is required, takes a name snapshot when needed, and calls `fsnotify()` with both parent and child context.

It also lazily clears stale child dentry flags when a parent no longer watches children.

## Event Dispatch

`fsnotify()` builds an iterator over possible mark lists:

- superblock marks
- vfsmount marks
- inode marks
- parent or second-inode marks
- mount-namespace marks

It first checks aggregate masks to avoid SRCU overhead when no mark can care. When marks exist, it enters SRCU, walks each list, and merges them by group priority/address.

For each selected group, `send_to_group()` combines mark masks and effective ignore masks. It clears ignore masks on modify when appropriate and calls either the backend `handle_event()` or the default inode-event adapter.

## Default Inode Adapter

The default adapter supports backends that only implement `handle_inode_event()`. It handles parent marks before child marks, strips `FS_EVENT_ON_CHILD` for child delivery, suppresses names except for directory-entry events, and applies unlink-exclusion behavior.

## Permission Open Optimization

With fanotify access permissions enabled, `fsnotify_open_perm_and_set_mode()` performs open-time checks for priority watchers and sets file mode bits so later permission/pre-content hooks can skip work when no relevant watcher existed at open time.

## Mount Namespace Events

`fsnotify_mnt()` wraps mount namespace attach/detach events in `struct fsnotify_mnt` and sends them only when the namespace has marks.

## Initialization

`fsnotify_init()` verifies event-bit count, initializes SRCU for mark traversal, and initializes connector caches.

## Design Notes

The core design optimizes the no-watch case aggressively, then uses priority-ordered mark list merging to deliver each group one coherent view of its inode/mount/sb marks and ignore masks.
