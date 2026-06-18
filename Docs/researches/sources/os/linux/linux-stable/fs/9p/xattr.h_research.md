# File Research: sources/os/linux/linux-stable/fs/9p/xattr.h
- Purpose: Declares xattr support shared by 9P xattr and ACL code.
- Main exports: `v9fs_fid_xattr_get`, `v9fs_xattr_get`, `v9fs_xattr_set`, `v9fs_fid_xattr_set`, `v9fs_listxattr`, and `v9fs_xattr_handlers`.
- Integration: Included by inode/super/ACL code to wire VFS xattr handlers and POSIX ACL persistence.
- Research notes: This header carries the public internal xattr contract for the 9P subtree.
