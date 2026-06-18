# File Research: sources/os/linux/linux/fs/notify/notification.c

## Role

This file implements generic fsnotify notification queue operations and rename-cookie allocation.

Groups such as inotify and fanotify use these helpers to queue, peek, remove, overflow, and flush events.

## Cookies

`fsnotify_get_cookie()` returns an atomic increasing 32-bit cookie used to pair related events such as rename-from and rename-to.

## Event Destruction

`fsnotify_destroy_event()` ignores null and per-group overflow events. For normal events, it warns if the event is still queued and then calls the backend `free_event()` callback.

## Queue Insertion

`fsnotify_insert_event()` is the central queue insertion helper. Under `notification_lock`, it:

- refuses events after group shutdown
- switches to the overflow event if the queue is full or the incoming event is already overflow
- queues the overflow event only once
- optionally merges with existing queued events
- appends the event
- optionally inserts it into a backend merge structure
- wakes readers and sends async SIGIO

Return values distinguish queued, merged, and dropped/overflow/shutdown outcomes.

## Queue Removal And Flush

The file provides helpers to remove a queued event, peek at the first event, remove the first event, and flush all queued notifications during group teardown.

Queue length is maintained with `group->q_len`.

## Design Notes

The queue layer is generic but leaves policy hooks to backends: merging and auxiliary hash insertion are callback-driven, and event memory ownership remains with backend `free_event()`.
