# File Research: sources/os/linux/linux/fs/notify/mark.c

## Role

This file implements fsnotify mark and connector lifetime, locking, attachment, detachment, lookup, destruction, mask recalculation, and superblock watcher accounting.

It is the concurrency core for inotify, fanotify, and other fsnotify users.

## Locking Model

The documented lock order is:

1. `group->mark_mutex`
2. `mark->lock`
3. `mark->connector->lock`

Group mutex protects the group's mark list and private limits. Mark lock protects masks, flags, group/object references. Connector lock protects the watched object's mark list.

Mark lists are protected for lockless dispatch by `fsnotify_mark_srcu`.

## Connectors

A connector is attached to each watched object and holds the ordered hlist of marks. Objects include inode, vfsmount, superblock, and mount namespace.

Inode connectors are additionally tracked on the superblock's inode connector list so unmount can find watched inodes.

Connectors update aggregate object masks and watched-object counters. Inode connectors may hold an inode reference unless all marks are evictable.

## Mask Recalculation

`__fsnotify_recalc_mask()` combines attached mark masks and ignore masks into the object aggregate mask. It also determines whether an inode reference is needed.

`fsnotify_recalc_mask()` updates masks, adjusts inode references, and sets child dentry flags when a directory starts watching children.

## Mark Attachment

`fsnotify_add_mark_locked()` adds a mark to the group list, then inserts it into the object's connector list ordered by group priority and address. Duplicate group marks are rejected unless the group allows duplicates.

Adding the first mark creates a connector with `cmpxchg()` so concurrent attachers converge safely.

## Mark Detachment And Freeing

`fsnotify_detach_mark()` marks a mark detached and removes it from the group list while leaving object-list removal to reference teardown.

`fsnotify_put_mark()` removes the mark from the connector list when refcount reaches zero, detaches/freeing connectors when empty, recalculates masks, queues connectors for SRCU-delayed freeing, and queues marks for delayed destruction.

`fsnotify_free_mark()` marks a mark no longer alive and invokes backend `freeing_mark()`.

## Group/Object Clearing

`fsnotify_clear_marks_by_group()` detaches all marks for a group or all marks of a selected object type.

`fsnotify_destroy_marks()` destroys all marks attached to one object connector and detaches the connector from the object to avoid pinning inodes during teardown.

## Unmount Handling

`fsnotify_unmount_inodes()` repeatedly finds a living watched inode from the superblock connector list, sends `FS_UNMOUNT`, clears its marks, and drops the inode.

## User Wait Support

Permission-event paths can call `fsnotify_prepare_user_wait()` to pin marks safely, drop SRCU while waiting for userspace, then reacquire SRCU with `fsnotify_finish_user_wait()`.

## Design Notes

This file balances fast SRCU read-side dispatch with safe asynchronous destruction. Marks can be removed by group teardown, object teardown, unmount, explicit user action, or refcount drop, and the code is structured to tolerate those paths racing.
