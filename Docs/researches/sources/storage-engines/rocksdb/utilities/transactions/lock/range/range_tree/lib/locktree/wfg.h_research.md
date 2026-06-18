# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/locktree/wfg.h

## Purpose
`wfg.h` declares the wait-for graph abstraction used to model "transaction A waits for transaction B" relationships for deadlock detection.

## Important APIs, Types, And Functions
Public APIs are `create()`, `destroy()`, `add_edge()`, `node_exists()`, `cycle_exists_from_txnid()`, `apply_nodes()`, and `apply_edges()`. Private `node` stores a `TXNID`, `txnid_set edges`, and `visited` flag, with allocation/free helpers.

## Control Flow
The graph API is mutable during construction, then traversed for cycle checks or diagnostic iteration. `cycle_exists_from_txnid()` accepts a `std::function<void(TXNID)>` reporter for deadlock detail collection.

## State And Persistence Behavior
State is one OMT of node pointers, each with an edge set. It is manual-lifecycle, POD-enforced, and transient.

## Dependencies
It includes `<functional>`, OMT, and `txnid_set`. Transaction ID definitions arrive through `txnid_set.h`.

## Integration Points
Only lock request deadlock logic should need this class. It is independent of key ranges and relies solely on transaction IDs supplied by conflict discovery.

## Risks And Edge Cases
Manual allocation and POD constraints limit modernization. Any caller that mutates the graph while traversing would violate assumptions. Large wait graphs could recurse deeply.

## Test Signals
Cycle/no-cycle unit tests and lock-request deadlock integration tests are expected. Reporter callback coverage is useful because RocksDB deadlock diagnostics depend on it.
