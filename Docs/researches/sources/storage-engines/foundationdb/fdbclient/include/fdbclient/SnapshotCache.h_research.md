# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/SnapshotCache.h

## Purpose
`SnapshotCache.h` declares the read snapshot cache used by RYW transactions. It records known key ranges and values from snapshot reads, exposes an iterator over known KVs, known-empty spans, and unknown spans, and supports promises for in-flight cache fills.

## Important APIs, Types, And Functions
- `ExtStringRef` represents a `StringRef` plus virtual trailing zero bytes, supports arena conversion, comparison, prefix checks, and `keyAfter()`.
- Comparison operators and `Traceable<ExtStringRef>` support ordering and trace output.
- `SnapshotCache::Entry` stores known `[beginKey, endKey)` plus sorted `KeyValueRef` values; absent keys inside the range are implicitly empty.
- `SnapshotCache::iterator` traverses `UNKNOWN_RANGE`, `EMPTY_RANGE`, and `KV` segments and supports skip/next/previous/contiguous skipping.
- `SnapshotCache` stores an arena pointer and an `IndexedSet<Entry>`, initialized with degenerate all-keys boundary entries.
- `insert(key, value)` records a known present or absent single key if still unknown.
- `insert(range, values)` records a known range, trimming around already-known subranges.
- `promise(segment, keys, onReady)` declares an in-flight read that should later populate the cache.

## Control Flow And State
The cache starts with sentinel entries at `allKeys.begin` and `allKeys.end`. Iterators compute segment type from an `Entry` plus offset. `skip()` finds the entry containing or just before a key, then classifies whether the key is known, empty, or unknown. Range insertion finds begin/end iterators, trims values against already-known boundaries, erases unknown entry spans, and inserts a new known entry.

## Persistence And External State
All state is transaction-local and arena-backed. The cache does not persist to disk. It depends on read results from native transactions and feeds RYW range merge logic.

## Dependencies And Integration Points
It depends on FDB types, native API constants such as `allKeys`/`afterAllKeys`, system data, and Flow `IndexedSet`. `ReadYourWritesTransaction` is a friend and combines it with `WriteMap` through `RYWIterator`.

## Risks And Edge Cases
`ExtStringRef` comparison with virtual trailing zeroes is subtle and critical for key-after semantics. Iterator offsets encode segment type; off-by-one errors can misclassify empty ranges as KVs or unknown ranges. Insert trimming must preserve cache invariants and sorted values. `promise()` must not invalidate the provided segment. Arena lifetimes govern returned refs.

## Test Signals
Tests should cover `ExtStringRef` comparison/prefix/keyAfter, empty cache behavior, single-key present/absent insertion, range insertion with existing known boundaries, iterator skip and forward/backward traversal, contiguous skip helpers, all-keys sentinels, promise readiness interactions, and cache dumping/tracing.
