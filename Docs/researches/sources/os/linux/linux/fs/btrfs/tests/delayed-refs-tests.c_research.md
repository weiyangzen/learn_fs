# File Research: sources/os/linux/linux/fs/btrfs/tests/delayed-refs-tests.c

Read completely: 1016 lines.

This file tests delayed-reference creation, selection, ordering, and merge behavior for metadata and data refs.

Validation helpers:
- `ref_head_check` and `ref_node_check` describe expected delayed-ref head/node fields.
- `validate_ref_head()` checks bytenr, num_bytes, `ref_mod`, `total_ref_mod`, and `must_insert_reserved`.
- `validate_ref_node()` checks bytenr, num_bytes, ref_mod, action, parent, root, disk ref type, owner, and offset.
- `delete_delayed_ref_head()` and `delete_delayed_ref_node()` manually remove selected test refs and drop references.

`simple_test()` converts a prepared `btrfs_ref` into a delayed tree/data ref, selects the head and first delayed-ref node, and validates both.

`simple_tests()` covers single add and single drop cases for:
- tree block refs
- extent data refs
- shared block refs
- shared data refs

`merge_tests()` runs for both `BTRFS_REF_METADATA` and `BTRFS_REF_DATA`. It validates:
- add followed by drop collapses to a head with zero total mod and no nodes.
- two adds merge into one add node with `ref_mod == 2`.
- two drops merge into one drop node with `ref_mod == -2`.
- many adds then more drops produce the expected negative merged node.
- many drops then more adds produce the expected positive merged node.
- many refs across alternating roots/parents followed by matching drops collapse to no nodes.

`select_delayed_refs_test()` validates delayed-ref selection priority:
- Add operations are selected before drop operations even if insertion order or rb-tree order would otherwise differ.
- If an add is merged away, a remaining add is still selected before drops.

`btrfs_test_delayed_refs()` creates dummy fs_info, dummy transaction, and dummy transaction handle, then runs simple tests, metadata merge tests, data merge tests, and selection-order tests.

Correctness focus:
- Delayed refs must preserve correct aggregate reference deltas while merging equivalent operations.
- Selection order matters because extent processing depends on adds being handled before drops.
- Data and metadata refs share many mechanics but differ in ref type, owner, and offset semantics, so both are exercised.
