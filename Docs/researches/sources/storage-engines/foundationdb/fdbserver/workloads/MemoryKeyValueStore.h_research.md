# sources/storage-engines/foundationdb/fdbserver/workloads/MemoryKeyValueStore.h

## Purpose
Header for an in-memory ordered key-value store that mirrors a subset of FoundationDB key-value operations for tester workloads.

## Important APIs, types, and functions
Declares class `MemoryKeyValueStore` with public APIs for `get`, key-selector resolution via `getKey`, bounded `getRange`, point and range `clear`, `set`, `size`, `startKey`, `endKey`, and `printContents`. It stores data in a private `std::map<Key, Value>`.

## Control flow
The header has no runtime control flow; it defines the contract implemented by `MemoryKeyValueStore.cpp`. Consumers can treat the class as a synchronous model store with FoundationDB key/value and range types.

## State and persistence behavior
State is entirely in-memory and scoped to the object lifetime. There is no persistence, versioning, transaction isolation, or concurrency control in the class contract.

## Dependencies and integration points
Includes `fdbrpc/fdbrpc.h` and tester workload headers for FoundationDB value/range types and pulls in `<map>`. It is intended for workload code rather than production storage.

## Risks and test signals
The API is intentionally minimal and synchronous, so consumers must not assume database semantics such as conflict ranges or snapshots. Test signal comes indirectly from workloads that compare database behavior to this local model.
