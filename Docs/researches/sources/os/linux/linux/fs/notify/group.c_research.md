# File Research: sources/os/linux/linux/fs/notify/group.c

## Role

This file implements generic fsnotify group allocation, reference counting, shutdown, destruction, and async notification helper support.

A group represents one notification consumer, such as one inotify or fanotify file descriptor.

## Lifetime

`fsnotify_alloc_group()` allocates and initializes a group with:

- refcount 1
- notification queue lock/list/waitqueue
- unlimited default max events
- mark mutex and mark list
- backend ops
- flags

User groups are allocated with accounted GFP.

`fsnotify_get_group()` increments the group refcount. `fsnotify_put_group()` decrements it and calls final destruction when the count reaches zero.

Final destruction calls backend private cleanup, drops memcg, destroys the mark mutex, and frees the group.

## Shutdown And Destruction

`fsnotify_group_stop_queueing()` sets `group->shutdown` under the notification lock so no new events enter the queue.

`fsnotify_destroy_group()` performs full teardown:

1. Stop queueing.
2. Clear all marks by group.
3. Wait for marks pinned by userspace waits.
4. Wait for asynchronous mark destruction.
5. Flush queued notifications.
6. Free the overflow event.
7. Drop the final group reference.

## Async Notification

`fsnotify_fasync()` wires a descriptor into the group fasync list so queue insertion can deliver `SIGIO`.

## Design Notes

Group destruction is deliberately staged around mark refs and SRCU-delayed mark freeing. This prevents backend queues from being flushed while event delivery or permission waits can still hold mark/group references.
