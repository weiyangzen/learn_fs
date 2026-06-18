<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job.go

## Purpose
This file implements sparse/chunked read support for `Job`. Instead of downloading a full object prefix, it checks whether requested byte ranges are already cached, downloads missing configured chunks, tracks in-flight chunks to avoid duplicate work, updates sparse `FileInfo.DownloadedChunks`, and returns whether the cache can satisfy the read.

## Important APIs and functions
`HandleSparseRead` is the public sparse path. It retrieves `FileInfo`, checks `DownloadedChunks.ContainsRange`, computes missing chunks through `getChunksToDownload`, downloads missing chunks in an `errgroup`, waits for already-in-flight chunks, and verifies the requested range. `downloadSparseRange` downloads a byte range, writes it to the cache file using `io.NewOffsetWriter`, updates `DownloadedChunks`, and calls `lru.Cache.UpdateSize` with only newly added bytes.

## Control flow and state behavior
Missing chunks are computed from `ByteRangeMap.GetMissingChunks`. `job.inflightChunks` maps chunk IDs to close-on-completion channels and is protected by `job.mu`. New chunks are marked in-flight before goroutines start; duplicate callers receive wait channels instead of launching duplicate downloads. After all download attempts finish, the initiator closes and deletes its chunk channels. Sparse file-info entries use `Offset` as a max-uint sentinel elsewhere, while actual cached data is represented by `DownloadedChunks`.

## Dependencies and integration points
The sparse path depends on `data.ByteRangeMap`, `data.FileInfo`, LRU lookup/update-size APIs, `gcs.Bucket.NewReaderWithReadHandle`, random-read metrics, `errgroup`, the shared global semaphore, logger, and the cache file created by higher-level cache-handler code. It integrates with `CacheHandler` sparse initialization, which allocates the byte-range map and sets sentinel offsets.

## Risks and edge cases
`HandleSparseRead` downloads full missing chunks, not just the requested byte range, so object-size capping in `downloadSparseRange` is important. If a download fails, cleanup still closes in-flight channels, so waiters can continue and then verify cache state. `downloadSparseRange` opens an existing file with `O_WRONLY`; missing local files surface as errors. `UpdateSize` intentionally can push LRU current size past max until a later insert, so sparse growth eviction is deferred.

## Test signals
Sparse tests cover chunk-boundary calculation, invalid ranges, in-flight chunk deduplication, direct sparse range download and byte-range tracking, cache-hit fast path, and downloading missing chunks before verifying requested reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job.go -->
