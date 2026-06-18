# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_setinfo_fs.c

Implements SMB2 filesystem set-info dispatch.

Key behavior:
- Supports `FileFsControlInformation` as a successful disk-tree no-op.
- Rejects `FileFsObjectIdInformation` with `NT_STATUS_INVALID_PARAMETER`.
- All other classes return `NT_STATUS_INVALID_INFO_CLASS`.

Important dependencies:
- Tree resource type validation through `STYPE_ISDSK`.

Notable details:
- Object IDs cannot be changed, matching the referenced FSCC behavior.
