# File Research: sources/os/linux/linux-stable/fs/notify/notification.c

## Summary
Implements fsnotify notification queue primitives, overflow handling, queue insertion/removal, event destruction, flushing, and rename cookie generation.

## Main APIs
- `fsnotify_get_cookie()`.
- `fsnotify_insert_event()`.
- `fsnotify_destroy_event()`.
- `fsnotify_peek_first_event()`, `fsnotify_remove_first_event()`, `fsnotify_remove_queued_event()`.
- `fsnotify_flush_notify()`.

## Behavior
Events are queued on a group notification list under `notification_lock`. Backends may supply a merge callback and an insert callback. If the group is shutting down or the queue exceeds `max_events`, the group overflow event is queued once. Successful insertion wakes readers and sends async notification via fasync.

## State and Synchronization
`group->q_len` tracks queue length. Overflow events are per-group and are never freed through normal event destruction. Event destruction checks that the event is not still queued before invoking backend `free_event`.

## Risks
Queue overflow semantics are user-visible. The overflow event must not be double-queued or freed. Permission events may be removed and freed by different CPUs, so the queued-list sanity check uses locking when needed.
