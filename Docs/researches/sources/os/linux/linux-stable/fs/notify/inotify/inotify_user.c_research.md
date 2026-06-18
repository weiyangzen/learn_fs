# File Research: sources/os/linux/linux-stable/fs/notify/inotify/inotify_user.c

## Summary
Implements userspace inotify syscalls, anon inode file operations, watch descriptor IDR management, per-user limits, sysctls, and init-time cache setup.

## Main APIs
- Syscalls: `inotify_init`, `inotify_init1`, `inotify_add_watch`, `inotify_rm_watch`.
- File operations: read, poll, ioctl, release, fasync.
- Watch management: new watch, existing watch update, IDR add/find/remove, ignored-event cleanup.
- Init: `inotify_user_setup()`.

## Behavior
`inotify_init*` creates an fsnotify group with a preallocated overflow event and per-user instance accounting. `inotify_add_watch` validates mask bits, resolves the path, checks read permission and `security_path_notify()`, then creates or updates an inode mark. Reads dequeue events, copy `struct inotify_event` plus padded name bytes to userspace, and destroy each event after copying. `inotify_rm_watch` finds the mark by watch descriptor and destroys it.

## State and Synchronization
The group IDR maps watch descriptors to `inotify_inode_mark` objects and is protected by `idr_lock`. Group mark updates use `fsnotify_group_lock()`. Watch and instance limits use ucounts. Queue reads use `notification_lock` and `notification_waitq`.

## Risks
IDR and mark refcounts are tightly coupled: removing a descriptor drops the IDR-held mark reference and sets `wd = -1`. `IN_MASK_ADD` and `IN_MASK_CREATE` are mutually exclusive. Existing watch replacement must recalculate inode masks when bits are dropped or newly added.
