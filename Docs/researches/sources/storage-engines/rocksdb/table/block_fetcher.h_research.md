# sources/storage-engines/rocksdb/table/block_fetcher.h

Purpose: declares `BlockFetcher`, a single-block retrieval helper used by RocksDB table readers. The class hides prefetch, persistent cache, checksum, decompression, direct IO, and memory allocation details behind `ReadBlockContents` and `ReadAsyncBlockContents`.

Important APIs/types/functions: constructor arguments include file reader, optional prefetch buffer, footer, read options, block handle, output `BlockContents`, immutable options, decompression flags, block type, decompressor, persistent cache options, allocators, compaction flag, and optional read-scoped buffer provider. Public accessors expose compression type, block size with trailer, compressed block slice, and debug copy counters.

Control flow: the header lays out private phases: lookup uncompressed cache, try prefetch, lookup serialized cache, prepare file buffer, copy to final buffers, produce block contents, insert caches, process trailer, and read from file. The public methods orchestrate these phases synchronously or through async prefetch.

State and persistence: the fetcher is per-read transient. It can update persistent cache through helper methods, but otherwise owns temporary buffers and moves final ownership into `BlockContents`. `BlockContents` may end up backed by heap allocation, mmap slice, compressed allocation, or read-scoped cleanup.

Dependencies/integration: includes file utilities, memory allocator implementation, block definitions, format/footer, persistent cache options, and cast utilities. It is called by `BlockBasedTable::RetrieveBlock`/`MaybeReadBlockAndLoadToCache` paths and feeds parsed block classes.

Risks and test signals: because it stores references to footer, handle, options, and cache options, those must outlive the fetcher call. Feature flags for FS scratch and verify/reconstruct alter buffer lifetimes and retry behavior. The test file asserts expected allocations and memcpys in representative modes but not all persistent-cache or async branches.
