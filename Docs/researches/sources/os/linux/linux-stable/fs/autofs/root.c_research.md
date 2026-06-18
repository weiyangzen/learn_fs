# File Research: sources/os/linux/linux-stable/fs/autofs/root.c

## Purpose
Implements autofs dentry operations, directory inode operations, root ioctls, lookup behavior, and daemon-controlled namespace mutation.

## Main Interfaces
- Dentry ops: `autofs_d_automount()`, `autofs_d_manage()`, `autofs_dentry_release()`.
- Directory ops: `autofs_lookup()`, `autofs_dir_permission()`, `autofs_dir_symlink()`, `autofs_dir_unlink()`, `autofs_dir_mkdir()`, `autofs_dir_rmdir()`.
- Root ioctl dispatcher: `autofs_root_ioctl()` and compat wrapper.
- Exported helper: `is_autofs_dentry()`.

## Important Behavior
Non-daemon path walks trigger or wait for mounts through `autofs_wait()`. The owner daemon, detected by `autofs_oz_mode()`, can operate on the raw namespace without triggering mounts. `autofs_d_manage()` decides whether path walk should proceed, trigger automount, or stop with `-EISDIR` for already-satisfied rootless multi-mount/symlink cases.

`autofs_lookup()` reuses unhashed active dentries when possible, creates per-dentry `autofs_info`, and marks root children as automount triggers for indirect mounts. Directory creation and symlink creation are daemon-only namespace operations that turn active dentries into persistent dentries. Unlink/rmdir do not simply delete; they drop dentries and place them on the expiring list so walkers racing expiry can wait and retry.

Legacy root ioctls implement ready/fail, catatonic mode, protocol queries, timeout get/set, ask-umount, single expire, and multi-expire.

## State And Synchronization
Uses `lookup_lock` for active/expiring lists and dentry list manipulation, `fs_lock` for pending/expiring flags and requester state, and dentry locks for managed-flag updates. RCU walk paths return `-ECHILD` when blocking is required.

## Risks / Review Notes
Path-walk behavior is subtle because autofs dentries are both filesystem objects and mount triggers. The code must avoid false `ELOOP`, handle stale dentries after daemon replacement, and preserve expiring dentries long enough for waiters to resolve races.
