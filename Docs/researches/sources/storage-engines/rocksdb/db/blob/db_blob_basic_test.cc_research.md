# sources/storage-engines/rocksdb/db/blob/db_blob_basic_test.cc

## Purpose

This file is the main end-to-end DB test suite for integrated blob-file behavior. Unlike `blob_source_test.cc`, it exercises public `DB` APIs and DB-internal paths that produce, read, cache, merge, trace, recover, and size blob-backed values. It validates that blob indexes stored in SSTs are transparent to users while preserving correct error statuses and cache semantics.

The coverage spans `Get`, iterators, `MultiGet`, direct I/O multi-read ordering, multiple blob files, corrupt blob indexes, inlined TTL blob indexes, missing files, IO tracing, best-efforts recovery, merge operands, DB properties, blob cache prepopulation, secondary cache, wide-column `GetEntity`, timestamped reads, and approximate-size accounting.

## Important APIs, Types, and Functions

- `DBBlobBasicTest`: base fixture using `DBTestBase`.
- `DBBlobBasicIOErrorTest` and `DBBlobBasicIOErrorMultiGetTest`: parameterized fixtures using `FaultInjectionTestEnv` and sync points for blob open/read failures.
- `DBBlobWithTimestampTest`: timestamp-aware fixture using `DBBasicTestWithTimestampBase` and `TestComparator`.
- Public APIs under test: `Put`, `Flush`, `Get`, `MultiGet`, `NewIterator`, `PrepareValue`, `GetEntity`, `MultiGetEntity`, `CompactRange`, `IngestExternalFile`, `StartIOTrace`, `EndIOTrace`, `GetProperty`, `GetIntProperty`, `GetApproximateSizes`, and dynamic `SetOptions`.
- Internal helpers and types: `BlobIndex`, `WriteBatchInternal::PutBlobIndex`, `BlobLogRecord`, `BlobFilePartitionManager`, `BlobLogSequentialReader`, `RandomAccessFileReader::MultiRead`, `SyncPoint`, trace reader/writer types, and file-name parsing.

## Control Flow

Most tests enable blob files, choose `min_blob_size`, write values, flush to produce SSTs containing blob indexes plus blob files, and then use a public read path to verify transparent value reconstruction. Cache-focused tests alternate `ReadOptions::fill_cache` and `read_tier` to prove blob values are unavailable in cache-only mode until explicitly cached.

Iterator tests cover forward and backward movement, cache pinning on blob values only, and `allow_unprepared_value`, where keys can be positioned before blob values are fetched and `PrepareValue()` performs the actual blob read.

`MultiGetWithDirectIO` constructs a layout where keys from different levels refer to offsets in the same blob file out of offset order. A sync point asserts that blob multi-read requests are sorted before direct I/O alignment so the filesystem sees one merged aligned request.

Error tests tamper with blob indexes, inject filesystem errors at blob open/read sync points, or simulate table-cache `FindTable` errors. They assert precise per-key statuses and ensure raw blob handles are not leaked as values after partial failures.

Later tests validate cache warmup during flush, runtime disabling of `prepopulate_blob_cache`, secondary cache promotion, wide-column entity reads backed by blobs, timestamped blob values and merges, and approximate sizes with optional blob-file inclusion.

## State and Persistence Behavior

These tests create real RocksDB state: WAL/write batches, SST files with blob indexes, blob files, table cache entries, blob cache entries, secondary cache entries, properties derived from version metadata, and optional IO trace files. `Flush` is the main persistence boundary for creating blob files. `CompactRange` updates live version metadata, garbage accounting, and sometimes blob file liveness.

Cache state is intentionally manipulated with shared LRU caches, small cache capacities, and `read_tier`. Some tests hold iterators open to keep old versions alive, proving `kTotalBlobFileSize` counts blob files across live versions without double-counting shared files.

Best-efforts recovery deletes the newest blob file after flushing two table/blob pairs and verifies reopening with `best_efforts_recovery` can fall back to an older value.

## Dependencies

The suite depends on RocksDB DB test utilities, blob index/log formats/readers, block-based table cache options, compressed secondary cache, file naming, random access file readers, trace reader/writer utilities, replay support, sync points, compression helpers, fault injection env, merge operators, and timestamp comparator test utilities.

Some tests depend on platform support, especially direct I/O. The direct I/O test skips when reopening with `use_direct_reads` returns `InvalidArgument`.

## Integration Points

This file is a broad integration harness for blob files across the DB stack: write path blob creation, SST blob-index lookup, version-level `Get` and `MultiGetBlob`, iterators, merge resolution, compaction filters, table cache errors, IO tracing, cache prepopulation during flush, secondary cache, timestamped APIs, DB properties, and approximate-size estimation.

It also protects interactions with external SST ingest and bottommost-level compaction, ensuring blob reads still work when table levels and blob file offsets are not naturally aligned by user key order.

## Risks

- Many tests assert exact status classes. Reclassifying errors between `Incomplete`, `IOError`, `Corruption`, and `Aborted` can break compatibility.
- Direct I/O request ordering is subtle; unsorted blob offsets can increase I/O count or violate alignment assumptions.
- `allow_unprepared_value` changes iterator validity after `PrepareValue()` failures, so iterator state transitions are easy to regress.
- Empty values must remain inline even with `min_blob_size = 0`; storing them as blobs can waste space and break secondary cache paths.
- Cache prepopulation must happen during flush but not compaction, and runtime option changes must take effect for later flushes.
- Timestamped iteration combines internal keys, user timestamps, blob values, and bounds; comparator or iterator changes can disturb ordering.

## Test Signals

High-value signals include cache-only `Incomplete` reads before blob caching, successful cache-only reads after fill-cache or flush prepopulation, exact merge results, corruption from malformed blob indexes, IOError preservation under injected filesystem failures, direct I/O aligned request count, `BLOB_DB_CACHE_*` and `SECONDARY_CACHE_HITS` ticker counts, DB blob property strings and integer properties, IO trace records containing blob file operations, and approximate sizes increasing when `include_blob_files` is enabled.
