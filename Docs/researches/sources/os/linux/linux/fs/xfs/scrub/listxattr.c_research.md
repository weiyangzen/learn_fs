# File Research: sources/os/linux/linux/fs/xfs/scrub/listxattr.c

Provides a low-level xattr iterator for scrub code. It walks every extended attribute entry without validation restarts and detects malformed attr dabtrees, including loops.

Main functions:
- `xchk_xattr_walk_sf` iterates shortform xattr entries from the incore attr fork.
- `xchk_xattr_walk_leaf_entries` iterates entries in a leaf block, passing local values directly and remote values as `NULL` plus length.
- `xchk_xattr_walk_leaf` reads and walks the single leaf-format attr block.
- `xchk_xattr_find_leftmost_leaf` descends node-format attr trees from block zero to the leftmost leaf, checking magic, headers, levels, and repeated blocks with a dablock bitmap.
- `xchk_xattr_walk_node` walks the leaf sibling chain in node-format xattrs, detects loops, optionally calls a per-leaf callback between leaves, and walks entries in each leaf.
- `xchk_xattr_walk` selects shortform, leaf, or node traversal after requiring the caller to hold ILOCK and loading attr fork extents when needed.

Important behavior:
- Returns `-EFSCORRUPTED` for malformed tree shape or loops.
- Does not perform cursor restarts; callers must already hold appropriate locks.
- Handles local and remote attribute entries uniformly through callback metadata.
