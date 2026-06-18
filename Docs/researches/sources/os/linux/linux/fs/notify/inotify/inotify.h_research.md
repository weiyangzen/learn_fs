# File Research: sources/os/linux/linux/fs/notify/inotify/inotify.h

## Role

This private inotify header defines inotify event and mark structures, user-mask conversion helpers, and cross-file declarations.

## Data Structures

`struct inotify_event_info` wraps a generic fsnotify event with:

- inotify mask
- watch descriptor
- rename sync cookie
- optional name length and name bytes

`struct inotify_inode_mark` wraps a generic fsnotify mark with the inotify watch descriptor.

## Mask Helpers

`INOTIFY_USER_MASK` limits userspace-visible bits to `IN_ALL_EVENTS`.

`inotify_mark_user_mask()` converts an internal fsnotify mark back to userspace bits and adds `IN_EXCL_UNLINK` or `IN_ONESHOT` based on internal mark flags.

## Declarations

The header declares:

- `inotify_ignored_and_remove_idr()`
- `inotify_handle_inode_event()`
- `inotify_fsnotify_ops`
- `inotify_inode_mark_cachep`

With `CONFIG_INOTIFY_USER`, it also provides ucounts helpers for instances and watches.

## Design Notes

The file keeps inotify's public watch-descriptor model separate from generic fsnotify mark mechanics.
