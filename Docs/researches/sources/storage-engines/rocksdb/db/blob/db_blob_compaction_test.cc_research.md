# sources/storage-engines/rocksdb/db/blob/db_blob_compaction_test.cc

## Purpose

This file tests compaction behavior when values are stored in blob files. It verifies when compaction can decide using blob indexes only, when it must read blob values, when it writes replacement blob records, how blob garbage is tracked, and how blob reads are optimized during compaction with readahead and cache bypass.

The tests are built around custom `CompactionFilter` implementations that use different decision APIs (`FilterBlobByKey` and `FilterV2`) and different decisions (`kKeep`, `kRemove`, `kChangeValue`, `kRemoveAndSkipUntil`, invalid blob decisions, and errors).

## Important APIs, Types, and Functions

- `DBBlobCompactionTest::GetCompactionStats()`: reaches into `VersionSet`, default `ColumnFamilyData`, and `InternalStats` to inspect per-level compaction blob bytes.
- `FilterByKeyLength`: removes blob-backed entries based only on key length using `FilterBlobByKey`.
- `FilterByValueLength`: removes based on materialized value length through `FilterV2`.
- `BadBlobCompactionFilter`: returns unsupported decisions to validate error handling.
- `ValueBlindWriteFilter`: writes a new value from `FilterBlobByKey` without reading the old blob.
- `ValueMutationFilter`: reads existing values through `FilterV2` and appends padding.
- `AlwaysKeepFilter`, `SkipUntilFilter`, and `ReadBlobCompactionFilter`-style behavior validate keep, skip-until iteration, and read-blob paths.
- Sync points observe blob-index tampering, `BlobCountingIterator` in-flow processing, and non-prefetch blob reads.

## Control Flow

The tests generally enable blob files, set `min_blob_size`, install a compaction filter, write keys, flush, run `CompactRange`, then verify user-visible values and internal blob byte stats.

Key-only filtering removes entries without reading or writing blob files, so `bytes_read_blob` and `bytes_written_blob` remain zero. Value-based filtering reads blob values and removes short ones, so read bytes increase while write bytes stay zero. Blind writes produce replacement blob records without reading old blob values. Value mutation reads old blobs and writes new blobs.

`BlobCompactWithStartingLevel` uses an SST partitioner to force multiple output table files and checks that blob files are created only when compaction output reaches `blob_file_starting_level`.

`TrackGarbage` writes two flush generations, overwrites two keys, compacts, then inspects `VersionStorageInfo::GetBlobFiles()` metadata to confirm old blob records are marked garbage while newer records remain live.

Readahead tests enable `blob_compaction_readahead_size` and use sync points to assert compaction paths that need blob values avoid non-prefetch reads. `CompactionDoNotFillCache` confirms compaction blob reads do not populate the blob cache.

## State and Persistence Behavior

Compaction rewrites table metadata and can update blob file metadata without always rewriting blob files. Some filters remove table references, making existing blob records garbage. Other filters write replacement blob records and produce new blob files or new records. `TrackGarbage` directly validates durable version metadata for total blob count, total blob bytes, garbage blob count, and garbage blob bytes.

Starting-level behavior controls when values remain inline in compaction output versus being written to blob files. Readahead state is transient read buffering during compaction and should not alter cache state.

## Dependencies

The file depends on `BlobIndex`, `BlobLogRecord`, DB test utilities, `InternalStats`, `VersionSet`, `VersionStorageInfo`, compaction filters, merge operators, SST partitioners, and sync points. It uses direct internal metadata access rather than only public properties.

## Integration Points

These tests protect the integration between blob indexes and the compaction iterator, compaction filters, merge resolution, blob garbage collection, blob file metadata, blob compaction readahead, and cache admission policy. They also validate that unsupported compaction-filter decisions for blob paths fail as `NotSupported` rather than silently corrupting data.

## Risks

- Blob byte counters depend on precise record-size accounting via `BlobLogRecord::CalculateAdjustmentForRecordHeader`.
- `FilterBlobByKey` paths must not accidentally materialize blob values, or key-only compactions become unnecessarily expensive.
- `FilterV2` paths must receive materialized values for blob-backed entries and must not see `kBlobIndex` when a normal value is expected.
- Unsupported decisions such as `kChangeBlobIndex` and `kIOError` from filter paths must fail cleanly.
- Readahead regressions may preserve correctness but cause extra non-prefetch reads, hurting compaction performance.
- Compaction reads should not fill the blob cache; doing so can pollute user read caches.

## Test Signals

Important signals include final `Get` results, `CompactRange` statuses (`OK`, `NotSupported`, `Corruption`), per-level `bytes_read_blob` and `bytes_written_blob`, blob file counts, table file counts by level, blob file metadata totals and garbage counts/bytes, sync-point counters for in-flow skip handling and non-prefetch reads, and `BLOB_DB_CACHE_ADD` remaining zero during compaction.
