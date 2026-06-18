# File Research: sources/os/linux/linux-stable/fs/notify/mark.c

## Summary
Core fsnotify mark and connector lifetime implementation. It manages mark attachment, detachment, refcounts, connector allocation, object masks, inode pinning, watched-object accounting, SRCU-safe traversal, and deferred destruction.

## Main APIs
- Ref/lifetime: `fsnotify_get_mark()`, `fsnotify_put_mark()`, `fsnotify_free_mark()`, `fsnotify_destroy_mark()`.
- Add/find/clear: `fsnotify_add_mark_locked()`, `fsnotify_add_mark()`, `fsnotify_find_mark()`, `fsnotify_clear_marks_by_group()`, `fsnotify_destroy_marks()`.
- Permission wait support: `fsnotify_prepare_user_wait()`, `fsnotify_finish_user_wait()`.
- Superblock unmount support: `fsnotify_unmount_inodes()`.
- Init: `fsnotify_init_mark()`, `fsnotify_init_connector_caches()`.

## Behavior
Marks are attached to per-object connectors for inodes, mounts, superblocks, or mount namespaces. Connector lists are sorted by group priority and address so dispatch can merge mark lists by group. Recalculation updates aggregate object masks and manages inode references when any attached mark requires the inode to be pinned. Detachment removes the mark from the group list first, then leaves object-list removal to the final put path.

## State and Synchronization
Required lock ordering is `group->mark_mutex`, then `mark->lock`, then `connector->lock`. Object-list traversal is protected by `fsnotify_mark_srcu`. Mark and connector freeing is deferred through workqueues after SRCU grace periods. Superblocks track watched-object counters by priority to support teardown and permission fast paths.

## Risks
This is the most sensitive lifetime file in the fsnotify stack. Races among group destruction, object teardown, permission waits, and lockless event dispatch are handled by mark refs, group user-wait counters, SRCU, and deferred freeing. Any change to detach ordering, connector mask recalculation, or inode reference rules risks use-after-free, leaked inode pins, missed events, or unmount hangs.
