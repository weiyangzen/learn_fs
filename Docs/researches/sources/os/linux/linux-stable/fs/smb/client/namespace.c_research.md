# File Research: sources/os/linux/linux-stable/fs/smb/client/namespace.c

Read status: complete.

## Purpose

Implements CIFS namespace automount support for DFS referrals and SMB junction traversal.

## Main Responsibilities

- Maintain a list of CIFS automounts eligible for expiry.
- Build CIFS device names from referral UNC paths and optional prepaths.
- Construct full automount paths for ordinary and DFS-origin mounts.
- Duplicate and adjust filesystem context for submounts.
- Mount referred targets through `fc_mount()`.
- Register new automounts for expiry scheduling.

## Important Functions

- `cifs_expire_automounts()`
  - Marks CIFS automounts for expiry and reschedules delayed expiry work while the list is nonempty.

- `cifs_release_automount_timer()`
  - Cancels delayed expiry work, warning if automounts still remain.

- `cifs_build_devname()`
  - Normalizes a referral UNC into `//server/share[/prepath]`.
  - Trims leading/trailing delimiters, appends prepath when present, converts delimiters to `/`, and returns an allocated string.

- `is_dfs_mount()`
  - Checks whether the master tcon has an `origin_fullpath`, indicating a DFS-origin mount.

- `automount_fullpath()`
  - Builds the full automount source path from a dentry.
  - For DFS-origin mounts, prepends `tcon->origin_fullpath` to the raw dentry path.

- `fs_context_set_ids()`
  - Sets uid/gid/credential uid defaults from current credentials for multiuser automount contexts.

- `cifs_do_automount()`
  - Synchronizes session passwords, creates a submount fs context, builds the full path, duplicates current context, parses the new devname, derives source, sets DFS automount flags, and mounts.

- `cifs_d_automount()`
  - Public automount entry point.
  - Calls `cifs_do_automount()`, registers expiry, schedules expiry work, and returns the new mount.

- `cifs_namespace_inode_operations`
  - Empty inode operations table used for automount-marked namespace inodes.

## Dependencies

- Uses VFS fs context and submount APIs, CIFS mount context parsing/duplication helpers, session password synchronization, tcon origin paths, dentry path utilities, and mount expiry APIs.

## Notable Behaviors

- Root dentries are rejected as stale automount points.
- Automount context clears pointer-owned fields before duplication to avoid sharing mutable strings from the parent context.
- DFS automount state is propagated through `ctx->dfs_automount` and `ctx->dfs_conn`.
