# File Research: sources/os/linux/linux/fs/autofs/root.c

## Summary
Implements autofs root/directory file operations, dentry operations, lookup, automount triggering, daemon-visible directory manipulation, and legacy root ioctls.

## Main Responsibilities
- Provide autofs root and directory `file_operations`.
- Provide autofs directory `inode_operations`.
- Provide dentry `d_automount`, `d_manage`, and `d_release`.
- Create active autofs dentries during lookup and reuse unhashed active dentries.
- Trigger daemon mount requests during path walk.
- Wait for pending expires and pending mounts.
- Allow daemon-only mkdir/symlink/unlink/rmdir operations.
- Support root-directory ioctls for wait release, protocol queries, timeout, askumount, and expire.

## Key APIs
- `autofs_d_automount()`, `autofs_d_manage()`.
- `autofs_lookup()`.
- `autofs_dir_mkdir()`, `autofs_dir_symlink()`, `autofs_dir_unlink()`, `autofs_dir_rmdir()`.
- `autofs_root_ioctl()`, `autofs_root_compat_ioctl()`.
- `is_autofs_dentry()`.

## Important Behavior
The automount daemon never triggers mounts; oz-mode path walks see the raw autofs filesystem. Non-daemon writers are denied by `autofs_dir_permission()`.

`autofs_d_automount()` waits for pending expires, sets `AUTOFS_INF_PENDING` when it must call the daemon, waits for `NFY_MOUNT`, then detects whether userspace replaced the dentry.

`autofs_d_manage()` can return `-EISDIR` to tell VFS that a managed dentry is not a mount trap after all, avoiding needless automount recursion for symlinks and non-empty directories.

Lookup creates `autofs_info`, attaches it to the dentry, and adds it to the active list. Root entries in indirect mounts are marked managed mount triggers.

Daemon unlink/rmdir uses `d_drop()` plus the expiring list rather than ordinary negative-dentry deletion, so path walkers can detect incomplete expiry and wait.

## Risks
The path-walk hooks are race-sensitive around RCU walk, expiring dentries, stale indirect mount dentries, rootless multi-mounts, and daemon replacement of directories with symlinks. Active/expiring list cleanup in `d_release` must match lookup and expire behavior.
