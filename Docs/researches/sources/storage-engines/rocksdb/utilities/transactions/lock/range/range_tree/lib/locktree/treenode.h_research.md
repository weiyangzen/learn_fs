# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.h

## Purpose
`treenode.h` declares the low-level mutable node type backing `concurrent_tree`, including traversal, insertion, removal, shared ownership, per-node locking, and approximate balancing.

## Important APIs, Types, And Functions
Public APIs include root lifecycle, range/txnid setup, state queries, mutex lock/unlock, subtree search, templated `traverse_overlaps()`, `insert()`, `remove()`, and `recursive_remove()`. Private helpers define `child_ptr`, shared-owner operations, extreme-child search, root removal, rebalance operations, allocation/free, and range/owner swapping.

## Control Flow
`traverse_overlaps()` performs in-order traversal while locking each child before recursing and unlocking after. The tree assumes callers hold the current node lock and children are initially unlocked for most operations.

## State And Persistence Behavior
The node contains a `toku_mutex_t`, copied `keyrange`, `TXNID` or `TXNID_SHARED`, shared-lock flag, optional owner vector, left/right children and depth estimates, comparator pointer, and root/empty flags.

## Dependencies
It includes comparator, memory helpers, pthread wrappers, status header, transaction ID substitution, and `keyrange`.

## Integration Points
`concurrent_tree` is the only intended caller; `locktree` observes node data through traversal callbacks. Friend unit-test classes can inspect internals.

## Risks And Edge Cases
This is not a general container: callers must enforce non-overlap and exact-match removal. The templated traversal passes references to internal ranges that must not be used after node deletion. Balance estimates are approximate and updated through child pointers.

## Test Signals
Tree unit tests should cover overlap traversal pruning, exact removal, root emptying, rotations, shared owners, and recursive removal. Range-lock integration tests cover it indirectly.
