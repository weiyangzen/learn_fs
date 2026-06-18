## sources/storage-engines/rocksdb/table/block_based/block_prefix_index.h

Purpose: declares `BlockPrefixIndex`, the reader-side hash structure mapping a transformed key prefix to one or more possible data blocks.

Important APIs/types: `GetBlocks(const Slice& key, uint32_t** blocks)` returns the number of candidate blocks and an internal pointer to block IDs. `ApproximateMemoryUsage()` reports object plus bucket/buffer arrays. Static `Create()` builds an index from serialized prefix and metadata blocks using a caller-owned `SliceTransform`. The private constructor stores bucket metadata and an `InternalKeySliceTransform`.

Control flow: table readers call `Create()` after reading hash-index metadata blocks. Lookup paths call `GetBlocks()` before or during index search to narrow candidate blocks by prefix. If zero is returned, the key cannot exist under that prefix index.

State and persistence behavior: persistent bytes live in table metadata; this class owns only decoded heap arrays. Ownership is manual (`new[]`/`delete[]`), and `prefix_extractor` ownership remains with the table reader as documented.

Dependencies/integration points: depends on RocksDB `Status`, `Slice`, `SliceTransform`, comparators, and internal key transforms. It is used with block-based table hash search and prefix extraction options.

Risks: callers must not outlive the prefix extractor. Returned block pointers are internal and must not be freed or retained beyond the index lifetime. Because hash buckets can contain collisions, consumers must treat returned blocks as candidates, not exact matches.

Test signals: hash-search table reader parameterization and prefix extractor setup in `block_based_table_reader_test.cc` indirectly validate creation/lookup. Corruption paths would need targeted metadata corruption tests elsewhere.
