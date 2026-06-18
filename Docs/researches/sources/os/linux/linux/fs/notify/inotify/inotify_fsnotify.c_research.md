# File Research: sources/os/linux/linux/fs/notify/inotify/inotify_fsnotify.c

## Role

This file implements the inotify backend operations that plug into generic fsnotify. It converts inode events into queued inotify events and frees inotify-specific group/event/mark resources.

## Event Merging

`event_compare()` treats two events as mergeable when mask, watch descriptor, name length, and name match. `FS_IN_IGNORED` events never merge.

`inotify_merge()` compares only the new event with the last queued event, matching historical inotify adjacent-duplicate behavior.

## Event Handling

`inotify_handle_inode_event()` receives a mark-selected fsnotify event, allocates an `inotify_event_info` sized for an optional name, and populates mask, wd, cookie, and name.

Important behavior:

- It skips events racing with mark removal when wd is `-1`.
- Allocation is charged to the monitoring group's memcg, not the target process.
- Allocation failure queues overflow notification.
- `IN_ISDIR` is stripped from `IN_MOVE_SELF` and `IN_DELETE_SELF` for compatibility.
- One-shot marks are destroyed after event handling.

The event is queued through `fsnotify_add_event()` with duplicate merge support.

## Mark And Group Cleanup

When a mark is freed, `inotify_freeing_mark()` queues `IN_IGNORED` and removes the watch descriptor from the idr.

Group private cleanup checks for leaked idr entries, destroys the idr, and decrements the inotify instance ucount.

Event and mark free callbacks release `inotify_event_info` allocations and `inotify_inode_mark` cache entries.

## Design Notes

This file is the narrow translation layer from fsnotify's generic inode events to inotify's watch-descriptor event stream.
