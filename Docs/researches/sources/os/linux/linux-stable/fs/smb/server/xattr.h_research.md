# File Research: sources/os/linux/linux-stable/fs/smb/server/xattr.h

## Summary
Defines ksmbd on-disk xattr metadata formats for Samba-compatible DOS attributes, named streams, POSIX ACL hashes, and NT security descriptors.

## Main Responsibilities
- Define DOS attribute valid-field flags and `struct xattr_dos_attrib`.
- Define simplified ACL entry/tag constants used to hash POSIX ACL state.
- Define `struct xattr_smb_acl` for encoded POSIX ACL hash input.
- Define `struct xattr_ntacl` for NDR v4 NTACL storage, descriptor hashes, POSIX ACL hashes, timestamp, and descriptor metadata.
- Define xattr name prefixes for DOS attributes, named streams, and NTACL security descriptors.

## Cross-File Interactions
Used by `vfs.c` for DOS attribute, stream, and NTACL xattr storage; by ACL code for security descriptor interoperability; and by NDR encode/decode helpers.

## Risks
These are persistent metadata formats. Changing fields, versions, prefixes, or hash semantics can break compatibility with existing ksmbd/Samba xattrs.
