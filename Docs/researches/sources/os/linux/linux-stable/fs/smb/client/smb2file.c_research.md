# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2file.c

## Purpose
Implements SMB2 file open helpers, symlink error-response parsing, target normalization, resilient handle setup, inode-number fallback retrieval, and byte-range lock replay/unlock support.

## Main Responsibilities
- Parse SMB2 symlink reparse error contexts.
- Normalize symlink targets for file-vs-directory semantics.
- Open SMB2 files and populate `cifs_open_info_data`.
- Request network resiliency for opened handles when configured.
- Unlock byte-range lock sets in batches.
- Re-push cached mandatory locks after reconnect or reopen.

## Key Functions
- `symlink_data()` locates and validates `smb2_symlink_err_rsp` inside either SMB2 error contexts or legacy error data.
- `smb2_fix_symlink_target_type()` appends a trailing slash to directory symlinks, rejects file symlinks with trailing slash, and skips these adjustments for POSIX paths.
- `smb2_parse_symlink_response()` validates substitute/print-name bounds and delegates native symlink target parsing.
- `smb2_open_file()` converts paths to UTF-16, adds `FILE_READ_ATTRIBUTES` when useful, retries without it on `-EACCES`, handles stopped-on-symlink responses, performs reopen with `OPEN_REPARSE_POINT`, optionally requests resiliency, and fills open metadata.
- `smb2_unlock_range()` scans cached locks, filters by requested range and owner semantics, batches SMB2 unlock elements, and restores local lock state on server-side unlock failure.
- `smb2_push_mand_fdlocks()` sends one file descriptor’s mandatory locks in bounded batches.
- `smb2_push_mandatory_locks()` iterates inode lock lists and replays mandatory locks using server `maxBuf` sizing.

## Important Data Flow
1. Path strings are converted with `cifs_convert_path_to_utf16()`.
2. `SMB2_open()` returns create/open metadata or an error iov.
3. `STATUS_STOPPED_ON_SYMLINK` is treated as structured data, not a plain error, when the caller asked for open info.
4. Successful opens may trigger resiliency IOCTL and server inode-number lookup.
5. Lock operations use local lock lists as the source of truth, updating them only after server success.

## Edge Cases and Defensive Logic
- Validates symlink context bounds against `iov_len`.
- Rejects malformed symlink tags and unexpected reparse tags.
- Avoids retry-without-read-attributes unless it intentionally added that access bit.
- Handles servers that do not support resiliency by disabling it for the tcon.
- Caps lock vector allocation by both server `maxBuf` and `PAGE_SIZE`.
- Preserves local locks if a batched unlock request fails.

## Dependencies
Relies on SMB2 protocol helpers from `smb2proto.h`, CIFS inode/session structures, lock-list helpers, UTF-16 conversion helpers, common SMB2 status definitions, and FSCTL constants.
