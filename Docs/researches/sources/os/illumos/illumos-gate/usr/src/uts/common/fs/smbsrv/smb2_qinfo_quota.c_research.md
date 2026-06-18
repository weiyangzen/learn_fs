# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_qinfo_quota.c

Implements optional SMB2 quota query support for `SMB2_0_INFO_QUOTA`.

Key behavior:
- Requires tree quota feature and a disk-backed file handle.
- Decodes quota query flags and SID/start SID lengths from the request.
- Rejects requests containing both SID list and start SID.
- Builds the share root mount path, determines query mode, calculates max quota output, decodes SID input, calls `smb_quota_query()`, and encodes quota entries.
- Treats `NT_STATUS_NO_MORE_ENTRIES` as successful end of enumeration after clearing quota resume state.

Important dependencies:
- Quota subsystem: `smb_quota_max_quota`, `smb_quota_init_sids`, `smb_quota_query`, `smb_quota_encode_quotas`, `smb_quota_free_sids`.
- Tree root path: `smb_node_getmntpath`.

Notable details:
- Unsupported quota-capable trees return `NT_STATUS_INVALID_DEVICE_REQUEST`.
- The implementation mirrors older SMB1 quota transaction behavior.
