# File Research: sources/os/linux/linux-stable/fs/afs/mntpt.c

## Summary
Implements AFS mountpoint automount behavior. AFS mountpoints are represented as special symlinks or dynamic-root pseudo directories; this file converts them into submount filesystem contexts and manages expiry of resulting vfsmounts.

## Main Responsibilities
- Defines mountpoint inode and file operation tables.
- Rejects normal lookup/open on mountpoint placeholder directories.
- Parses mount parameters from pseudo-directory names or special symlink contents.
- Creates submounts through `fs_context_for_submount()` and `fc_mount()`.
- Tracks automounted vfsmounts for periodic expiry.
- Cancels the mountpoint expiry timer during shutdown.

## Key APIs
- `afs_d_automount()`.
- `afs_mntpt_inode_operations`.
- `afs_autocell_inode_operations`.
- `afs_mntpt_file_operations`.
- `afs_mntpt_kill_timer()`.

## Important Behavior
For dynamic-root pseudo directories, the dentry name selects the cell; a leading dot forces read/write volume mounting. The target volume is `root.cell`.

For real AFS mountpoint symlinks, the symlink content must end in `.` and is parsed as the submount source. The current source cell is inherited when present. Backup-volume mountpoints cannot cross into another backup volume.

Automounted mounts are placed on `afs_vfsmounts`, marked for expiry after 10 minutes, and the expiry worker reschedules while the list remains nonempty.

## State and Synchronization
The expiry list is a static global `LIST_HEAD`, with delayed work queued on `afs_wq`. Mount context setup may replace `fc->net_ns` with the source superblock's network namespace.

## Risks
Mountpoint parsing is intentionally strict about symlink size and trailing dot. The dynamic-root path depends on pseudo-directory flags from inode setup. Shutdown asserts the vfsmount expiry list is empty before cancelling delayed work.
