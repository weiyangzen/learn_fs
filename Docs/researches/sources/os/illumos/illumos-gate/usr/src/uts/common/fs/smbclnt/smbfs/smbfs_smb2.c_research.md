# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_smb2.c

## Scope

This file implements SMB2-specific SMBFS protocol operations for query/set info, statfs, flush, rename, directory enumeration, stream info, and security descriptors.

## APIs And Behavior

- A disabled `smbfs_smb2_locking()` block reserves future over-the-wire locking support.
- `smbfs_smb2_getpattr()` opens the target with read-attributes/read-control rights, uses create response attributes, and closes the handle.
- `smbfs_smb2_query_info()` builds and sends SMB2 QUERY_INFO requests, validates response structure size, skips to payload offsets, and returns payload as an mdchain.
- `smbfs_smb2_qfileinfo()` queries `FileAllInformation` and decodes it.
- `smbfs_smb2_query_fs_info()` opens the share root directly and queries filesystem information.
- `smbfs_smb2_qfsattr()` queries and decodes `FileFsAttributeInformation`.
- `smbfs_smb2_statfs()` queries `FileFsFullSizeInformation`.
- `smbfs_smb2_flush()` sends SMB2 FLUSH with persistent and volatile FID parts and disables reconnect for the request.
- `smbfs_smb2_set_info()` builds common SMB2 SET_INFO requests with payload length backpatching.
- `smbfs_smb2_seteof()`, `smbfs_smb2_setdisp()`, and `smbfs_smb2_setfattr()` set EOF, disposition, and basic metadata.
- `smbfs_smb2_rename()` builds `FileRenameInformation` with a full target path.
- `smbfs_smb2_qdir()` sends SMB2 QUERY_DIRECTORY, caps buffers at 64 KiB or negotiated max transact size, transfers the response payload to the find context, and marks EOF on parse errors or empty responses.
- `smbfs_smb2_findopen()` opens a directory handle for enumeration and initializes the find context.
- `smbfs_smb2_findclose()` releases directory handle, request, name buffer, and mdchain.
- `smbfs_smb2_findnext()` refills directory buffers as needed and decodes one directory entry.
- `smbfs_smb2_get_streaminfo()` opens the object and queries `FileStreamInformation`.
- `smbfs_smb2_getsec()` queries SMB2 security information and returns the payload mblk.
- `smbfs_smb2_setsec()` consumes a caller mblk and sends SMB2 security SET_INFO.

## State And Dependencies

- Uses SMB2 request opcodes, `smb2fid_t`, mchain/mdchain helpers, common path/create/close helpers, and SMBFS decode functions.

## Risks And Invariants

- SMB2 payload offsets are validated against expected header-relative positions to catch malformed responses.
- Directory query receive is marked non-interruptible to avoid server-side enumeration offset corruption.
- Query-directory lacks entry count, so parsing tracks byte offsets through `f_left` and `f_eofs`.
- Security set consumes the input mblk and clears the caller pointer.
