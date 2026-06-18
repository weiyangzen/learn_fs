# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_sec.c

Implements SMB2 security descriptor query handling.

Key behavior:
- Requires disk-backed file handles.
- Clears SACL requests when the target tree ACL type is not `ACE_T`.
- Reads the security descriptor with `smb_sd_read()`, computes encoded length, and either returns it or reports the required size.
- On insufficient output buffer, encodes a 4-byte required-size value and returns `NT_STATUS_BUFFER_TOO_SMALL`.

Important dependencies:
- Security descriptor conversion: `smb_sd_read`, `smb_sd_len`, `smb_encode_sd`, `smb_sd_term`.
- Error wrapping in `smb2_query_info.c` handles SMB 3.1.1 error-context specifics.

Notable details:
- Empty/zero-length descriptors are treated as invalid security descriptors.
