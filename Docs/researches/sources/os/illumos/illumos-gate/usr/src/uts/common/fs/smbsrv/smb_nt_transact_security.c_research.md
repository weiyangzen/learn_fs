# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_security.c

## Summary
Implements SMB1 NT transact query/set security descriptor operations and the local encoder/decoder for SMB self-relative security descriptors, SIDs, ACLs, and ACEs.

## Main Responsibilities
- Reads security descriptors for disk file handles.
- Writes security descriptors for disk file handles.
- Masks SACL requests on filesystems that do not support `ACE_T`.
- Rejects writes on readonly trees.
- Encodes self-relative security descriptors into response data.
- Decodes self-relative security descriptors from request data.
- Allocates and frees decoded SID/ACL structures through SMB security helpers.

## Key APIs
- `smb_nt_transact_query_security_info()`.
- `smb_nt_transact_set_security_info()`.
- `smb_encode_sd()`, `smb_encode_sid()`.
- `smb_decode_sd()`, `smb_decode_sid()`.

## Important Behavior
Query decodes FID and `secinfo`, looks up a disk ofile, adopts the ofile credential, reads the descriptor with `smb_sd_read()`, calculates the encoded length, and either returns `NT_STATUS_BUFFER_TOO_SMALL` with a size hint or encodes the descriptor.

Set decodes FID and `secinfo`, rejects readonly trees, decodes the supplied descriptor, validates required owner/group fields, and skips writes to system nodes. Non-`ACE_T` targets have SACL bits removed from requested security information.

`sm b_encode_sd()` writes a self-relative header and offsets for owner, group, SACL, and DACL, then serializes the selected components. DACL ACEs are emitted from the sorted ACL list; SACL ACEs are emitted in array order.

`sm b_decode_sd()` shadows the request chain, validates component offsets against the descriptor header, ensures SACL/DACL present bits agree with nonzero offsets, and decodes pointed-to SIDs/ACLs.

## Dependencies
Depends on SMB security descriptor model helpers, SID/ACL allocation/free, filesystem security read/write functions, mbuf-chain shadowing, ofile credentials, tree ACL type, and readonly tree checks.

## Risks
`sm b_decode_sid()` checks `bytes_left < sizeof (smb_sid_t)`, which is larger than the minimum wire SID header. Very short but otherwise valid SIDs may be rejected depending on `smb_sid_t` layout.

Set-security returns success without writing when the target node is marked system, silently protecting special files.
