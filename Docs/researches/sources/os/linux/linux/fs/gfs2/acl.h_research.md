# File Research: sources/os/linux/linux/fs/gfs2/acl.h

Declares GFS2 POSIX ACL interfaces and the ACL entry limit macro.

Exports:
- `GFS2_ACL_MAX_ENTRIES(sdp)` computes the maximum ACL entries from block size.
- `gfs2_get_acl()`
- `__gfs2_set_acl()`
- `gfs2_set_acl()`

Integration:
- Included by ACL implementation and inode/xattr code paths that need ACL operations.
