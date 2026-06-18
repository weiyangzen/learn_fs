# Research: sources/storage-engines/rocksdb/include/rocksdb/iterator.h

## Purpose

`iterator.h` defines the public `Iterator` interface for ordered key/value traversal over RocksDB data sources such as DBs, column families, tables, and composed internal iterators. It extends `IteratorBase` with value access, wide-column access, iterator properties, timestamps, and MultiScan preparation.

## Important APIs, Types, and Functions

`Iterator` inherits from `IteratorBase` and adds pure virtual `value()`, virtual `columns()`, `GetProperty(std::string, std::string*)`, `timestamp()`, and `Prepare(const MultiScanArgs&)`. It also declares factory helpers `NewEmptyIterator()` and `NewErrorIterator(const Status&)`. Documented properties include `rocksdb.iterator.is-key-pinned`, `rocksdb.iterator.is-value-pinned`, `rocksdb.iterator.super-version-number`, `rocksdb.iterator.internal-key`, and `rocksdb.iterator.write-time`.

## Control Flow

Normal iteration flow is inherited from `IteratorBase`: seek, check `Valid()`, read `key()` and `value()` or `columns()`, advance with `Next()` or `Prev()`, and finally inspect `status()`. `Prepare()` is an optional optimization path for MultiScan-style workloads: callers provide scan ranges, implementation prefetches relevant blocks, and then callers seek to each range start in order. If subsequent seeks diverge from the prepared scan sequence, implementations should disregard prepared state until `Prepare()` is called again.

## State and Persistence Behavior

The header defines no storage itself. Implementations hold snapshots, pinned blocks, table-reader state, prepared scan state, and buffers for key/value/column slices. Returned `Slice` and `WideColumns` references are valid only until the next iterator modification unless a property reports pinned lifetime. `timestamp()` is virtual and defaults to an assertion failure because only timestamp-aware iterators should expose it.

## Dependencies and Integration Points

The header depends on `iterator_base.h`, `options.h`, and `wide_columns.h`. It is consumed across table iterators, DB iterators, merging iterators, external table iterators, BlobDB, secondary index utilities, Java bindings, and `multi_scan.h`. The implementation of `NewEmptyIterator` and `NewErrorIterator` lives in `table/iterator.cc`.

## Risks and Edge Cases

The default `columns()` and `timestamp()` assert false, so callers must only use them when the implementation contract says they are supported. Slice lifetimes are short unless pinning is guaranteed. `GetProperty` support is implementation-specific. Prepared MultiScan state depends on ordered seeks and correct upper bounds; HISTORY entries show recent bugs around MultiScan upper bounds, unpinning, and limit handling. Wide-column conversion must preserve default anonymous column semantics.

## Test Signals

Tests in `table/table_test.cc` and related DB iterator suites validate `PrepareValue`, BlobDB on-demand value loading, pinned key/value properties, MultiScan prefetch, wide-column scan/dump behavior, and error iterators. Failures surface as invalid iterators, non-OK status, wrong key/value order, assertion failures in unsupported accessors, or stale slice use.
