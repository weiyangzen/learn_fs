# sources/storage-engines/rocksdb/db/blob/blob_source_test.cc

## Purpose

This file is a focused unit test suite for `BlobSource`, the read-side component that opens blob files, reads blob records, decodes/decompresses values, interacts with the blob value cache, and exposes single-blob and multi-blob read helpers below the public `DB` API. It uses synthetic blob files written directly through `BlobLogWriter` so the tests can control offsets, sizes, compression, file numbers, and cache state without relying on full DB write paths.

The suite covers primary blob cache behavior, cache-only read tiers, compressed blobs, reads spanning multiple blob files, secondary cache promotion/demotion, error detail preservation after file refresh failures, and charged cache reservation accounting.

## Important APIs, Types, and Functions

- `WriteBlobFile(...)`: anonymous helper that creates a `.blob` file with a header, records, and footer. It optionally compresses each blob with the built-in compression manager, records blob offsets and compressed sizes, and is the fixture's persistence primitive.
- `BlobSourceTest`: `DBTestBase` fixture configuring `enable_blob_files`, a real LRU blob cache, `lowest_used_cache_tier = kVolatileTier`, DB identity/session IDs, and a separate `BlobFileCache`.
- `BlobSource::GetBlob`, `MultiGetBlob`, `MultiGetBlobFromOneFile`, `GetBlobFileReader`, and `TEST_BlobInCache`: core APIs under test.
- `BlobSecondaryCacheTest`: fixture with a small primary cache, compressed secondary cache, and `lowest_used_cache_tier = kNonVolatileBlockTier`.
- `BlobSourceCacheReservationTest`: fixture that wraps blob cache charging through `ChargedCache` and validates `ConcurrentCacheReservationManager` state.
- `OffsetableCacheKey`, `CacheKey`, `BlobContents`, `CacheHandleGuard<BlobFileReader>`, `PinnableSlice`, `BlobReadRequest`, and `BlobFileReadRequests` are the important data carriers.

## Control Flow

Most tests follow the same flow: configure options and cache, reopen the DB to obtain immutable/mutable CF options, write one or more blob files with known keys and values, create a `BlobFileCache`, construct `BlobSource`, and perform read sequences under different `ReadOptions`.

`GetBlobsFromCache` first reads with `fill_cache=false` and confirms no blob values are cached; then reads with `fill_cache=true` and verifies values are cached and pinned; then switches to `kBlockCacheTier` to prove cache-only reads succeed only while entries are resident. After erasing unreferenced entries, cache-only reads return `Incomplete`. A final missing-file path returns `IOError`.

`GetCompressedBlobs` writes Snappy-compressed records, confirms file reader compression metadata and compressed sizes, reads/decompresses from file while filling cache, then verifies later cache-only reads return uncompressed values without extra decompression time.

`MultiGetBlobsFromMultiFiles` and `MultiGetBlobsFromCache` build grouped read requests by file number, exercise batch reads, add a fake file request, and check per-request statuses rather than treating the batch as all-or-nothing.

The secondary cache test intentionally alternates two large blobs through an undersized primary cache, then inspects raw primary and secondary cache entries to validate dummy handles, promotion, and blob content materialization. The reservation tests read blobs with and without fill-cache, then assert reserved dummy-entry size and memory usage grow and shrink as cache entries are inserted and erased.

## State and Persistence Behavior

Persistent state is created as actual blob files in per-test CF paths. The helper writes valid blob log headers, records, and footers, so `BlobSource` observes normal on-disk metadata. Blob offsets and sizes are captured from the writer and reused as exact lookup coordinates.

Transient state includes primary blob cache entries keyed by DB identity, DB session, blob file number, and offset; secondary cache entries; blob file reader cache handles; `PinnableSlice` pinning; perf-context counters; and statistics tickers. Tests explicitly reset perf context and statistics between phases to isolate cache hits, misses, adds, bytes read, bytes written, checksum time, decompression time, and filesystem read counters.

The reservation fixture validates that blob cache memory is charged through `ChargedCache` and that dummy reservation size is released when the last blob cache entry is erased through the wrapper.

## Dependencies

The tests depend on RocksDB internals: `db/blob/blob_source.h`, `BlobFileCache`, `BlobFileReader`, `BlobLogWriter`, `BlobLogRecord`, `BlobLogHeader`, `BlobLogFooter`, compression helpers, `CompressedSecondaryCache`, `ChargedCache`, `DBTestBase`, filename utilities, and perf/statistics infrastructure. Snappy-specific tests skip when Snappy is unavailable.

## Integration Points

Although the tests instantiate `BlobSource` directly, they model the read behavior used by higher-level DB `Get`, iterator, MultiGet, and compaction code. They verify the boundary between blob file reader cache and blob value cache, the cache key format shared with secondary cache, `ReadOptions::read_tier` semantics, and the DB identity/session scoping used to avoid cache key collisions across DB lifetimes.

## Risks

- Cache counter assertions are detailed and can become brittle if cache lookup ordering changes, even when user-visible behavior remains correct.
- The tests depend on hand-computed file sizes and record byte counts; changes to blob log record encoding or footer/header size require updates.
- Secondary cache behavior relies on dummy-handle implementation details and raw cache lookups, so it can fail on internal cache refactors.
- Error preservation tests require the first read to populate/open a file and a later deleted-file refresh path to combine corruption and I/O details correctly.
- Compression tests use compressed sizes as read inputs; any compression framing or manager behavior change can alter expected size comparisons.

## Test Signals

Strong signals include exact `Status` categories (`OK`, `Incomplete`, `IOError`, `Corruption`), returned value equality, `PinnableSlice::IsPinned`, `TEST_BlobInCache`, perf-context counters, `BLOB_DB_CACHE_*` ticker counts, secondary cache hit/promotion state, and charged cache reservation sizes. These tests are especially useful when changing `BlobSource`, blob cache admission, secondary cache integration, blob file reader refresh, or blob log format accounting.
