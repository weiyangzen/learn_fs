# File Research: sources/local-fs/ntfs-3g/libntfs-3g/xattrs.c

Implements common handling for NTFS-3G system extended attributes. It maps external xattr names to internal NTFS metadata operations for security descriptors, POSIX ACLs, DOS attributes, EFS metadata, reparse data, object IDs, DOS names, timestamps, creation time, and extended attributes.

The static name table recognizes `system.ntfs_acl`, `system.ntfs_attrib`, `system.ntfs_attrib_be`, `system.ntfs_efsinfo`, `system.ntfs_reparse_data`, `system.ntfs_object_id`, `system.ntfs_dos_name`, `system.ntfs_times`, `system.ntfs_times_be`, `system.ntfs_crtime`, `system.ntfs_crtime_be`, `system.ntfs_ea`, `system.posix_acl_access`, and `system.posix_acl_default`. `ntfs_xattr_system_type()` resolves names, optionally consulting volume-level remapping rules or the raw-EFS alternate `user.ntfs.efsinfo`.

When `XATTR_MAPPINGS` is enabled, the file parses an xattr mapping file either from an absolute host path with `read()` or from a relative path on the NTFS volume using internal inode/attribute reads. Mapping lines bind a known system xattr to a valid `user.*` name, skip comments/space, reject bad items, ignore duplicate/conflicting mappings, and add `user.ntfs.efsinfo` automatically for raw EFS if not explicitly mapped.

`ntfs_xattr_system_getxattr()` dispatches reads to ACL/security, POSIX ACL, NTFS attributes, EFS info, reparse data, object ID, DOS name, inode times, creation time, and EA helpers. Big-endian variants byte-swap scalar values or timestamp arrays for caller-visible big-endian formats. On big-endian hosts with POSIX ACLs, POSIX ACL structures are converted between little-endian wire format and CPU-endian structures.

`ntfs_xattr_system_setxattr()` mirrors get dispatch for writes, including endian conversion before storing attributes/times/ACLs. EFS metadata is writable only in raw EFS mode. DOS-name setting requires a directory inode and notes that the callee closes both inodes. `ntfs_xattr_system_removexattr()` denies removal of non-removable metadata such as ACLs, attributes, EFS info, and times, but permits owner-authorized removal of POSIX ACLs, reparse data, object IDs, DOS names, and NTFS EAs.

Dependencies include security contexts, ACL conversion, EFS, reparse point, object ID, EA, directory/DOS-name, inode timestamp, xattr mapping, and NTFS logging helpers. Key invariants are permission checks through owner/security helpers, raw-EFS gating for EFS metadata, endian-stable xattr formats, and careful handling of xattrs whose set/remove helpers may close passed inodes.
