# File Research: sources/os/linux/linux/fs/afs/mntpt.c

## Purpose
Implements AFS mountpoint and autocell automount handling.

## Main Responsibilities
- Exposes mountpoint inode/file operations that reject direct lookup/open with `-EREMOTE`.
- Parses mountpoint symlink content or pseudo-directory names into a submount `fs_context`.
- Creates automounted AFS submounts and manages their expiry list/timer.
- Handles autocell pseudo directories by mapping the dentry name to `root.cell`.

## Key Functions and Data
- `afs_mntpt_set_params()` fills an AFS submount context from a mountpoint dentry.
- `afs_mntpt_do_automount()` creates an `fs_context` for a submount and mounts it.
- `afs_d_automount()` is the dentry automount hook used by dynroot and mountpoint dentries.
- `afs_mntpt_expiry_timed_out()` marks tracked mounts for expiry and reschedules if needed.
- `afs_mntpt_kill_timer()` cancels the expiry timer during cleanup.

## Important Details
- Pseudo-directory autocell mounts use the dentry name as the cell name and mount `root.cell`.
- Dotted autocell names force read/write volume type.
- Regular AFS mountpoints are encoded as special symlink content ending in `.`.
- Backup-volume mountpoints cannot recursively cross to another backup volume.
