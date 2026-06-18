# File Research: sources/os/linux/linux-stable/fs/notify/inotify/inotify.h

## Summary
Internal inotify header defining event and mark structures plus shared helpers and backend declarations.

## Main Types
- `struct inotify_event_info`: queued event with mask, watch descriptor, rename cookie, and optional name.
- `struct inotify_inode_mark`: fsnotify mark extension carrying the watch descriptor.

## Important Details
`INOTIFY_USER_MASK` limits user-visible watch/event bits to `IN_ALL_EVENTS`. `inotify_mark_user_mask()` reconstructs user-visible flags such as `IN_EXCL_UNLINK` and `IN_ONESHOT`. The header declares the fsnotify ops table, mark cache, event handler, and IDR cleanup helper.

## Risks
Inotify relies on bit layout compatibility between `IN_*` and `FS_*` constants, checked in `inotify_user.c`. Watch descriptor lifetime depends on keeping the IDR and mark refcounts aligned.
