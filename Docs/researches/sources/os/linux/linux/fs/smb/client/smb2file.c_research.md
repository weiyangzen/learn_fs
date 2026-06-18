# File Research: sources/os/linux/linux/fs/smb/client/smb2file.c

This file contains SMB2/SMB3 file-open helpers, symlink error-response parsing, resilient-handle setup, server inode-number fallback, and SMB2 byte-range lock batching.

Primary responsibilities:
- Parse SMB2 symlink error responses from `STATUS_STOPPED_ON_SYMLINK`.
- Normalize parsed symlink targets for file vs directory behavior.
- Open SMB2 files through `smb2_open_file()`.
- Request network resiliency on opens when the tree connection enables it.
- Query a server file number when the open response lacks `IndexNumber`.
- Unlock SMB2 byte-range lock ranges in batches.
- Replay locally tracked mandatory byte-range locks to the server.

Important control flow:
- `symlink_data()` supports both SMB2 error-context responses and older direct `ErrorData` symlink layouts, validating byte counts, context lengths, tags, and bounds.
- `smb2_parse_symlink_response()` checks substitute/print name offsets and lengths before calling `smb2_parse_native_symlink()`.
- `smb2_fix_symlink_target_type()` appends a trailing slash to directory symlink targets on non-POSIX mounts and rejects file symlink targets that end in `/`.
- `smb2_open_file()` converts the path to UTF-16, may temporarily add `FILE_READ_ATTRIBUTES`, opens with batch oplock request, retries without `FILE_READ_ATTRIBUTES` after `-EACCES`, and handles stopped-on-symlink by reopening with `OPEN_REPARSE_POINT`.
- After a successful open, resilient opens issue `FSCTL_LMR_REQUEST_RESILIENCY`; `-EOPNOTSUPP` disables future resiliency attempts for the tcon.
- If metadata was requested and `IndexNumber` is zero, the helper calls `SMB2_get_srv_num()` and lets higher layers handle unsupported inode numbers.

Lock handling:
- `smb2_unlock_range()` walks locally tracked locks for a file, selects locks fully covered by the requested unlock range and matching owner rules, removes locally cached locks without sending, or batches SMB2 unlock elements to `smb2_lockv()`.
- On server unlock failure, moved locks are restored to the file lock list; on success, temporary lock records are freed.
- `smb2_push_mandatory_locks()` allocates a page-bounded array of `smb2_lock_element` objects and replays all per-FID mandatory locks through `smb2_push_mand_fdlocks()`.

Validation and safety:
- Path conversion failure returns `-ENOMEM`.
- Symlink parsing validates every server-provided offset/length against the actual response iov.
- Lock batch sizing snapshots `server->maxBuf`, rejects too-small values, caps allocation at `PAGE_SIZE`, and uses `BUILD_BUG_ON()` for element size assumptions.
- The unlock path holds `cinode->lock_sem` while mutating lock lists.

Dependencies:
- SMB2 open/ioctl/query helpers, CIFS path conversion, open-info data structures, tcon/session/server state, lock-list helpers, inode lock state, and SMB2 symlink/reparse constants.

Research notes:
- The file bridges VFS open semantics and SMB2 open semantics, especially for symlink traversal and metadata access-denied fallbacks.
- Lock batching is carefully written to preserve local lock state if remote unlocks fail.
- The `FILE_READ_ATTRIBUTES` retry path is important for servers/share ACLs that allow opening but deny explicit attribute-read access.
