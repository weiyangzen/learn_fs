# File Research: sources/local-fs/gfs2-utils/gfs2/fsck/inode_hash.c

## Purpose
Implements a red-black tree keyed by inode block address for non-directory inode link-count tracking during fsck.

## Main Elements
- `inodetree_find()`: searches `cx->inodetree` by `num.in_addr`.
- `inodetree_insert()`: returns an existing node for a block or allocates/inserts a new `struct inode_info`.
- `inodetree_delete()`: removes a node from the tree and frees it.

## Dependencies And Integration
Uses `osi_tree` style node operations via `osi_link_node()`, `osi_insert_color()`, and `osi_erase()`. Called by link counting, bitmap repair, pass1 cleanup, duplicate resolution, and global teardown.

## Behavioral Notes
The tree is keyed only by block address. Formal inode number mismatches are checked by callers such as `incr_link_count()`.
