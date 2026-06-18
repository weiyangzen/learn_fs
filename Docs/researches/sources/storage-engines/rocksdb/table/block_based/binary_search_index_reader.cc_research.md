# sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.cc

Purpose: implements the block-based table index reader for the standard binary-search index.

Important APIs/types/functions: `BinarySearchIndexReader::Create` and `NewIterator`.

Control flow: `Create` asserts valid inputs, optionally reads/prefetches the index block, drops it if it should remain cache-backed and unpinned, and constructs the reader. `NewIterator` obtains the index block through cache or file read, returns an error iterator on failure, otherwise asks `Block::NewIndexIterator` for a binary-search-capable iterator and transfers cache ownership to it.

State and persistence behavior: owns or references a cached index block through `CachableEntry`. No persistence; it reads table index blocks from SST files and may pin/cache them.

Dependencies and integration points: depends on `IndexReaderCommon`, `BlockBasedTable::Rep`, block cache lookup context, global sequence number handling, timestamp persistence, and table options for index block search type.

Risks and test signals: cache/pin/prefetch combinations affect lifetime and memory use. Iterator invalidation must preserve read errors. Block-based table reader, block cache, and partitioned/full-filter tests are useful.
