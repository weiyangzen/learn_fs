# File Research: sources/local-fs/reiserfsprogs/include/reiserfs_fs.h

Central on-disk ReiserFS format header. It defines endian-safe accessors, superblock layouts for old and current formats, journal descriptor/commit/header structures, keys, item headers, block headers, stat-data formats, directory-entry headers, disk-child pointers, paths, virtual nodes, tree-balance structures, item type constants, and balancing modes.

Major areas:
- Superblock and journal constants: magic strings, disk offsets, format versions, mount/fs states, journal defaults.
- Key/item model: v1 and v2 key encoding, item flags, stat/direct/indirect/directory classification, item-body access macros.
- Tree node layout: block headers, internal child pointers, path macros, node size limits, `MAX_HEIGHT`.
- Directory format: directory entry headers, visibility/bad-location flags, hash/generation offset helpers.
- Balancing model: `virtual_item`, `virtual_node`, `tree_balance`, mode constants, neighbor/FEB arrays, and buffer-info helpers.
- Function declarations for search, fix_nodes, balance, printing, hashing, and node-format helpers.

This file is the contract binding fsck, mkreiserfs, bitmap, journal, and tree-balancing code to the same byte-level disk layout.
