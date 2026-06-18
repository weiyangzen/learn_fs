# File Research: sources/os/linux/linux/fs/notify/inotify/inotify_user.c

## Role

This file implements inotify userspace syscalls, descriptor file operations, watch descriptor idr management, per-user limits, sysctls, and initialization.

## Sysctls And Limits

It registers `fs/inotify` sysctls for:

- `max_user_instances`
- `max_user_watches`
- `max_queued_events`

At init, max watches are calculated from 1% of addressable memory using an estimated watch cost and clamped to `[8192, 1048576]`. Default queued events are 16384 and default instances are 128.

## File Operations

The inotify fd supports fdinfo, poll, read, fasync, release, ioctl, and no-op seek.

`inotify_poll()` reports readable state when the notification queue is non-empty.

`inotify_read()` waits unless nonblocking, removes queued events one at a time, copies `struct inotify_event` plus padded names to userspace, and destroys events after copying.

`FIONREAD` sums the exact bytes currently queued. With checkpoint/restore enabled, `INOTIFY_IOC_SETNEXTWD` adjusts the idr cursor.

Release destroys the fsnotify group.

## Path And Permission Checks

`inotify_add_watch()` validates mask bits, fd type, `IN_MASK_ADD`/`IN_MASK_CREATE` incompatibility, path lookup flags, read permission, and LSM notification permission before updating marks.

## Watch Descriptor Management

Each group has an idr protected by `idr_lock`.

New marks are allocated from `inotify_inode_mark_cachep`, initialized, assigned cyclic watch descriptors, charged to user watch ucounts, and attached as inode marks.

Existing marks can be replaced or extended. Mask/flag changes recalculate the inode fsnotify mask only when needed.

Removal finds a wd, destroys the fsnotify mark, and drops the lookup reference.

When a mark is ignored/freed, the code queues `IN_IGNORED`, removes it from idr, and decrements user watch count.

## Syscalls

Implemented syscalls are:

- `inotify_init1`
- `inotify_init`
- `inotify_add_watch`
- `inotify_rm_watch`

`inotify_init1()` validates flags against `IN_CLOEXEC` and `IN_NONBLOCK`, allocates a group with an overflow event, charges an instance ucount, and returns an anonymous inode fd.

## Initialization

`inotify_user_setup()` verifies bit layout compatibility between inotify and fsnotify constants, creates the mark cache, sets defaults, and registers sysctls.

## Design Notes

The file preserves inotify's watch-descriptor ABI while delegating event delivery, queueing, and mark lifetime to fsnotify.
