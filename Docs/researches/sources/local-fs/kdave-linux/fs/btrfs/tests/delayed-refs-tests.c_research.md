# File Research: sources/local-fs/kdave-linux/fs/btrfs/tests/delayed-refs-tests.c

This file validates Btrfs delayed-reference construction, merging, selection order, and cleanup behavior using dummy transactions.

It defines expected-state structs `ref_head_check` and `ref_node_check`, plus validators for delayed ref heads and nodes. Checks cover bytenr, num_bytes, ref modifiers, total ref modifiers, must-insert state, action, ref type, parent/root/owner/offset identity, and delayed-ref owner/offset accessors.

`simple_test()` converts a `struct btrfs_ref` into either a tree or data delayed ref, selects the resulting delayed-ref head and node, and validates both. `simple_tests()` exercises single add/drop operations for tree block refs, extent data refs, shared block refs, and shared data refs.

`merge_tests()` tests delayed-ref merging for metadata and data refs. It verifies add+drop cancellation, double adds, double drops, positive/negative net transitions after many operations, and complete cancellation across many distinct roots/parents.

`select_delayed_refs_test()` ensures delayed ref selection prioritizes add operations before drop operations, even when insertion order and rbtree ordering could otherwise expose drops first. It also tests a case where one add is merged away while another add remains selectable.

Helper deletion functions remove delayed ref heads and nodes from their trees/lists while managing refcounts and locks in the same style as core delayed-ref code.

`btrfs_test_delayed_refs()` allocates dummy fs info and a dummy transaction, runs simple tests, metadata merge tests, data merge tests, and selection-order tests, then frees all dummy state.
