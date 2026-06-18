<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_source.cc

## Purpose
Implements `BlobSource`, the high-level access layer for blob values. It combines blob value cache lookup, blob file reader cache lookup, on-disk reads, optional cache population, cache handle pinning, multiget batching, and stale-reader refresh on corruption.

## Important APIs, Types, and Functions
The constructor configures the shared typed blob cache and optionally wraps it in `ChargedCache` when block-based cache charging is enabled. `GetBlobFromCache`, `PutBlobIntoCache`, `GetEntryFromCache`, and `InsertEntryIntoCache` isolate cache access. `PinCachedBlob` transfers cache handle ownership to a `PinnableSlice`; `PinOwnedBlob` pins heap-owned contents with a cleanup callback. `GetBlob` reads one blob through cache then file. `MultiGetBlob` dispatches per-file groups, while `MultiGetBlobFromOneFile` handles cache hits, file multireads, refresh retries, cache insertion, and result pinning.

## Control Flow
Single reads compute a cache key from db id/session/file/offset, try the blob cache, obey `kBlockCacheTier` by returning incomplete on misses, then use a cached `BlobFileReader`. If file read returns corruption, the cached reader is evicted, an uncached fresh reader is opened, and the read is retried; successful retries refresh the reader cache. Multiget first sorts each file group, services cache hits, marks cache-only misses as incomplete when no I/O is allowed, reads remaining misses from one file, retries only corrupted requests with a fresh reader, optionally installs that reader, then fills or owns result buffers.

## State and Persistence Behavior
`BlobSource` itself is mostly read-only after construction, but it mutates blob cache contents and blob file reader cache state. Cache keys intentionally use DB id, session id, file number, and offset. Bytes-read outputs report on-disk compressed record bytes for consistency even when values come from cache. Persistent blob files are not modified.

## Dependencies and Integration Points
The implementation depends on typed/shared cache interfaces, charged cache, blob contents/cache/file reader/log format, cache reservation support, block-based table options, get/multiget context limits, statistics counters, and RocksDB mutable/immutable options. It is the bridge used by point lookups, multigets, iterators, and version blob reads.

## Risks and Edge Cases
Cache handle pinning transfers ownership, so cleanup lifetimes must be correct. `kBlockCacheTier` only succeeds on cache hits; misses must not open blob files. Corruption retry must preserve original corruption details while appending refresh failures when retry cannot prove the cached reader was stale. Multiget uses a `uint64_t` bit mask, so it relies on the batch size not exceeding mask width and `MultiGetContext::MAX_BATCH_SIZE`. Cache insertion failures are propagated after successful disk reads, meaning a read can fail because cache population failed.

## Test Signals
No companion test appears in this subset, but expected tests include cache hit/miss accounting, no-I/O read tier behavior, fill-cache on/off pinning, stale cached-reader refresh for single and multiget reads, partial multiget corruption retry, charged cache usage, and cache-key session isolation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.cc -->
