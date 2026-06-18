# File Research: sources/os/linux/linux-stable/fs/smb/client/xattr.c

## Summary
Implements CIFS/SMB VFS extended attribute handlers. It exposes user and OS/2 EA passthrough, pseudo-xattrs for DOS attributes and creation time, and system xattrs for CIFS/SMB3 security descriptors.

## Main Responsibilities
- Set pseudo-xattrs `user.cifs.dosattrib`, `user.smb3.dosattrib`, `user.cifs.creationtime`, and `user.smb3.creationtime` by translating them to `FILE_BASIC_INFO` updates.
- Get pseudo-xattrs from cached/revalidated inode metadata.
- Pass ordinary `user.*` and `os2.*` EAs through protocol operations `set_EA` and `query_all_EAs`, unless `CIFS_MOUNT_NO_XATTR` is set.
- Get and set CIFS/SMB3 ACL/security descriptor xattrs through server `get_acl` and `set_acl` operations.
- Provide `cifs_listxattr()` by querying all EAs from the server.
- Register `cifs_xattr_handlers[]` for user, os2, legacy `system.cifs_*`, and newer `system.smb3_*` names.

## Key Interfaces
- Set path: `cifs_xattr_set()`, `cifs_attrib_set()`, `cifs_creation_time_set()`.
- Get path: `cifs_xattr_get()`, `cifs_attrib_get()`, `cifs_creation_time_get()`.
- List path: `cifs_listxattr()`.
- Handler table: `cifs_xattr_handlers`.

## Security Descriptor Handling
Supported system xattrs include DACL-only, owner+DACL, owner-only, SACL-only, and full owner/group/DACL/SACL forms. Handler flags are translated into CIFS ACL selector bits for set operations and SMB security information flags for get operations.

## Risks
This file bridges untrusted user buffers, path construction, server operations, and security metadata. Important checks include EA value size limits, exact pseudo-xattr sizes, `NO_XATTR` mount handling, forced-shutdown handling in listxattr, and revalidation before returning pseudo attributes. SACL/full descriptor access depends on lower-layer authorization and server behavior.
