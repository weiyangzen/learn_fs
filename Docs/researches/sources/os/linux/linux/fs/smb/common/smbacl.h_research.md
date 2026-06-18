# File Research: sources/os/linux/linux/fs/smb/common/smbacl.h

This common SMB header defines Windows security descriptor, SID, ACL, and ACE wire layouts used by SMB client/server code. The structures are packed and little-endian where required.

Key contents:
- ACE type constants from MS-DTYP, including allow, deny, audit, callback, object, mandatory label, resource attribute, and scoped policy ACEs.
- ACE inheritance/audit flags such as `OBJECT_INHERIT_ACE`, `CONTAINER_INHERIT_ACE`, and `INHERITED_ACE`.
- SID string sizing helpers and SID subauthority limits.
- SID role enum values for owner, group, UNIX/NFS user/group, and mode.
- Packed `struct smb_ntsd`, `struct smb_sid`, `struct smb_acl`, and `struct smb_ace`.

The file has no behavior; it is a shared ABI/layout definition for security metadata parsing and generation.
