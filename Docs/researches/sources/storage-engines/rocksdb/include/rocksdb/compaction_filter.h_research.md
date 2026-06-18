# sources/storage-engines/rocksdb/include/rocksdb/compaction_filter.h

## Purpose

`compaction_filter.h` defines the public extension point for application logic that inspects, drops, or rewrites records during table-file creation, especially compaction. It also introduces wide-column and blob-aware filtering support, including lazy blob-column resolution so filters can avoid unnecessary blob file IO. A companion `CompactionFilterFactory` creates per-table-creation filter instances based on context.

## Important APIs, Types, and Functions

`WideColumnBlobResolver` is an abstract interface with `ResolveColumn`, `ResolveColumns`, `IsBlobColumn`, and `NumColumns`. Its contract says resolved slices remain valid until `FilterV4` returns and resolver instances are single-compaction-thread objects.

`CompactionFilter` derives from `Customizable`. It defines `ValueType` values for plain values, merge operands, legacy BlobDB blob indexes, and wide-column entities. Its `Decision` enum includes `kKeep`, `kRemove`, `kChangeValue`, `kRemoveAndSkipUntil`, internal legacy blob decisions, `kPurge`, `kChangeWideColumnEntity`, and `kUndetermined` for key-only blob filtering. `BlobDecision` remains for internal stacked BlobDB use. `Context` exposes table-creation metadata: full/manual compaction flags, input start level, column family id, creation reason, and input table properties.

The filtering API is layered for compatibility. Old code can override `Filter` for plain key/value records and `FilterMergeOperand` for merge operands. `FilterV2` unifies plain values and merge operands and defaults to the older functions. `FilterV3` adds wide-column entities and defaults to keeping wide columns while delegating other types to `FilterV2`. `FilterV4` adds `WideColumnBlobResolver` and defaults to `FilterV3`. `SupportsFilterV4()` defaults false to force eager resolution for backward compatibility. `FilterBlobByKey` lets integrated BlobDB filters make decisions based on key without reading the blob value.

`CompactionFilterFactory` derives from `Customizable`, provides `ShouldFilterTableFileCreation(TableFileCreationReason)`, and creates a `std::unique_ptr<CompactionFilter>` from a `CompactionFilter::Context`. The default `ShouldFilterTableFileCreation` preserves old behavior by filtering only compaction-created files.

## Control Flow

During table-file creation, RocksDB decides whether to use a filter. A single `Options::compaction_filter` can be shared across threads, or a factory can create one filter per table-creation thread. The table builder/compaction/flush paths pass records through the filter before writing output. The filter returns a `Decision`, and RocksDB keeps, removes, rewrites, purges, converts to wide-column entity, or skips a key range according to that decision.

The versioned API flow is fallback-based. If a filter only overrides `Filter`, `FilterV2` adapts bool/value_changed outputs to `Decision`; `FilterV3` and `FilterV4` delegate down. If a filter overrides `FilterV4` and returns `SupportsFilterV4() == true`, wide-column blob values can be resolved lazily; otherwise blob-backed columns are eagerly fetched before legacy filtering. `FilterBlobByKey` runs before value-based filtering for blob-backed values when a key-only decision is possible; `kUndetermined` resumes the normal value path.

## State and Persistence Behavior

Compaction filters can permanently change durable DB contents by removing entries, rewriting values, changing wide-column entities, emitting tombstones, single-delete tombstones, or dropping ranges from output table files. The header explicitly warns that snapshots do not preserve repeatable reads in the presence of compaction filters; filtered data can disappear from snapshot views after a new table file is installed. It also notes that `IgnoreSnapshots()` is deprecated and false is unsupported.

Filter objects can hold application state, but if a single filter instance is configured directly it must be thread-safe under multithreaded compaction. Factory-created filters are per table-creation thread, reducing thread-safety burden while allowing multiple concurrent instances. Blob resolver state is transient and valid only during a `FilterV4` call.

## Dependencies and Integration Points

The header depends on `customizable.h`, `table_properties.h`, `types.h`, and `wide_columns.h`, with forward declarations for `Slice` and `SliceTransform`. Integration points include `Options::compaction_filter`, `Options::compaction_filter_factory`, table builder code, flush job code, compaction iterator/merge helper logic, BlobDB integrated compaction, wide-column storage, and config-string customization. Search signals show creation in `db/builder.cc` and `db/flush_job.cc`, compaction stats integration in `db_impl_compaction_flush.cc`, and many blob/wide-column tests under `db/blob/db_blob_index_test.cc` and `db/blob/db_blob_compaction_test.cc`.

## Risks and Edge Cases

This is a correctness-sensitive API. Incorrect `kRemove`, `kPurge`, or `kRemoveAndSkipUntil` decisions can delete data or expose older values. The header highlights TransactionDB risks when filtering merge operands: conflicts may be missed, so merge filtering should usually live in the merge operator. `kRemoveAndSkipUntil` ignores snapshots, can expose overwritten older values, does not work with PlainTable prefix mode, and has compaction readahead implications. Unsupported internal decisions must not be returned by applications.

Exception propagation from overridden methods is forbidden because RocksDB is not exception-safe. `FilterV4` lazy resolution errors must be handled conservatively: the header recommends returning `kKeep` for the current entry and allowing RocksDB to fail compaction after the resolver error is surfaced. A filter claiming `SupportsFilterV4()` without handling resolver semantics can change IO and correctness behavior. Thread safety differs sharply between direct filters and factory-created filters.

## Test Signals

Direct signals include `db/blob/db_blob_compaction_test.cc` for `FilterBlobByKey`, blob filtering, invalid decisions, and value mutation; `db/blob/db_blob_index_test.cc` for plain blob FilterV4, lazy wide-column blob resolution, resolver error paths, FilterV3 fallback, and TTL-based entity dropping; `db_stress_tool/db_stress_compaction_filter.h` for stress coverage of FilterV3/FilterV4 paths; and Java compaction filter tests for binding-level integration. Flush and builder code paths should be checked when changing factory decisions because filters can now apply outside ordinary compaction depending on `ShouldFilterTableFileCreation`.
