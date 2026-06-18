# sources/user-network-fs/samba/source4/smb_server/smb2/fileinfo.c

## Purpose
Implements SMB2 GETINFO and SETINFO request handling for file, filesystem, and security information. It maps SMB2 info classes to Samba raw/passthrough levels, calls NTVFS backends, marshals output blobs, parses input blobs, validates handles, and serializes SMB2 replies/errors.

## Important APIs, Types, And Functions
- `struct smb2srv_getinfo_op` and `struct smb2srv_setinfo_op` carry request-local operation state.
- `smb2srv_getinfo_recv()` parses SMB2 GETINFO body fields, pulls input buffer, resolves the file handle, and dispatches to `smb2srv_getinfo_backend()`.
- `smb2srv_getinfo_file()`, `smb2srv_getinfo_fs()`, and `smb2srv_getinfo_security()` map info type/class to NTVFS qfileinfo/fsinfo/security calls.
- `smb2srv_getinfo_send()` remaps `NT_STATUS_INVALID_LEVEL` to `NT_STATUS_INVALID_INFO_CLASS`, marshals output, checks output buffer length, and sends the response blob.
- `smb2srv_setinfo_recv()` parses SMB2 SETINFO body fields and dispatches to `smb2srv_setinfo_backend()`.
- `smb2srv_setinfo_file()`, `smb2srv_setinfo_fs()`, and `smb2srv_setinfo_security()` parse input and call NTVFS setfileinfo or return SMB2-specific status.

## Control Flow
GETINFO checks the fixed body size, allocates both the public `smb2_getinfo` and private operation state, creates an NTVFS request, reads info type/class, output length, additional information, flags, handle, and input buffer. File info handles SMB2 all-EAs and all-information specially; other file and filesystem classes map to raw level `class + 1000`. Security info class 0 uses NDR to push a security descriptor. On completion, the output blob must fit the requested output buffer or `INFO_LENGTH_MISMATCH` is returned. SETINFO similarly parses level, blob, flags, and handle. File levels map to passthrough setfileinfo, with SMB2 rename using a distinct raw level; filesystem setinfo mostly denies or rejects; security class 0 pulls an NDR security descriptor and calls `ntvfs_setfileinfo()`.

## State And Persistence
No state persists beyond the request except whatever the NTVFS backend changes: file metadata, filesystem metadata if ever implemented, delete-on-close, rename, allocation/EOF, security descriptors, etc. The request holds output/input blobs and operation state until async completion.

## Dependencies And Integration Points
Uses SMB2 server request helpers, SMB2 blob offset/length helpers, NTVFS, passthrough marshaling/parsing from `blob.c`, and NDR security descriptor routines. It shares the same backend raw information model as SMB1 Trans2/NTTrans.

## Risks
SMB2 status mapping differs from SMB1; preserving `INVALID_INFO_CLASS` behavior is important. Output buffer length is enforced after backend marshaling, so large metadata paths must return `INFO_LENGTH_MISMATCH` cleanly. The TODO in filesystem GETINFO notes qfsinfo should be limited to the share root directory handle. SETINFO filesystem classes are deliberately denied/not implemented for selected levels. Rename parsing differs between SMB1 and SMB2 because SMB2 uses an 8-byte root FID field in the blob.

## Test Signals
Test GETINFO file passthrough levels, SMB2 all-EAs/all-information, filesystem info levels, security descriptor query, output buffer too small, invalid info type/class mapping, SETINFO basic/disposition/allocation/EOF/rename paths, security descriptor set, unsupported quota, denied filesystem set classes, invalid handles, and async backend completion status translation.
