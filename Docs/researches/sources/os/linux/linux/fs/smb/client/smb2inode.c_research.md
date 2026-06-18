# File Research: sources/os/linux/linux/fs/smb/client/smb2inode.c

This file implements SMB2/SMB3 path and inode metadata operations using compound open-operation-close request chains. It covers path stat, mkdir/rmdir/unlink, rename, hardlink, truncate, attribute update, reparse-point creation/query, POSIX query info, WSL EA handling, and pending-delete rename.

Primary responsibilities:
- Build reusable SMB2 compound requests in `smb2_compound_op()`.
- Query path metadata through regular SMB2 `FILE_ALL_INFORMATION` or SMB3.1.1 POSIX info.
- Parse POSIX owner/group SIDs from POSIX query responses.
- Validate and copy WSL EA metadata for special file emulation.
- Validate FSCTL reparse responses and transfer reparse response-buffer ownership to callers.
- Implement mkdir, rmdir, unlink/delete-on-close, rename, hardlink, set-size, and set-file-info operations.
- Create and query reparse-point inodes.
- Rename a file to a hidden temporary “silly” name and mark it pending delete.

Important control flow:
- `smb2_compound_op()` optionally opens a path, appends one or more operations, optionally closes the compound FID, sends through `compound_send_recv()`, parses each response, frees request buffers, transfers selected output buffers, and retries replayable errors with `smb2_should_replay()`.
- When a caller already has `cifsFileInfo`, the helper skips open/close and sends only the operation portion using the existing persistent/volatile FID.
- Lease reuse is attempted when a dentry has an existing lease key; callers retry without lease on `-EINVAL` for hardlink/path alias edge cases.
- `smb2_query_path_info()` uses cached root directory metadata when possible, otherwise compounds query info. It falls back to `SMB2_OP_OPEN_QUERY` with `MAXIMUM_ALLOWED` when `FILE_READ_ATTRIBUTES` open/query fails with `-EACCES`.
- Reparse handling for `-EOPNOTSUPP` parses create response status, optionally gets the reparse point, optionally queries WSL EAs, and fixes symlink target type.
- `smb2_unlink()` is specialized: it opens with `CREATE_DELETE_ON_CLOSE | OPEN_REPARSE_POINT`, adjusts share access to `FILE_SHARE_DELETE`, compounds close, retries replayable errors, retries without lease on `-EINVAL`, and marks open handles deleted after success.
- `smb2_create_reparse_inode()` creates the object with `OPEN_REPARSE_POINT`, sets reparse data, queries inode metadata, and unlinks the intermediate object if create succeeded but setting reparse data failed.

Validation and safety:
- `reparse_buf_ptr()` checks output offset/count addition overflow, iov bounds, minimum reparse buffer length, and `ReparseDataLength`.
- `parse_posix_sids()` validates POSIX query output length and SID lengths before copying owner/group SIDs.
- `check_wsl_eas()` enforces minimum/maximum EA response sizes, bounds every EA entry, validates name length, value length, expected WSL xattr names, alignment, and next-entry overflow.
- `smb2_validate_and_copy_iov()` is used for query-info response copying.
- Response buffers are freed via `free_rsp_iov()` unless ownership is explicitly transferred for reparse data.
- Compound response arrays account for implicit open and close responses around the requested operation list.

Notable operations:
- `smb2_mkdir()` creates a directory through SMB2 CREATE parameters; `smb2_mkdir_setinfo()` follows with attribute update for read-only directory state.
- `smb2_rmdir()` drops cached directory handles before delete disposition.
- `smb2_rename_path()` and `smb2_create_hardlink()` share `smb2_set_path_attr()` for UTF-16 target-name set-info operations.
- `smb2_set_path_size()` sends `FILE_END_OF_FILE_INFORMATION`.
- `smb2_set_file_info()` skips no-op all-zero timestamp/attribute updates.
- `smb2_query_reparse_point()` returns both tag and response iov/buffer type to the caller.
- `smb2_rename_pending_delete()` clears readonly, may set hidden for last-link deletes, renames to a generated silly path, then sets delete disposition.

Dependencies:
- CIFS VFS/inode structures, tcon/session/server state, cached directory handles, SMB2 request init/free helpers, compound send/receive, path conversion, reparse constants, POSIX query structures, WSL EA constants, tracepoints, and inode metadata refresh helpers.

Research notes:
- `smb2_compound_op()` is the central abstraction in this file; the correctness of many VFS path operations depends on its response indexing, buffer ownership, replay logic, and cfile reference handling.
- Reparse and symlink behavior is one of the most subtle areas because successful create/open responses can carry reparse status, and some follow-up queries intentionally open with `OPEN_REPARSE_POINT`.
- WSL EA handling is deliberately strict because the server response is copied into client metadata used to represent Unix-like special files.
