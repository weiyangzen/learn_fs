# sources/storage-engines/foundationdb/fdbclient/RYWIterator.cpp

## Purpose
`RYWIterator.cpp` implements the iterator that overlays a transaction's local `WriteMap` on top of its `SnapshotCache`. It is the low-level mechanism used by read-your-writes transactions to see local mutations, clears, dependent atomic operations, and cached snapshot reads as one ordered keyspace.

## Important APIs, Types, and Functions
- `RYWIterator::typeMap` maps the cartesian product of write segment type and cache segment type to `UNKNOWN_RANGE`, `EMPTY_RANGE`, or `KV`.
- `type`, `is_kv`, `is_unknown_range`, `is_empty_range`, `is_dependent`, and `is_unreadable` classify the current overlay segment.
- `beginKey` and `endKey` compute the current segment bounds from the write/cache boundary comparisons.
- `kv(Arena&)` returns the visible key/value, coalescing local write operations over cached values when needed, and returns `nullptr` for deletes produced by operations such as compare-and-clear.
- `operator++` and `operator--` advance both underlying iterators when segment boundaries are reached.
- `skip`, `skipContiguous`, and `skipContiguousBack` support positioning and efficient contiguous cache traversal.
- `extractWriteMapIterator` gives higher-level code access to the underlying write iterator for conflict tracking.

## Control Flow and State
The iterator maintains a `SnapshotCache::iterator`, a `WriteMap::iterator`, and cached comparison results between their begin/end keys. Movement advances whichever iterator owns the current boundary, then flips/recomputes comparisons. Reads first enforce unreadable protection unless bypassed, then either return cached data, local independent writes, or coalesced dependent writes over cached values.

## State and Persistence Behavior
State is transient and points into the transaction-owned arena/cache/write map. There is no persistence. The `temp` key/value is used to return a stable coalesced result until the iterator advances or another `kv` call overwrites it.

## Dependencies and Integration Points
The file depends on `fdbclient/RYWIterator.h`, `KeyRangeMap`, and Flow unit tests. It is tightly coupled to `ReadYourWrites.actor.cpp`, `SnapshotCache`, `WriteMap`, `OperationStack`, and mutation coalescing semantics.

## Risks and Edge Cases
- Unreadable versionstamp-related ranges must throw unless bypassed; bypass is used in targeted tests and internal paths.
- `kv` can return `nullptr` for logically deleted keys even when `is_kv()` is true, so callers must check.
- Correctness depends on `begin_key_cmp` and `end_key_cmp` staying in sync after every skip or movement.
- Coalescing dependent atomic operations over absent cached values is subtle and must match storage-server mutation semantics.

## Test Signals
This file contains extensive unit tests for `WriteMap` emptiness, clears, versionstamped key/value unreadability, atomic add coalescing, random mutation ranges, conflict map behavior, and debug-only snapshot cache iteration. Important additional signals are reverse iteration parity, contiguous skip correctness, and compare-and-clear deletion results.
