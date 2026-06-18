# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tests/delayed-refs-tests.c

This file tests delayed-reference insertion, merging, selection order, and cleanup. It uses fake constants for root objectid, bytenr, tree level, inode, file offset, and shared parent so that metadata and data ref cases can share validation logic.

`struct ref_head_check` and `struct ref_node_check` encode expected delayed-ref-head and delayed-ref-node fields. `validate_ref_head()` checks bytenr, num_bytes, ref_mod, total_ref_mod, and reserved-insert state. `validate_ref_node()` checks bytenr, num_bytes, ref_mod, action, parent, root, type, owner, and offset.

`simple_test()` creates a `struct btrfs_ref`, initializes it as metadata or data depending on the disk ref key type, adds it through the real delayed-ref add helpers, selects the ref head, selects one node, validates both, then destroys delayed refs. `simple_tests()` runs this for add/drop variants of tree-block, extent-data, shared-block, and shared-data refs.

`merge_tests()` validates ref merging for metadata and data refs. It covers add followed by drop producing a zero-ref-mod head with no nodes; double add producing one merged add node; double drop producing one merged drop node; positive-to-negative and negative-to-positive transitions after many adds/drops; and a 50-ref mixed root/parent workload that should cancel cleanly to a zero-mod head with no nodes.

`select_delayed_refs_test()` checks delayed-ref selection order. It verifies that add operations are selected before drops even when the drop was inserted first and even when one add is canceled by merging, leaving another add that still must be selected before the drop.

The file includes local delete helpers that erase selected nodes/heads from delayed-ref trees and drop references in the same style expected by the delayed-ref implementation. `btrfs_test_delayed_refs()` allocates a dummy fs_info and transaction, initializes dummy transaction state, runs simple tests, metadata merge tests, data merge tests, and selection-order tests, then frees all resources.
