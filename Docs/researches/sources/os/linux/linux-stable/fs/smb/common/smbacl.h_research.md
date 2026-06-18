# File Research: sources/os/linux/linux-stable/fs/smb/common/smbacl.h

Read status: complete.

## Purpose
Provides shared SMB/CIFS ACL, ACE, SID, and security descriptor wire-format definitions.

## Main Contents
- SID authority/subauthority sizing constants.
- MS-DTYP ACE type and ACE inheritance/audit flag constants.
- SID string sizing helpers and SID type enums for owner/group/Unix/NFS forms.
- Packed wire structs: `smb_ntsd`, `smb_sid`, `smb_acl`, and `smb_ace`.

## Dependencies And Role
Used by SMB client and server ACL code as the common layout contract for security descriptors and access control entries.

## Risks
Packed structure layout and SID size bounds are protocol-sensitive. Changing field order, array sizes, or constants would break ACL parsing/building and can create bounds-checking bugs in callers.
