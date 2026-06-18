# sources/user-network-fs/samba/source3/smbd/close.c

## Purpose
`close.c` is the main SMB file-handle teardown implementation. It closes normal files, directories, alternate streams, fake files, print files, and non-FSA/path reference handles while coordinating share-mode removal, oplock release, durable disconnects, pending AIO, delete-on-close, write-time updates, magic scripts, change notifications, and recursive deletion of veto-hidden directory contents.

## Important APIs, types, and functions
- `delete_all_streams()` enumerates named streams with `vfs_fstreaminfo()` and unlinks all non-default streams relative to a directory FSP.
- `has_other_nonposix_opens()`, `has_nonposix_opens()`, and `has_delete_opens()` inspect share-mode entries for delete-on-close decisions and open-conflict reporting.
- `close_share_mode_lock_prepare()` and `close_share_mode_lock_cleanup()` are callbacks around `share_mode_entry_prepare_lock_del()`/unlock that decide whether deletion must happen while holding the global share lock.
- `close_remove_share_mode()` handles normal file share-mode teardown and delete-on-close file unlinking.
- `close_normal_file()` handles durable disconnect, pending SMB1 lock cleanup, write-time update, fd close, and magic-script execution.
- `recursive_rmdir_fsp()`, `rmdir_internals()`, and `close_directory()` implement directory close and delete-on-close directory removal.
- `close_file_smb()`, `close_file_free()`, and `msg_close_file()` are the public close dispatch and messaging entry points.

## Control flow
For normal files, `close_normal_file()` first refuses unsafe close with outstanding AIO except controlled shutdown cleanup, completes any blocked SMB1 locks, and attempts a durable disconnect only for shutdown closes on durable opens. Durable success updates the open database and schedules the scavenger instead of doing a full close. Otherwise it clears durable state, sends directory-lease break notifications for modified files, removes share modes, applies SMB1 explicit close write time, closes the fd, optionally runs a magic script, and returns the first meaningful status.

Delete-on-close is decided under the share-mode lock. If this is the last relevant non-POSIX open and the close is normal or shutdown, the close path retrieves the security tokens associated with the delete disposition, temporarily becomes that user if needed, validates that the pathname still names the same file ID, deletes streams, removes kernel share modes, unlinks the file or directory, resets delete-on-close, unlocks share modes, and sends remove notifications. Directory deletion first tries `unlinkat(..., AT_REMOVEDIR)`, then, if configured, verifies that only veto/invisible entries remain and recursively removes them before retrying.

## State and persistence behavior
Persistent filesystem state changes include unlinking files/directories/streams, chmod/execution of magic scripts, write-time updates, and possible spool file finalization. Shared open state is removed or marked disconnected in share-mode and `smbXsrv_open` databases. In-memory state on `files_struct` is cleared through `fd_close()`, `file_free()`, alternate-stream base FSP cleanup, and `fsp_unbind_smb()`. Delete-on-close token state and parent lease keys are read from share-mode records.

## Dependencies and integration points
The file integrates tightly with locking/share-mode code, durable handle VFS hooks, SMBX open records, scavenger scheduling, byte-range lock cleanup from `blocking.c`, stream VFS, notification, leases, pathref helpers, security tokens, print spool, fake files, and directory helpers from `dir.c`.

## Risks and edge cases
- Delete-on-close must retain the share lock through deletion to prevent recreate races.
- Stale names after rename are tolerated by validating file IDs before unlink.
- `rmdir_internals()` declares a local `struct stat_ex st` but uses `SMB_VFS_LSTAT(conn, smb_dname)` without visibly filling that local in the shown code; reviewers should confirm macro semantics or a latent bug.
- Shutdown close with pending AIO uses careful talloc ordering because AIO destructors mutate the FSP AIO array.
- Magic scripts run from share paths and create output files; configuration and permissions must prevent unintended command execution.
- Alternate stream close recursively frees the base FSP, so stream/base ownership invariants are critical.

## Test signals
Exercise normal/error/shutdown close, durable disconnect success and fallback, delete-on-close for files/directories with other opens, stream deletion, veto-file recursive directory deletion, pending AIO shutdown, SMB1 close write time, magic script output, print/fake file close dispatch, and `MSG_SMB_CLOSE_FILE` handling.
