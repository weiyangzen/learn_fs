# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/treenode.cc

## Purpose
`treenode.cc` implements the mutex-protected binary search tree node used by `concurrent_tree` to store one non-overlapping range lock plus optional child subtrees.

## Important APIs, Types, And Functions
Implemented methods include mutex wrappers, root lifecycle, `set_range_and_txnid()`, `range_overlaps()`, allocation/free, in-place swap, shared-owner add/remove, search, insert, remove, recursive removal, depth estimate, imbalance checks, rotations, child locking, and child pointer maintenance.

## Control Flow
Search compares the target range with the current range, locks/rebalances the relevant child, and descends until a parent of the overlapping or insertion subtree is found. Insert recurses left/right for non-overlap or adds a shared owner for exact shared-lock equality. Remove either removes this subtree root or recurses to the matching child. `maybe_rebalance()` performs AVL-style single/double rotations when depth estimates exceed thresholds.

## State And Persistence Behavior
Each node owns a copied `keyrange`, transaction owner state, optional shared-owner vector, child pointers with depth estimates, comparator pointer, mutex, root/empty flags, and lock-mode flag. State is in-memory only.

## Dependencies
It uses comparator, keyrange, transaction ID substitution, memory macros, internal pthread wrappers, race-tool annotations, and `TxnidVector`.

## Integration Points
`concurrent_tree::locked_keyrange` delegates all actual tree mutation and traversal to this class. `locktree` depends on correct owner preservation during removal, shared-owner update, and rotations.

## Risks And Edge Cases
Manual lock ordering is delicate; rotations unlock all but the new root and reset valgrind ordering metadata. `swap_in_place()` must move range, txnid, shared flag, and owners together. Shared-owner removal can leave `m_txnid == TXNID_SHARED` with a null owners pointer if invariants are broken.

## Test Signals
Insertion/removal order stress, shared lock duplicate ownership, release of one shared owner, escalation extraction after rotations, and concurrent non-overlapping acquisitions are key tests.
