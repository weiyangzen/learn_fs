# File Research: sources/os/linux/linux-stable/fs/btrfs/tests/delayed-refs-tests.c

## Role
Tests Btrfs delayed-reference construction, merging, selection, and ordering for both metadata refs and data refs.

## Main Helpers
- Defines fake object IDs, bytenrs, levels, inode/file offsets, and parents used by test refs.
- `ref_head_check` and `ref_node_check` encode expected delayed-ref head and node fields.
- `validate_ref_head` checks bytenr, size, `ref_mod`, `total_ref_mod`, and reserved-insert state.
- `validate_ref_node` checks bytenr, size, ref mod, action, parent, root, type, owner, and offset.
- `delete_delayed_ref_head` and `delete_delayed_ref_node` remove selected refs while matching delayed-ref locking and reference-count expectations.

## Test Behavior
- `simple_tests` verifies that single add and drop operations for tree block refs, extent data refs, shared block refs, and shared data refs create the expected delayed-ref node shape.
- `merge_tests` runs for metadata and data refs. It validates add+drop cancellation, double add merge, double drop merge, positive-to-negative and negative-to-positive aggregate changes, and many-root/many-parent add/drop cancellation.
- `select_delayed_refs_test` verifies delayed-ref selection ordering: add operations are selected before delete operations even if inserted later in rb-tree order, and merged-away add refs do not hide other add refs.
- `btrfs_test_delayed_refs` creates dummy fs_info, dummy transaction state, and a dummy transaction handle, then runs simple, merge, and selection tests.

## Dependencies
Depends on transaction and delayed-ref internals, extent-tree ref initialization, common dummy fs_info/transaction helpers, rb-tree manipulation, delayed-ref locks, and delayed-ref destruction paths.
