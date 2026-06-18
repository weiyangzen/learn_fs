<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.h -->
# sources/storage-engines/rocksdb/db/blob/blob_source.h

## Purpose
Declares `BlobSource`, the unified blob value retrieval interface above blob value cache, blob file reader cache, and storage.

## Important APIs, Types, and Functions
Public methods include `GetBlob`, `MultiGetBlob`, `MultiGetBlobFromOneFile`, `GetBlobFileReader`, `GetBlobCache`, `TEST_BlobInCache`, and typed-cache `Create`. Private helpers manage cache lookup/insert, pinning cached or owned contents into `PinnableSlice`, typed cache access, and cache key construction.

## Control Flow
Callers pass BlobIndex-derived file number, offset, file size, stored value size, and compression type. `BlobSource` first uses blob cache when available, then falls back to file readers if the read tier allows disk I/O. Multiget callers supply requests grouped by blob file; the source sorts within each file and delegates to the single-file path.

## State and Persistence Behavior
The class stores references to DB id/session id strings, statistics, blob file cache, a mutable typed shared blob cache interface, and the lowest cache tier used. It does not own the id strings or file cache. Cache keys are offsetable and session-scoped to avoid reuse across DB sessions.

## Dependencies and Integration Points
The header depends on cache key and typed cache infrastructure, `BlobContents`, `BlobFileCache`, `BlobReadRequest`, RocksDB cache APIs, `CachableEntry`, and `autovector`. It is used by version/read paths and tests that need blob cache visibility.

## Risks and Edge Cases
Lifetime of referenced `db_id`, `db_session_id`, and `blob_file_cache` must exceed the source. `TEST_BlobInCache` is test-only but still performs real cache lookup and can affect stats through `GetBlobFromCache`. The `file_size` parameter is currently not used in cache keys, so offset uniqueness relies on file number/session/offset.

## Test Signals
Expected coverage should validate single and multiget reads through cache and file, cache charge reporting, no-disk read tier, reader refresh on corruption, and result pinning lifetimes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_source.h -->
