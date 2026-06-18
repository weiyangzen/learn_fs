# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.h

## Purpose
`txnid_set.h` declares a POD-compatible set abstraction for transaction IDs used by conflict, owner, and wait-for-graph code.

## Important APIs, Types, And Functions
The class exposes `create()`, `destroy()`, `contains()`, `add()`, `remove()`, `size()`, and `get(i)`. It stores `toku::omt<TXNID> m_txnids` and is guarded by `ENSURE_POD`.

## Control Flow
The API is intentionally simple: callers create the set, add/remove IDs, iterate by index, and destroy the internal OMT. Sorting is provided by implementation comparator functions.

## State And Persistence Behavior
All state is in-memory OMT storage. The set does not own transaction objects, only numeric IDs.

## Dependencies
It includes transaction ID substitution and OMT. `ENSURE_POD` comes through portability/assert infrastructure.

## Integration Points
`locktree::get_conflicts()`, `lock_request::deadlock_exists()`, `wfg::node::edges`, and shared-owner conflict expansion all depend on this type.

## Risks And Edge Cases
Because it is POD-style, constructors are not used; missing `create()` or `destroy()` causes invalid access or leaks. Index iteration assumes stable ordering while no mutation occurs.

## Test Signals
Conflict collection in range-lock tests and deadlock tests are integration coverage. Direct unit tests should validate POD lifecycle and duplicate handling.
