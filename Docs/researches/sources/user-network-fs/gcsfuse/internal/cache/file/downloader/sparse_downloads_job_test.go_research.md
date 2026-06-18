<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job_test.go

## Purpose
This ogletest suite validates sparse downloader behavior around chunk selection, duplicate in-flight work, sparse range downloads, and `HandleSparseRead` cache-hit outcomes.

## Important fixtures and APIs
`sparseDownloaderTest` embeds `downloaderTest` and configures experimental chunk cache, 20 MiB sparse chunks, CRC enabled, and experimental parallel default. Tests manually create sparse `data.FileInfo` values with `data.NewByteRangeMap` and max-uint offsets to mirror `CacheHandler` sparse initialization.

## Control flow and state behavior
`Test_getChunksToDownload` covers aligned and unaligned ranges, end capping, and invalid offset ranges. `Test_getChunksToDownload_WithInflight` pre-populates `job.inflightChunks` and asserts that already-running chunks produce wait channels while other chunks are newly marked in-flight. `Test_DownloadRange` creates the local file and sparse file-info entry, downloads `[10 MiB, 30 MiB)`, checks file bytes, and verifies `DownloadedChunks.ContainsRange`.

## Dependencies and integration points
The tests rely on fake storage, cache utility file creation, `data.ByteRangeMap`, LRU insertion and lookup without changing order, and random byte generation. They validate sparse code but also exercise `lru.UpdateSize` indirectly during `downloadSparseRange`.

## Risks and edge cases
The test named `HandleSparseRead_NeedsDownload` expects a request `[15 MiB, 25 MiB)` to download chunks covering `[0, 40 MiB)`, proving chunk expansion rather than exact-range download. The suite does not cover download failure cleanup, waiter context cancellation, or concurrent callers racing through `HandleSparseRead`; those remain risk areas for in-flight channel handling.

## Test signals
Signals include chunk ID calculation for unaligned reads, invalid range rejection, in-flight chunk deduplication, sparse file writes at offsets, byte-range map mutation, pre-downloaded cache hits, and post-download cache-hit verification with content validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job_test.go -->
