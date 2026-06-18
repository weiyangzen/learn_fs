# File Research: sources/os/linux/linux/fs/smb/client/xattr.c

## Scope
Read completely: 535 lines. This file implements CIFS/SMB VFS extended attribute handlers, including user EAs, OS/2-style aliases, DOS attribute pseudo-xattrs, creation-time pseudo-xattrs, and CIFS/SMB3 security descriptor xattrs.

## Purpose
`xattr.c` connects Linux xattr VFS operations to SMB server capabilities. It provides get/set/list handlers and exports `cifs_xattr_handlers[]` for CIFS inode/superblock operations.

## Xattr Names And Handler Classes
Pseudo/user names:
- `user.cifs.dosattrib`
- `user.cifs.creationtime`
- `user.smb3.dosattrib`
- `user.smb3.creationtime`

Security descriptor names:
- `system.cifs_acl`: DACL only.
- `system.cifs_ntsd`: owner/group plus DACL.
- `system.cifs_ntsd_full`: owner/group, DACL, and SACL.
- `system.smb3_acl`: DACL-only alias.
- `system.smb3_ntsd_sacl`: SACL only.
- `system.smb3_ntsd_owner`: owner/group only.
- `system.smb3_ntsd`: owner/group plus DACL alias.
- `system.smb3_ntsd_full`: full descriptor alias.

Handler flags distinguish `XATTR_USER`, CIFS ACL, POSIX ACL slots, and NTSD variants.

## Set Path
`cifs_xattr_set()`:
- Acquires a tcon link from the superblock.
- Gets an XID and builds a full path from the dentry.
- Rejects EA values larger than `CIFSMaxBufSize`.
- For user pseudo-xattrs:
  - `cifs.dosattrib` / `smb3.dosattrib` call `cifs_attrib_set()`.
  - `cifs.creationtime` / `smb3.creationtime` call `cifs_creation_time_set()`.
  - Other user attrs call dialect `set_EA` unless mounted with `CIFS_MOUNT_NO_XATTR`.
- For security descriptor attrs:
  - Copies user-provided descriptor into kernel memory.
  - Converts handler flag to CIFS ACL flags: owner, group, DACL, SACL.
  - Calls dialect `set_acl()` if available.
  - Forces inode revalidation on success.

`cifs_attrib_set()` and `cifs_creation_time_set()` build `FILE_BASIC_INFO` buffers and call dialect `set_file_info()`, then update cached CIFS inode fields on success.

## Get Path
`cifs_xattr_get()`:
- Acquires tcon, XID, and full dentry path.
- For pseudo-xattrs:
  - `cifs_attrib_get()` revalidates dentry attributes and returns cached DOS attributes.
  - `cifs_creation_time_get()` revalidates and returns cached creation time.
- For user EAs:
  - Calls dialect `query_all_EAs()` unless `CIFS_MOUNT_NO_XATTR`.
- For NTSD/ACL xattrs:
  - Maps the handler flag to `OWNER_SECINFO`, `GROUP_SECINFO`, `DACL_SECINFO`, and/or `SACL_SECINFO`.
  - Calls dialect `get_acl()`.
  - Returns descriptor length for size probe or copies the descriptor into caller buffer if it fits.
- Converts `-EINVAL` to `-EOPNOTSUPP` before returning.

## List Path
`cifs_listxattr()`:
- Rejects forced shutdown with traced EIO.
- Rejects `CIFS_MOUNT_NO_XATTR`.
- Builds full path and calls dialect `query_all_EAs()` with a null EA name to enumerate attributes.
- Releases path, XID, and tcon resources on exit.

## Handler Registration
`cifs_xattr_handlers[]` registers:
- `user.*`
- `os2.*` treated like user xattrs.
- legacy `system.cifs_*` security names.
- newer `system.smb3_*` aliases.

The comments explicitly call out that the SMB3 names are aliases intended to avoid exposing the legacy “cifs” name to users for modern SMB2/3 mounts.

## State And Synchronization
The file does not own complex locks. It relies on:
- tcon references from `cifs_sb_tlink()`.
- XID accounting.
- path allocation/free helpers.
- inode revalidation and cached fields in `CIFS_I(inode)`.
- dialect operation callbacks for actual protocol operations.

## Security-Relevant Behavior
- Security descriptor xattrs can expose or modify owner/group/DACL/SACL depending on the requested name.
- SACL access depends on server-side permissions and dialect ACL implementation.
- The file copies user-provided security descriptors into kernel memory before passing them to protocol code.
- EA values are bounded by `CIFSMaxBufSize`.

## Risks And Review Focus
- In the ACL get path, `acllen` is a `u32`; assigning `-ERANGE` to it when the caller buffer is too small can produce a large positive return value when assigned to `rc`. This is a review-worthy bug pattern.
- Pseudo-xattr set paths trust exact `sizeof(__u32)` and `sizeof(__u64)` value sizes; userspace ABI expectations should remain stable.
- Security descriptor get/set semantics must stay aligned with `cifsacl.c` and dialect `get_acl`/`set_acl` implementations.
- `CIFS_MOUNT_NO_XATTR` suppresses server EAs but not pseudo-xattrs before the check in user get/set paths.

## Research Takeaways
`xattr.c` is the VFS adapter for SMB EAs and security descriptors. It mixes true server EAs, locally cached pseudo attributes, and ACL/NTSD protocol calls behind Linux xattr names.
