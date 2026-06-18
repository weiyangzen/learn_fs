# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/txnid_set.cc

## Purpose
`txnid_set.cc` implements a small sorted transaction-ID set on top of the local OMT container.

## Important APIs, Types, And Functions
`find_by_txnid()` compares transaction IDs. Methods implement `create()`, `destroy()`, `contains()`, `add()`, `remove()`, `size()`, and indexed `get()`.

## Control Flow
`create()` initializes the OMT without allocating an array. Lookup operations use `find_zero` with the comparator. `add()` inserts and accepts duplicate `DB_KEYEXIST`. `remove()` deletes only if found. `get()` fetches by sorted index and returns `TXNID_NONE` only for impossible `EINVAL` fallback.

## State And Persistence Behavior
State is the OMT-held set of TXNIDs. It is transient and must be destroyed manually. Ordering is sorted by numeric transaction ID.

## Dependencies
It includes `txnid_set.h` and `db.h` for return codes. It relies on OMT and invariant macros.

## Integration Points
Conflict collection, wait graph edges, shared-lock owner conflict expansion, and deadlock detection all use `txnid_set`.

## Risks And Edge Cases
The type is POD-style and manual lifecycle must be respected. `get(0)` is assumed valid by callers after conflicts are reported; conflict-producing paths must not leave the set empty.

## Test Signals
Set unit tests should cover duplicate insert, ordered fetch, removal of absent IDs, and empty lazy allocation. Lock timeout/deadlock paths indirectly exercise it.
