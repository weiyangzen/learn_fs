# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterKeyValueStore.h

## Purpose
`TesterKeyValueStore.h` declares the thread-safe ordered in-memory key/value store used as the expected-state oracle by C API tester workloads.

## Important APIs, Types, And Functions
- Query methods: `get`, `exists`, `getKey`, and `getRange`.
- Mutation methods: `set`, `clear(key)`, and `clear(begin,end)`.
- Metadata/debug methods: `size`, `startKey`, `endKey`, and `printContents`.
- Private members: `std::map<fdb::Key, fdb::Value, std::less<>> store` and mutable `std::mutex`.

## Control Flow
The header only declares the interface. Implementations lock internally, so callers do not manage synchronization.

## State And Persistence Behavior
The declared map holds local expected state. Sentinels returned by `startKey()`/`endKey()` model selector results before the first key and after the last key.

## Dependencies And Integration Points
It depends on STL containers, mutexes, optionals, and `TesterUtil.h` for FDB wrapper types. `TesterApiWorkload.h` includes it and stores per-tenant instances.

## Risks And Edge Cases
Because it is used as an oracle, semantic drift from FoundationDB selector/range behavior affects many tests. Methods accepting `fdb::KeyRef`/`ValueRef` must copy data into owning strings before refs expire; the implementation does this through `fdb::Key`/`Value`.

## Test Signals
Compile coverage comes from all API tester workloads. Runtime signal is indirect through comparisons in correctness and cancellation workloads.
