# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2inode.c

## Purpose
Implements SMB2/SMB3 inode-path operations using compound open-operation-close request chains. This is the central file for SMB2 path metadata queries, mkdir/rmdir/unlink, rename, hardlink, truncation, basic info updates, reparse point creation/query, WSL EA handling, and pending-delete rename behavior.

## Main Responsibilities
- Build and send SMB2 compound operations around an open file handle.
- Reuse existing `cifsFileInfo` handles when available.
- Query standard and POSIX metadata.
- Validate and copy reparse, POSIX SID, and WSL EA responses.
- Implement directory/file create-delete-rename-hardlink operations.
- Retry replayable compounds and retry without leases when lease keys are invalid.
- Clean up intermediate server objects after partial reparse creation failure.

## Key Helpers
- `reparse_buf_ptr()` validates IOCTL output bounds and returns a reparse data buffer.
- `file_create_options()` adds `OPEN_REPARSE_POINT` when a dentry inode is already marked reparse.
- `parse_posix_sids()` extracts owner/group SIDs from SMB3.1.1 POSIX query info.
- `check_wsl_eas()` validates WSL EA response layout, names, lengths, alignment, and allowed value sizes.
- `set_next_compound()` marks `NextCommand` and related-request bits while accounting for implicit close.
- `smb2_compound_op()` is the main dispatcher and transport wrapper for compound path operations.
- `parse_create_response()` extracts reparse/symlink state from SMB2 create responses.
- `ea_unsupported()` distinguishes tolerated WSL EA query failure after earlier compound commands succeeded.
- `free_rsp_iov()` frees response buffers and resets iov/buftype slots.

## `smb2_compound_op()` Behavior
The function accepts a tcon, mount info, path, open parameters, input iovs, operation command IDs, optional existing file handle, optional output response arrays, and optional dentry.

It:
1. Picks a channel and allocates per-compound variable storage.
2. Sets encryption flags when required.
3. Opens the path unless an existing `cfile` handle is supplied.
4. Reuses a lease key from the inode when available.
5. Builds operation requests based on `enum smb2_compound_ops`.
6. Adds close when it opened the handle itself.
7. Sends via `compound_send_recv()`.
8. Frees request buffers, maps each response’s error status, traces operation success/failure, copies requested output data, and frees or transfers response buffers.
9. Replays on replayable errors using `smb2_should_replay()`.
10. Drops the passed `cfile` reference before returning.

Supported operation cases include:
- `SMB2_OP_QUERY_INFO`
- `SMB2_OP_POSIX_QUERY_INFO`
- `SMB2_OP_MKDIR`
- `SMB2_OP_UNLINK`
- `SMB2_OP_SET_EOF`
- `SMB2_OP_SET_INFO`
- `SMB2_OP_RENAME`
- `SMB2_OP_HARDLINK`
- `SMB2_OP_SET_REPARSE`
- `SMB2_OP_GET_REPARSE`
- `SMB2_OP_QUERY_WSL_EA`

## Public Operations
- `smb2_query_path_info()` queries metadata, uses cached root handle when possible, supports POSIX query info, handles `-EACCES` fallback through open-query, handles reparse points and symlink parsing, and detects DFS links on invalid-name errors.
- `smb2_mkdir()` creates a directory through compound create semantics.
- `smb2_mkdir_setinfo()` sets readonly attributes after mkdir when needed.
- `smb2_rmdir()` drops cached directory state and marks the directory delete-pending.
- `smb2_unlink()` uses a two-request open/delete-on-close plus close compound, sets `FILE_SHARE_DELETE`, retries replayable errors, retries without lease on `-EINVAL`, and marks open handles for deleted files.
- `smb2_rename_path()` performs rename via `FILE_RENAME_INFORMATION`, invalidates cached dir entries, and retries without lease on invalid lease-key errors.
- `smb2_create_hardlink()` clears tmpfile attributes when needed and sends `FILE_LINK_INFORMATION`.
- `smb2_set_path_size()` sends `FILE_END_OF_FILE_INFORMATION` to truncate/extend by path, with invalid-lease retry.
- `smb2_set_file_info()` sends `FILE_BASIC_INFORMATION` for timestamps/attributes, skipping pure no-op updates.
- `smb2_create_reparse_inode()` creates an object with `OPEN_REPARSE_POINT`, sets its reparse buffer, queries resulting inode info, and unlinks the intermediate object if set-reparse fails after create succeeds.
- `smb2_query_reparse_point()` opens with `OPEN_REPARSE_POINT`, retrieves reparse IOCTL output, and transfers the response buffer to caller.
- `smb2_rename_pending_delete()` implements CIFS silly-rename style pending delete: clears readonly, optionally hides last-link files, renames to a generated delete-pending name, unlinks, and sets `CIFS_INO_DELETE_PENDING`.

## Important Data Flow
- Path inputs are converted to UTF-16 for SMB2 create/open and rename/link targets.
- Existing open handles avoid extra open/close compounds where possible.
- Compound responses are indexed relative to open + operation + close; callers that request output buffers receive ownership of selected response iovs.
- Metadata results are copied into `cifs_open_info_data`, with flags marking whether POSIX info, symlink target, WSL EA, or reparse data is present.
- Reparse-point handling bridges SMB IOCTL buffers to Linux inode creation/query paths.

## Edge Cases and Defensive Logic
- Reparse buffers are bounds-checked with overflow detection.
- POSIX SID and WSL EA parsers reject truncated, misaligned, unknown, or overlong data.
- Compound replay marks every replayed request with SMB2 replay flags.
- `-EREMCHG` marks the tree connection for reconnect after share deletion.
- Hardlink lease-key mismatch is explicitly documented and handled by retrying without the inode lease.
- WSL EA failures are tolerated for non-block/non-char reparse tags after other commands succeed.
- Reparse object creation cleans up empty server-side artifacts after partial failure.
- Pending-delete rename maps failure through SMB EIO tracing.

## Dependencies
This file depends on CIFS VFS state, SMB2 PDU construction/free helpers, compound send/receive, cached directory handling, reparse constants, POSIX info parsing, WSL EA constants, tracepoints, and inode update helpers.
