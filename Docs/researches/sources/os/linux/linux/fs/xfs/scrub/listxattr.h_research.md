# File Research: sources/os/linux/linux/fs/xfs/scrub/listxattr.h

Declares callback types and the xattr walker:
- `xchk_xattr_fn` receives each attr entry’s flags, name, optional local value pointer, value length, and caller private data.
- `xchk_xattrleaf_fn` optionally runs between node-format leaf blocks.
- `xchk_xattr_walk` walks all xattrs for a locked inode.

The API is designed for scrub users that need raw enumeration of existing xattr records with corruption reporting.
