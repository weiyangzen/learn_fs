# File Research: sources/os/linux/linux/fs/9p/xattr.c

Implements extended attribute get/set/list support for 9P2000.L.

Key behavior:
- `v9fs_fid_xattr_get()`:
  - Uses `p9_client_xattrwalk()` to open an xattr FID and learn attribute size.
  - Returns size for zero-length probe buffers.
  - Returns `-ERANGE` if the provided buffer is too small.
  - Reads the xattr contents through `p9_client_read()`.
- `v9fs_xattr_get()` looks up a dentry FID and delegates to FID-based get.
- `v9fs_fid_xattr_set()`:
  - Clones the input FID.
  - Uses `p9_client_xattrcreate()` to create/replace/remove the attribute stream.
  - Writes the value through `p9_client_write()`.
  - Returns clunk errors if the write path succeeded.
- `v9fs_xattr_set()` looks up a dentry FID and delegates to FID-based set.
- `v9fs_listxattr()` uses xattrwalk with an empty string.
- Defines generic xattr handlers for `user.*` and `trusted.*`.
- Adds `security.*` handler when `CONFIG_9P_FS_SECURITY` is enabled.

Important interactions:
- `vfs_super.c` installs these handlers only for dotl mounts when xattrs are not disabled.
- ACL code uses the same xattr-capable dotl infrastructure.
