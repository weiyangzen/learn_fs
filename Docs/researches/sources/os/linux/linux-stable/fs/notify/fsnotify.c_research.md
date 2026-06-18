# File Research: sources/os/linux/linux-stable/fs/notify/fsnotify.c

## Summary
Core fsnotify dispatcher and object cleanup implementation. It routes VFS events to interested fsnotify groups across inode, parent, mount, superblock, and mount-namespace marks.

## Main APIs
- Object cleanup: `__fsnotify_inode_delete()`, `__fsnotify_vfsmount_delete()`, `__fsnotify_mntns_delete()`, `fsnotify_sb_delete()`, `fsnotify_sb_free()`.
- Parent/name routing: `fsnotify_set_children_dentry_flags()`, `__fsnotify_parent()`.
- Main dispatcher: `fsnotify()`.
- Permission optimization: `fsnotify_open_perm_and_set_mode()`.
- Mount namespace events: `fsnotify_mnt()`.
- Init: `fsnotify_init()`.

## Behavior
The dispatcher first uses aggregate object masks to avoid SRCU traversal when no mark can match. When marks exist, it builds a multi-head iterator over all relevant mark lists, selects one group at a time by priority, applies ignore masks, and invokes either the group `handle_event` callback or inode-event fallback. Parent/name info is included when a parent watches children or when inode/sb/mount marks require parent/name reporting.

## State and Synchronization
Mark list traversal is protected by `fsnotify_mark_srcu`. Dentry child interest is cached in `DCACHE_FSNOTIFY_PARENT_WATCHED` and cleared lazily. Superblock teardown clears marks, sends unmount notifications, and waits for watched-object counters to drain. Permission-open optimization stores nonotify mode bits in the opened file based on current watcher masks.

## Risks
The mark iterator’s priority and grouping rules are central to fanotify permission ordering and ignore-mask semantics. Parent/name reporting has security-sensitive filtering for special files. Permission events may abort further delivery when a high-priority listener denies access, so ordering and return handling must remain exact.
