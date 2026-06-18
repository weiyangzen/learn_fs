# File Research: sources/os/linux/linux-stable/fs/notify/fdinfo.c

## Summary
Implements `/proc/<pid>/fdinfo` reporting for inotify and fanotify file descriptors when procfs support is enabled.

## Main APIs
- `inotify_show_fdinfo()`.
- `fanotify_show_fdinfo()`.
- Internal shared `show_fdinfo()` mark iterator.

## Behavior
The code locks the fsnotify group, walks `group->marks_list`, and emits per-mark details. Inotify output reports watch descriptor, inode number, superblock device, user-visible mask, and optionally an export file handle. Fanotify output reports group init flags and event flags, then inode, mount, superblock, or mount-namespace mark details with masks and ignore masks.

## Important Details
File handles are emitted only when `CONFIG_EXPORTFS` can encode the inode. Encoding is done under a shared superblock lock. Fanotify mark flags are converted back to user ABI flags through `fanotify_mark_user_flags()`.

## Risks
This is observability code but still depends on mark connector validity while holding the group lock. Output format is user-visible proc ABI, so field names and ordering should be treated carefully.
