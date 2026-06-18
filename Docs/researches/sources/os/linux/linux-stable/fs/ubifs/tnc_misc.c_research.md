# File Research: sources/os/linux/linux-stable/fs/ubifs/tnc_misc.c

## Purpose
Provides shared TNC helpers for traversal, zbranch binary search, TNC destruction, loading index znodes from flash, and reading leaf nodes.

## Key Behavior
- `ubifs_tnc_levelorder_next()` supports level-order traversal, mainly used by the shrinker to reclaim clean subtrees.
- `ubifs_search_zbranch()` binary-searches a znode’s sorted branches and returns either exact match or the left-nearest slot.
- `ubifs_tnc_postorder_first()` and `ubifs_tnc_postorder_next()` support safe subtree destruction.
- `ubifs_destroy_tnc_subtree()` frees all znodes in a subtree and returns the number of clean znodes freed.
- `ubifs_destroy_tnc_tree()` destroys the whole cached TNC and adjusts the global clean znode counter.
- `read_znode()` reads an on-flash index node, validates hash, branch count, level, branch addresses, key types, leaf-node length ranges, and sorted key order.
- `ubifs_load_znode()` allocates a znode, fills it from an index node, links it into the parent branch, timestamps it, and increments clean znode counters.
- `ubifs_tnc_read_node()` reads a leaf node through a journal write buffer if needed, validates the key and node hash, and returns errors for mismatches.

## Important Dependencies
- Uses UBIFS key comparison/read/write helpers and node validation/hash helpers.
- Clean znode counters are consumed by `shrinker.c`.
- TNC lookup and mutation paths in `tnc.c` rely on these helpers for lazy loading and tree traversal.

## Invariants and Risks
- Index-node validation rejects malformed branch positions outside the main area, unaligned offsets, invalid key types, impossible lengths, and invalid non-hash duplicate keys.
- Znodes are allocated with size dependent on superblock fanout, so no fixed slab cache is used.
- LNC leaf payloads are ignored by traversal/destruction helpers; leaf cache memory is managed where branches are removed or replaced.
