# sources/storage-engines/rocksdb/table/block_based/reader_common.h

Purpose: declares shared block-based table reader helpers used by block fetching, cache lifecycle, and checksum validation.

Important APIs/types/functions: `ForceReleaseCachedEntry` is a cleanup callback for cached entries. `GetMemoryAllocator` returns the block cache memory allocator from `BlockBasedTableOptions` when a block cache exists. `VerifyBlockChecksum` validates a block trailer and returns corruption diagnostics on mismatch.

Control flow: this header establishes the expected inputs for checksum verification: footer, data pointer, logical block size, file name, offset, and block type. It also documents that data must include the trailer bytes after the block data.

State and persistence: no state is declared. The functions operate on cache handles or read-only block bytes. `GetMemoryAllocator` exposes allocator configuration used by block read paths.

Dependencies/integration: includes `rocksdb/advanced_cache.h`, `rocksdb/table.h`, and `BlockType`. `BlockFetcher` and block cache wrappers depend on these declarations.

Risks and test signals: misuse risks include calling `ForceReleaseCachedEntry` with mismatched cache/handle arguments and passing an undersized buffer to checksum verification. Tests in this subset indirectly cover block fetch paths but not the release callback.
