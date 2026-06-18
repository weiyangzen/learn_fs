# File Research: sources/os/linux/linux/fs/notify/fanotify/fanotify_user.c

## Role

This file implements the userspace fanotify interface: `fanotify_init`, `fanotify_mark`, file operations for fanotify descriptors, event formatting for reads, permission-response writes, mark validation, per-user limits, sysctls, and initialization of fanotify caches.

It depends on generic fsnotify queue/mark mechanics and on fanotify event creation/ops provided elsewhere.

## Limits And Sysctls

The file defines defaults for queued events, user groups, user marks, legacy per-group mark limits, and the permission watchdog. With sysctl enabled it registers:

- `fs/fanotify/max_user_groups`
- `fs/fanotify/max_user_marks`
- `fs/fanotify/max_queued_events`
- `fs/fanotify/watchdog_timeout`

Mark limits are estimated from 1% of addressable memory using inode-mark cost.

## Permission Watchdog

Permission groups with pending access decisions may be linked into `perm_group_list`. The delayed watchdog scans `access_list` entries and rate-limits warnings when a receiving pid has not responded for more than the configured timeout.

Group removal unlinks a group so teardown cannot race with watchdog scans.

## Event Read Path

The read path dequeues one event if its computed variable length fits in the user buffer. Event length accounts for metadata plus optional records:

- FID/DFID/DFID_NAME file-handle records
- old/new rename records
- pidfd record
- filesystem error record
- access range record
- mount id record

For path events, privileged listeners may receive a newly opened fd created with `dentry_open_nonotify()`. `FAN_REPORT_FD_ERROR` controls whether fd creation failures are reported as errors or cause legacy-compatible event dropping.

Permission events are not destroyed after copying. They move to `access_list`, carry the generated fd, and wait for a userspace response.

## Permission Response Write Path

`fanotify_write()` accepts `struct fanotify_response` plus optional audit-rule info. It validates response bits, allow/deny semantics, custom errno support for pre-content groups, audit permissions, and response-info layout.

When a matching fd is found in `access_list`, the event is removed, marked answered, and waiters on `access_waitq` are woken.

## File Operations

The fanotify descriptor supports fdinfo display, poll, read, write, release, ioctl, and no-op seek. `FIONREAD` reports queued metadata length only.

Release stops queueing, removes watchdog tracking, auto-allows outstanding permission events, destroys non-permission events, wakes access waiters, and destroys the fsnotify group.

## `fanotify_init`

The syscall validates privilege, class, FID mode, mount-report mode, pidfd/TID exclusion, event fd open flags, audit permissions, and queue-limit flags. It allocates an fsnotify group, sets group priority from fanotify class, stores user namespace and memcg, creates merge hash and overflow event, initializes wait/list heads, and returns an anonymous inode fd.

Unprivileged groups are restricted to limited reporting modes and cannot receive open fds or real pids for other tasks.

## `fanotify_mark`

The mark path validates command, mark type, mask bits, ignore-mask API combinations, group capabilities, permission-event class restrictions, mount-event restrictions, filesystem-error restrictions, evictable mark scope, and FID requirements.

It resolves the target path or fd, checks read permission and LSM `security_path_notify`, validates fsid and exportfs file-handle support for FID groups, checks namespace/filesystem capabilities for mount/sb/mntns marks, and applies special handling for directory flags, non-directory parent-FID reporting, and ignore masks on writable inodes.

Marks are added, removed, or flushed through generic fsnotify mark APIs with fanotify-specific accounting and fsid consistency checks.

## Design Notes

This file is the fanotify policy boundary. The generic fsnotify layer handles queueing and mark lifetime, while this file enforces syscall ABI rules, privilege model, record layout, and userspace-visible compatibility behavior.
