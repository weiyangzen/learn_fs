# File Research: sources/os/linux/linux/fs/smb/server/xattr.h

Defines Samba-compatible xattr metadata formats used by ksmbd to preserve Windows filesystem semantics on POSIX filesystems.

Key contents:
- DOS attribute validity flags for attribute, EA size, size, allocation size, create time, change time, and initial time.
- `xattr_dos_attrib` for DOS attributes and Windows timestamps stored in `user.DOSATTRIB`.
- POSIX ACL entry/tag enums and `xattr_smb_acl` flexible-array structure used to hash current POSIX ACL state.
- NTACL xattr hash constants and `xattr_ntacl`, storing version, encoded security descriptor, hash type, descriptor label, timestamp, NTSD hash, and POSIX ACL hash.
- Xattr name prefixes and lengths for DOS attributes, alternate data streams, and security descriptors: `user.DOSATTRIB`, `user.DosStream.`, and `security.NTACL`.

Role in subsystem:
- On-disk metadata contract for interoperability with Samba and for preserving Windows attributes, streams, creation time, and NT ACLs.
