# File Research: sources/os/linux/linux/fs/smb/client/namespace.c

## Purpose
Implements CIFS automount handling for DFS referrals and SMB junctions, including device-name construction, automount expiry, submount fs-context creation, and namespace inode operations.

## Main Interfaces
- `cifs_build_devname()` builds a `//server/share[/prepath]` source string from a referral target.
- `cifs_d_automount()` is the dentry automount entry point.
- `cifs_release_automount_timer()` cancels the delayed automount expiry worker at module teardown.
- `cifs_namespace_inode_operations` exposes namespace inode operations for automount directories.

## Control Flow
`cifs_d_automount()` calls `cifs_do_automount()`, then adds the new mount to `cifs_automount_list` and schedules expiry. `cifs_do_automount()` rejects root automounts, synchronizes current fs-context passwords from the root session, creates a submount fs context, constructs the automount full path, duplicates the current SMB3 context with current uid/gid/credential ids, parses the new devname, builds `ctx->source`, marks DFS automount state, and calls `fc_mount()`.

## State And Synchronization
Automount expiry is driven by `cifs_automount_task` and `mark_mounts_for_expiry()`. DFS origin paths are read under `tcon->tc_lock`. The session password sync is protected by `ses->session_mutex`.

## Integration Points
Depends on path builders from `dir.c`, SMB3 fs-context parsing/duplication, `cifs_sb_master_tcon()`, DFS origin path state from tcons, and VFS automount/submount APIs.

## Notable Behaviors
- DFS-origin automount paths are reconstructed from `tcon->origin_fullpath` plus the raw dentry path.
- Multiuser automount contexts default uid/gid and cruid to the current caller when unspecified.
- Device names are normalized to slash delimiters and trailing UNC separators are trimmed.

## Risks And Review Focus
- Automount full-path construction must avoid underrunning the allocated path page when prepending origin paths.
- Password synchronization affects retry behavior for DFS submounts.
- Expiry list must be empty before final timer cancellation.
