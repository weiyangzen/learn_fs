# File Research: sources/os/linux/linux-stable/fs/notify/fanotify/fanotify_user.c

## Summary
Implements the userspace fanotify API: `fanotify_init`, `fanotify_mark`, fanotify fd operations, event formatting, permission-event response handling, mark accounting, sysctl limits, and init-time cache setup.

## Main APIs
- Syscalls: `fanotify_init`, `fanotify_mark`, compat/split-arg variants.
- File operations: `fanotify_read()`, `fanotify_write()`, `fanotify_poll()`, `fanotify_ioctl()`, `fanotify_release()`.
- Mark operations: add, remove, flush, fsid/fid validation, mark flag updates, error-event pool initialization.
- Event copy helpers for metadata, FID/DFID/name records, pidfd records, error records, range records, and mount-id records.
- Permission machinery: response validation, access list handling, wait wakeups, and timeout watchdog warnings.

## Behavior
`fanotify_init` validates privilege, class, FID/name/pidfd/mount-reporting combinations, event fd flags, queue limits, audit capability, and creates an anon inode backed by an fsnotify group. `fanotify_mark` resolves the target object, validates mark type and event mask, enforces namespace capabilities and LSM checks, verifies filesystem fid/fsid support when required, and adds/removes/flushes fsnotify marks. Reads dequeue one event at a time, copy ABI metadata and info records, install event fds/pidfds, and move permission events to an access-list until userspace writes a response.

## State and Synchronization
The notification queue and permission access-list are protected by `group->notification_lock`. Group mark changes use fsnotify group locking. User limits are enforced with `ucounts`; event memory is charged to the creator memcg. Permission groups can be linked into a global watchdog list protected by `perm_group_lock`. Error events use a per-group mempool initialized only when `FAN_FS_ERROR` is requested.

## Risks
This file is fanotify’s ABI choke point. Flag validation is intentionally strict: mount namespace events cannot mix with inode fid/fd modes, permission events require the right class, and rename reporting requires names. Permission-event cleanup must always wake waiters and avoid leaving access-list events unanswered. FID mode depends on stable filesystem export operations and fsid rules, especially weak fsids and btrfs subvolume checks.
