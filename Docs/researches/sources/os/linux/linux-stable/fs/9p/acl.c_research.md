# File Research: sources/os/linux/linux-stable/fs/9p/acl.c
- Purpose: Implements POSIX ACL support for 9P by translating between VFS ACL objects and 9P xattr operations.
- Main functions: `v9fs_get_acl`, `v9fs_iop_get_inode_acl`, `v9fs_iop_get_acl`, `v9fs_iop_set_acl`, `v9fs_acl_chmod`, `v9fs_set_create_acl`, `v9fs_acl_mode`.
- Data flow: Reads ACL xattrs through `v9fs_fid_xattr_get`, converts via `posix_acl_from_xattr`, caches ACLs on inodes, and writes ACLs with `v9fs_fid_xattr_set` or `v9fs_xattr_set`.
- Protocol behavior: Dotl and non-dotl paths differ for ACL setting and chmod interactions; dotl can use VFS setattr support for mode updates.
- Integration: Called during inode creation, chmod/setattr, and inode/dentry ACL inode operations declared in `acl.h`.
- Risks: ACL caching assumes inode instantiation populates cached ACL state; code uses `BUG_ON(is_uncached_acl())` for violated expectations. Error handling around xattr absence versus malformed ACL data is central to correct behavior.
