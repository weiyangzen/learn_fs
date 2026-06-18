# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_sec.c

Implements SMB2 security descriptor set handling.

Key behavior:
- Requires disk-backed file handles and writable media.
- Clears SACL requests on non-`ACE_T` filesystems.
- Returns success for empty effective security-info masks.
- Decodes the incoming security descriptor and validates requested owner/group fields are present.
- Avoids writing security descriptors on system nodes.
- Writes security descriptors through `smb_sd_write()` and releases descriptor resources.

Important dependencies:
- `smb_decode_sd`, `smb_sd_write`, `smb_sd_term`.
- Read-only media check: `SMB_TREE_IS_READONLY`.

Notable details:
- Missing owner/group in a descriptor that claims to set those fields returns `NT_STATUS_INVALID_PARAMETER`.
