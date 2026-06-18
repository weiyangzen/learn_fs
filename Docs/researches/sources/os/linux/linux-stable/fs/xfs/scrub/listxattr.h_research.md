# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/listxattr.h

This header declares callback types and the xattr walker used by scrub code.

Types:
- `xchk_xattr_fn`: called per xattr entry with scrub context, inode, attr flags, name, name length, value pointer, value length, and private data.
- `xchk_xattrleaf_fn`: optional callback invoked around leaf traversal in node-format attr forks.

Exported function:
- `xchk_xattr_walk`

Purpose:
- Provides a uniform interface over shortform, leaf, and node-format extended attributes without requiring each scrubber to duplicate attr fork traversal logic.
