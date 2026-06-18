# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/concurrent_tree.cc

## Purpose
`concurrent_tree.cc` implements the lockable range tree wrapper used by `locktree` to store non-overlapping row-lock ranges with per-subtree mutual exclusion.

## Important APIs, Types, And Functions
`concurrent_tree::create()` initializes an always-present root `treenode`; `destroy()`, `is_empty()`, and `get_insertion_memory_overhead()` provide lifecycle and memory accounting. `locked_keyrange::prepare()`, `acquire()`, `release()`, `insert()`, `remove()`, `remove_all()`, and `add_shared_owner()` are the mutable access primitives.

## Control Flow
`prepare()` locks the root and makes the current protected range infinite. `acquire()` narrows protection to the subtree that could contain or overlap the requested `keyrange`: empty root or root overlap stays at root, otherwise it descends with `find_node_with_overlapping_child()`. Inserts either populate an empty root or recurse through `treenode::insert()`. Removes delegate to `treenode::remove()` and handle the special empty-root result.

## State And Persistence Behavior
State is entirely in memory in `m_root` and allocated descendant nodes. The tree owns copied key ranges inside nodes, not persistent DB records. It assumes `destroy()` is called only after the tree is empty.

## Dependencies
It depends on `concurrent_tree.h`, `treenode`, `keyrange`, and comparator support. It is excluded under `OS_WIN`.

## Integration Points
`locktree` prepares/acquires locked keyranges for conflict checks, acquisition, release, dump, STO migration, and escalation. Memory accounting uses `sizeof(treenode)` via `get_insertion_memory_overhead()`.

## Risks And Edge Cases
The API relies on strict prepare/acquire/release sequencing; missing `release()` leaves tree mutexes held. `remove()` assumes the exact range exists. Subtree locking correctness depends on `treenode` preserving non-overlap and balanced child pointers.

## Test Signals
Range-lock conflict, release, escalation, and waiter tests indirectly exercise this file. Dedicated unit tests are referenced through friend declarations but are not in this work item.
