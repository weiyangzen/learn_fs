# sources/storage-engines/rocksdb/table/block_based/binary_search_index_reader.h

Purpose: declares the standard block-based table index reader that uses binary search over first keys of blocks.

Important APIs/types/functions: `BinarySearchIndexReader`, static `Create`, `NewIterator`, and `ApproximateMemoryUsage`.

Control flow: declaration inherits common index-block read/cache behavior from `BlockBasedTable::IndexReaderCommon`; constructor is private so callers use `Create`.

State and persistence behavior: stores index block state through the base common reader. Memory accounting includes index block memory and object size or malloc usable size.

Dependencies and integration points: used by block-based table reader when the table options select the binary-search index type. It depends on `index_reader_common.h`.

Risks and test signals: memory accounting depends on `ROCKSDB_MALLOC_USABLE_SIZE`; API drift with `IndexReaderCommon` can break table reads. Block-based table and memory usage tests are relevant.
