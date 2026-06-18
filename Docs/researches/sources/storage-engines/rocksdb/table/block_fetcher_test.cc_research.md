# sources/storage-engines/rocksdb/table/block_fetcher_test.cc

Purpose: unit tests for `BlockFetcher` buffer ownership and copy/allocation behavior under multiple IO modes and compression modes.

Important APIs/types/functions: `BlockFetcherTest` provides helpers to create a small block-based table, fetch its index block, fetch the first data block, build table readers, read footers, and wrap the raw `BlockFetcher` constructor. `MemcpyStats`, `BufAllocationStats`, and `TestStats` encode expected debug counters and custom allocator counts.

Control flow: each test creates SSTs with supported compression types, reads index handles through metadata/index readers, then calls `FetchBlock` under three modes: buffered read, mmap, and direct read. The tests compare returned block contents across modes and assert exact copy/allocation counts.

State and persistence: tests write temporary SST files under a per-thread DB path and remove the directory at teardown. They use `CountedMemoryAllocator` to validate allocation/deallocation behavior after `BlockContents::allocation.reset()`.

Dependencies/integration: depends on block-based table builder/reader/factory, binary-search index reader, footer/meta block lookup, file system abstractions, compression support enumeration, and test sync points for direct IO mocking.

Risks and test signals: coverage is strong for uncompressed reads, compressed reads without decompression, compressed reads with decompression, index block reads, and custom allocator lifetime. Gaps include persistent cache hits/inserts, checksum mismatch/retry, async prefetch, read-scoped block buffer provider, FS scratch ownership, and large-block paths exceeding the stack buffer threshold.
