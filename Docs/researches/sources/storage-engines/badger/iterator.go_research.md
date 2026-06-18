# sources/storage-engines/badger/iterator.go

## Purpose
`iterator.go` implements Badger `Item`, iterator options, and `Iterator` behavior. It is the core read path for scanning MVCC keys across pending writes, memtables, and SST levels while handling value-log pointers, prefetching, versions, deletes, expiry, prefixes, banned namespaces, and reverse iteration.

## Important APIs, Types, and Functions
- `Item`: reusable iterator result with key, value pointer or inline value, version, expiry, metadata, prefetch state, and transaction pointer.
- Item methods: `Key`, `KeyCopy`, `Version`, `Value`, `ValueCopy`, `IsDeletedOrExpired`, `DiscardEarlierVersions`, `EstimatedSize`, `KeySize`, `ValueSize`, `UserMeta`, `ExpiresAt`, `String`.
- Internal item helpers: `yieldItemValue`, `prefetchValue`, `hasValue`, `runCallback`.
- `IteratorOptions`: `PrefetchSize`, `PrefetchValues`, `Reverse`, `AllVersions`, `InternalAccess`, `Prefix`, `SinceTs`, and internal `prefixIsKey`.
- Table filtering: `compareToPrefix`, `pickTable`, `pickTables`.
- `DefaultIteratorOptions`.
- `Iterator`: merge iterator wrapper with item reuse lists, last-key tracking, scan accounting, optional `ThreadId`, and allocator.
- Iterator constructors and methods: `Txn.NewIterator`, `Txn.NewKeyIterator`, `Item`, `Valid`, `ValidForPrefix`, `Close`, `Next`, `Seek`, `Rewind`, plus internal `parseItem`, `fill`, `hasPrefix`, `prefetch`.

## Control Flow and State
`NewIterator` increments transaction iterator count, snapshots pending writes/memtables/level iterators, increments value-log iterator count, and merges all iterators. `Seek` clears prefetched data, sets timestamp-adjusted seek keys, and prefetches. `Next` waits for current item prefetch, recycles it, and parses until a visible item is found. `parseItem` filters internal keys, future versions, `SinceTs`, banned namespaces, duplicate older versions, deletes, and expiry. Reverse iteration has special handling because keys store timestamps descending.

## Persistence Behavior
The iterator does not persist state but reads persisted SST and value-log data. `yieldItemValue` decodes `valuePointer` and reads from `db.vlog`; inline values are copied from `ValueStruct`. `Close` decrements value-log iterator count, which can matter for value-log GC and file lifecycle.

## Dependencies and Integration Points
Integrates with transactions, pending write iterators, memtables, `levelsController.appendIterators`, table merge/concat iterators, value-log reads, namespace banning, metrics, and Badger key/timestamp helpers in `y`. It depends on `table`, `z.Allocator`, `crc32`, `math`, `sort`, `sync`, and `time`.

## Risks and Edge Cases
Items are reused; `Key` and `Value` lifetimes are limited until `Next`, iterator close, or transaction end. Async value prefetch uses goroutines and must be waited on during `Close` to avoid leaks. `yieldItemValue` logs value-log read errors and returns nil error, which can hide corruption from callers. Empty or incorrect prefix handling can over-scan; reverse iteration is particularly subtle around versions and deletes.

## Test Signals
Covered by broad iterator tests in `db_test.go` and focused tests in `iterator_test.go`: prefix/table picking, `SinceTs`, pending writes, read-only empty DB, benchmarked key prefix lookup, reverse iteration, prefetch size, deleted/expired skipping, namespace bans, and concurrent iterator behavior.
