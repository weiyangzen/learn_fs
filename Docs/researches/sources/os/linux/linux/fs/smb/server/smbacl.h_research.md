# File Research: sources/os/linux/linux/fs/smb/server/smbacl.h

Declares ksmbd ACL state structures, security descriptor flags, ACL conversion APIs, permission checks, inheritance helpers, and idmapped POSIX ACL translation helpers.

Key contents:
- Security descriptor control flags such as `DACL_PRESENT`, `SELF_RELATIVE`, inheritance/protection flags, and defaulted flags.
- `smb_fattr`, carrying translated uid/gid/mode, desired access, and access/default POSIX ACL pointers.
- Intermediate POSIX ACL state structures used while converting SMB ACEs.
- Public APIs for parsing/building security descriptors, inheriting/checking DACLs, setting security info, SID conversion, domain initialization, and scratch sizing.
- Inline helpers to translate POSIX ACL uid/gid through mount idmaps into init-user-namespace userspace IDs visible to ksmbd.

Role in subsystem:
- Exposes the ACL conversion contract used by SMB create/query/set-info paths and VFS xattr persistence.
