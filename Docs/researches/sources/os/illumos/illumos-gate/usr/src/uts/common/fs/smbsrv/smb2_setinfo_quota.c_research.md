# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_quota.c

Implements optional SMB2 quota set support.

Key behavior:
- Requires quota-enabled tree, disk-backed file handle, and admin user.
- Resolves share root mount path.
- Decodes quota records from the set-info input buffer.
- Sends quota changes to `smb_quota_set()` and returns its NT status reply.
- Frees quota list, root path, and releases the file reference before returning.

Important dependencies:
- Quota subsystem: `smb_quota_decode_quotas`, `smb_quota_set`, `smb_quota_free_quotas`.
- Authorization: `smb_user_is_admin`.
- `smb_node_getmntpath`.

Notable details:
- Unsupported or non-admin requests fail before calling quota service.
