# sources/storage-engines/rocksdb/table/block_fetcher.cc

Purpose: implements `BlockFetcher`, the central low-level path for retrieving one physical block from prefetch buffers, persistent cache, or file IO; verifying its trailer; optionally decompressing it; and returning `BlockContents` with correct ownership.

Important APIs/types/functions: helper methods include `ProcessTrailerIfPresent`, persistent-cache lookups/inserts for serialized and uncompressed blocks, `PrepareBufferForBlockFromFile`, buffer-copy helpers, `GetBlockContents`, `ReadBlock`, `ReadBlockContents`, and `ReadAsyncBlockContents`. A local helper records per-block-type read byte counters.

Control flow: synchronous reads first try uncompressed persistent cache, then prefetch buffer, then compressed persistent cache, then file read. File reads may use FS scratch/MultiRead or a prepared stack/heap/compressed/read-scoped buffer. After reading, the trailer is validated and compression type decoded. If checksum corruption occurs and the FS advertises verify-and-reconstruct support, the read is retried. Finally, compressed blocks are decompressed if requested; otherwise ownership is normalized into `BlockContents`. Async reads use `PrefetchAsync` when not for compaction, falling back to synchronous read.

State and persistence: persistent state is only optional persistent cache insertion of serialized or uncompressed blocks when `fill_cache` is set. Runtime state tracks IO status, slice/used buffer, direct IO buffer, heap/compressed allocations, read-scoped lease, FS scratch, prefetch hit state, decompression args, and debug memcpy counters.

Dependencies/integration: depends on `RandomAccessFileReader`, `FilePrefetchBuffer`, footer/checksum code, persistent cache helpers, compression manager/decompressor, memory allocators, file system features, perf counters, and block cache/table reader callers.

Risks and test signals: this code is ownership-sensitive. Key risks include returning memory backed by short-lived prefetch/stack buffers, incorrectly copying compressed versus uncompressed data, checksum retry state leaks, async fallback differences, and under-tested read-scoped leases. `block_fetcher_test.cc` verifies allocation/copy behavior across buffered, mmap, and direct reads for compressed and uncompressed data.
