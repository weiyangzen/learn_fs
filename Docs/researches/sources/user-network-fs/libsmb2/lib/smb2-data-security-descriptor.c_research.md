# sources/user-network-fs/libsmb2/lib/smb2-data-security-descriptor.c

## Purpose
Decodes self-relative SMB2/Windows security descriptors into SID, ACL, and ACE structures.

## Important APIs, Types, And Functions
The public API is `smb2_decode_security_descriptor`. Internal helpers are `decode_sid`, `decode_ace`, and `decode_acl`. It uses `struct smb2_security_descriptor`, `struct smb2_sid`, `struct smb2_acl`, and `struct smb2_ace`, with list linkage through `SMB2_LIST_ADD_END`.

## Control Flow
Security descriptor decoding validates the descriptor header and revision, reads owner/group/SACL/DACL offsets, and decodes present owner, group, and DACL components. SID decoding validates revision and subauthority count before allocating a variable-sized SID. ACL decoding validates revision and ACL size, then iterates ACE count and decodes each ACE. ACE decoding handles common allow/deny/audit/mandatory/object/callback ACEs and stores raw data for unknown types.

## State And Persistence
All decoded substructures are allocated under the provided memory context, commonly the security descriptor object. The DACL ACE list is linked into the decoded ACL. The parser advances local iovec copies and does not mutate the source buffer.

## Dependencies And Integration Points
Called from QUERY_INFO security response decoding. Depends on `slist.h`, SMB2 security constants, iovec helpers, context allocation, and error reporting through `smb2_set_error`.

## Risks
SACL offsets are read but not decoded. Some ACE paths call `decode_sid` but do not immediately fail if it returns null, leaving possible partially initialized ACEs. Unknown ACE raw length is the remaining local vector after the header, not necessarily bounded to `ace_size - 4`. Offset checks use minimal SID/ACL header sizes and ignore descriptors where an offset points exactly to the last valid byte.

## Test Signals
Test owner/group/DACL decoding, ACL revisions, zero ACEs, all supported ACE families, unknown ACE raw preservation, malformed SID revisions/counts, ACE size underflow/overflow, SACL-only descriptors, and truncated self-relative offsets.
