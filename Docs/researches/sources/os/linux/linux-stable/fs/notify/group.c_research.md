# File Research: sources/os/linux/linux-stable/fs/notify/group.c

## Summary
Implements fsnotify group allocation, teardown, reference counting, queue shutdown, and fasync helper support.

## Main APIs
- `fsnotify_alloc_group()`.
- `fsnotify_destroy_group()`.
- `fsnotify_group_stop_queueing()`.
- `fsnotify_get_group()`, `fsnotify_put_group()`.
- `fsnotify_fasync()`.

## Behavior
A group owns a notification queue, mark list, mark mutex, wait queue, optional overflow event, private backend state, memcg reference, and refcount. Destruction stops queueing, clears all marks, waits for user-wait-pinned marks, waits for deferred mark destruction, flushes notifications, frees the overflow event, and drops the group reference.

## State and Synchronization
`notification_lock` protects queue shutdown and queue state. `mark_mutex` protects `marks_list` and group-private mark state. Refcount finalization calls backend `free_group_priv`, releases memcg, destroys the mutex, and frees the group.

## Risks
Group teardown ordering matters because fanotify permission events can pin marks while waiting for userspace. Queue shutdown must happen before final flush so no new events appear after cleanup starts.
