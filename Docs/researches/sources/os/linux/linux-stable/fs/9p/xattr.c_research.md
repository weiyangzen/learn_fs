# File Research: sources/os/linux/linux-stable/fs/9p/xattr.c
- Purpose: Implements extended attribute get/set/list and VFS xattr handlers for 9P.
- Main functions: `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_xattr_set`, `v9fs_fid_xattr_set`, `v9fs_listxattr`, xattr handler get/set callbacks.
- Protocol flow: Uses xattr walk/open/read and create/write/clunk style 9P operations through FIDs.
- VFS integration: Exports `v9fs_xattr_handlers` for generic xattr namespaces and conditional security xattrs.
- ACL integration: ACL code uses the FID xattr helpers to fetch and write POSIX ACL xattr payloads.
- Risks: Buffer sizing and two-phase get operations must distinguish required size from actual read errors.
