# File Research: sources/os/linux/linux/fs/ubifs/tnc_misc.c

Read completely: 517 lines.

This file contains shared TNC helper functions for znode traversal, branch searching, subtree destruction, loading index znodes from flash, and reading leaf nodes by zbranch.

Main entry points: `ubifs_tnc_levelorder_next`, `ubifs_search_zbranch`, `ubifs_tnc_postorder_first`, `ubifs_tnc_postorder_next`, `ubifs_destroy_tnc_subtree`, `ubifs_destroy_tnc_tree`, `ubifs_load_znode`, and `ubifs_tnc_read_node`.

Traversal helpers: `ubifs_tnc_levelorder_next` supports breadth/level-order traversal from a subtree root and is used by the shrinker to reclaim old clean subtrees. `ubifs_tnc_postorder_first` and `ubifs_tnc_postorder_next` support postorder traversal for safe subtree freeing.

Branch search: `ubifs_search_zbranch` performs binary search inside a znode and returns either an exact match or the closest-left insertion position, using `-1` when the searched key is smaller than every branch key.

Tree destruction: `ubifs_destroy_tnc_subtree` frees all connected znodes below a subtree root and counts clean znodes freed. `ubifs_destroy_tnc_tree` destroys the whole TNC and subtracts the per-filesystem clean count from the global shrinker counter.

Index loading: `read_znode` reads an on-flash index node, verifies its node hash, child count, level, branch LEB/offset/length bounds, key types, leaf target length ranges, and key ordering. It rejects duplicate non-hashed keys and dumps bad index nodes before returning `-EINVAL`.

Lazy znode loading: `ubifs_load_znode` allocates a fanout-sized znode, fills it via `read_znode`, increments per-filesystem and global clean-znode counters, attaches it to the parent zbranch, stamps its access time, and records `iip`.

Leaf reads: `ubifs_tnc_read_node` reads a non-index node from either a journal write-buffer or flash, validates node type/length through low-level I/O, verifies the node key matches the zbranch key, and checks the stored node hash.

Important interactions: `tnc.c` relies on these helpers for lazy tree descent, branch search, leaf reads, and shutdown cleanup. `shrinker.c` uses level-order traversal and subtree destruction. `tnc_commit.c` and GC logic depend on index-node validation and hash propagation matching these helpers.

Reliability notes: all loaded index and leaf nodes are checked against both structural constraints and stored hashes. The global clean-znode counter is intentionally updated after per-mount counter updates and may be briefly inconsistent, which the shrinker design tolerates.
