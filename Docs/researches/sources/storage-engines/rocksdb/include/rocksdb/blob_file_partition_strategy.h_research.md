# sources/storage-engines/rocksdb/include/rocksdb/blob_file_partition_strategy.h

## Purpose
`blob_file_partition_strategy.h` defines the callback interface used by RocksDB blob direct write to choose a blob-file partition for each value or wide-column entity. It lets applications control partition placement while keeping the caller responsible for mapping the returned value into the configured partition count.

## Important APIs, Types, And Functions
`BlobFilePartitionStrategy` is an abstract base class with a virtual destructor, `Name()`, and two `SelectPartition` overloads. `Name()` returns a debug/logging identifier. The primary overload takes `num_partitions`, `column_family_id`, `key`, and a plain `Slice value`, and returns a `uint32_t` selector. The caller applies modulo `num_partitions`.

The wide-column overload takes `num_partitions`, `column_family_id`, `key`, and `const WideColumns& columns`. The default implementation chooses the default wide column value when present, otherwise the first column value, otherwise an empty `Slice`, then delegates to the plain-value overload. The comments remind derived classes that override only the Slice overload to add `using BlobFilePartitionStrategy::SelectPartition;` so the wide-column overload remains visible.

## Control Flow
The strategy is called on the write hot path for blob direct writes and can be called concurrently from multiple writer threads. For regular Put/Merge-style value separation, RocksDB calls the Slice overload. For `PutEntity()` wide-column separation, RocksDB calls the wide-column overload once per entity before writing any blob-backed columns, then reuses the chosen partition for all blob-backed columns in that entity.

The default wide-column control flow scans columns for `kDefaultWideColumnName`; if not found and the entity is non-empty, it uses `columns.front().value()`. Empty entities pass an empty `Slice` to the Slice overload. No modulo operation is performed by the strategy implementation in this header; the internal caller normalizes the returned selector.

## State And Persistence Behavior
The interface permits implementations to keep internal state, but it warns that any mutation must be synchronized because calls are concurrent. Implementations should avoid I/O, callbacks into RocksDB APIs, blocking operations, and expensive work because they execute on the write path.

The strategy object itself is an application-supplied callback, not a serialized OPTIONS object. As described by `advanced_options.h`, applications relying on custom partitioning must provide the strategy again on every DB open. Persistent blob placement is affected by the returned partition choices, but the strategy's state and code are not persisted by RocksDB.

## Dependencies And Integration Points
The header includes `rocksdb/rocksdb_namespace.h` and `rocksdb/wide_columns.h`, and forward-declares `Slice`. It depends on `WideColumns`, `WideColumn` accessors, `kDefaultWideColumnName`, and `Slice`.

Its primary integration point is `AdvancedColumnFamilyOptions::blob_direct_write_partition_strategy`, used when `enable_blob_direct_write` is enabled. It also integrates with wide-column `PutEntity()` handling by ensuring all blob-backed columns in one entity share a partition.

## Risks
The biggest correctness risks are write-path latency, thread safety, and exception safety. A slow or blocking strategy directly slows writers. Unsynchronized mutable state can race across writer threads. Exceptions must not escape into RocksDB because RocksDB is not exception-safe.

Partition determinism can matter operationally. Changing the strategy between opens or deploying different strategy implementations across processes changes future blob placement and can affect load distribution. Returning arbitrary large values is allowed, but callers must handle modulo correctly and implementations should still consider `num_partitions` to avoid pathological skew.

The wide-column overload has a C++ name-hiding pitfall: a derived class that overrides only the Slice overload without a `using` declaration hides the base overload. That can produce surprising compile-time or dispatch behavior for wide-column calls.

## Test Signals
Tests should verify default wide-column delegation with default column, first-column fallback, and empty-column fallback. Custom strategies should be tested for modulo behavior at the caller, concurrent invocation safety, deterministic placement, no exception propagation, and visibility of both overloads when derived classes override one or both methods. Blob direct write tests should confirm one partition selection per `PutEntity()` and reuse across all blob-backed columns.
