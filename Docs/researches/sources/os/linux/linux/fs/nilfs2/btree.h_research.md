# File Research: sources/os/linux/linux/fs/nilfs2/btree.h

This header defines the public B-tree structures, sizing macros, and exported entry points for NILFS2 B-tree block maps.

Key contents:
- `struct nilfs_btree_path` tracks one level of a B-tree operation:
  - current node buffer and sibling buffer
  - child index
  - old/new pointer requests
  - btnode key-change context
  - selected rebalance operation callback
- Capacity macros define:
  - inline root size and max/min children
  - non-root node extra padding
  - per-block max/min children
  - min/max key values
- Declares:
  - `nilfs_btree_init()`
  - `nilfs_btree_convert_and_insert()`
  - `nilfs_btree_init_gc()`
  - `nilfs_btree_broken_node_block()`

Important role:
- This file ties B-tree operations to the bmap layer and the btnode cache layer.
- The capacity macros are part of the on-disk layout contract because they determine how keys and pointers fit into root and node blocks.
