# File Research: sources/os/linux/linux-stable/fs/notify/inotify/inotify_fsnotify.c

## Summary
Inotify backend implementation for fsnotify event delivery, event merging, backend cleanup, and mark/event freeing.

## Main APIs
- `inotify_handle_inode_event()`.
- `inotify_fsnotify_ops`.
- Internal queue merge and cleanup callbacks.

## Behavior
On an interested inode event, the backend allocates an `inotify_event_info`, copies the watch descriptor, mask, cookie, and optional name, and queues it to the group. Adjacent duplicate events are merged when mask, watch descriptor, name length, and name match, except `IN_IGNORED`. One-shot marks are destroyed after event delivery.

## State and Synchronization
The watch descriptor is read with `READ_ONCE()` because mark destruction can race with event handling. Allocations are charged to the listener group memcg rather than the event-generating task. Group private cleanup destroys the IDR and decrements the inotify instance ucount.

## Risks
A mark with `wd == -1` must not generate user events. Allocation failure is converted to queue overflow so userspace can detect loss. `IN_MOVE_SELF` and `IN_DELETE_SELF` deliberately suppress `IN_ISDIR` for compatibility.
