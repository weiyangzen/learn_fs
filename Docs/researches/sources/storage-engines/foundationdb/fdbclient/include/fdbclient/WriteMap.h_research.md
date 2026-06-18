<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/WriteMap.h -->
# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/WriteMap.h

## Purpose
`WriteMap.h` declares the read-your-writes mutation overlay that tracks point mutations, clear ranges, conflict ranges, unreadable ranges, and dependency on snapshot values before a transaction commits.

## Important APIs, Types, and Functions
Important types include `RYWMutation`, `OperationStack`, boolean parameter wrappers, `WriteMapEntry`, comparison operators, and `WriteMap` with `mutate`, `clear`, `addUnmodifiedAndUnreadableRange`, `addConflictRange`, nested `iterator`, `coalesce`, `coalesceOver`, `coalesceUnder`, and private `clearNoConflict`.

## Control Flow
The map starts with sentinel entries for all keys and after-all keys. Mutations are inserted into a persistent tree at an internal version. Operation stacks coalesce or layer atomic operations, point writes, and clears. Iterators produce a complete segmentation of the keyspace into unmodified ranges, cleared ranges, independent writes, and dependent writes. Read-your-writes code combines these segments with snapshot reads to synthesize transaction-visible results.

## State and Persistence Behavior
`WriteMap` is transaction-local in-memory state backed by an arena and `PTreeImpl` persistent tree. It tracks conflict/unreadable flags and local mutation effects but persists only when the transaction commits through lower-level commit machinery. Its internal `ver` is not a database version; it separates iterator snapshots from later writes.

## Dependencies and Integration Points
It depends on FDB types, `VersionedMap`, `SnapshotCache`, and atomic mutation helpers. It integrates with `ReadYourWritesTransaction`, conflict range handling, snapshot cache reads, atomic operation coalescing, and approximate transaction size/cost calculations.

## Risks and Edge Cases
Atomic coalescing must preserve FoundationDB mutation semantics, especially dependent operations needing a snapshot value. Clear ranges and conflict ranges overlap but are tracked separately. Iterator snapshots can become stale after writes by design. Sentinel key handling must cover the entire keyspace without leaking after-all markers into user-visible results.

## Test Signals
Read-your-writes unit tests, atomic operation coalescing tests, conflict range tests, clear range/range read tests, unreadable range tests, and randomized transaction overlay tests are the main signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/fdbclient/include/fdbclient/WriteMap.h -->
