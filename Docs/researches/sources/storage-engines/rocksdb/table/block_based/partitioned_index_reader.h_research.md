# sources/storage-engines/rocksdb/table/block_based/partitioned_index_reader.h

Purpose: declares the partitioned-index reader used by block-based table readers for two-level index structures.

Important APIs/types/functions: `PartitionIndexReader` derives from `BlockBasedTable::IndexReaderCommon`. Public methods are static `Create`, `NewIterator`, `CacheDependencies`, `ApproximateMemoryUsage`, and `EraseFromCacheBeforeDestruction`. The private constructor takes a table pointer and top-level index `CachableEntry<Block>`.

Control flow: the declared contract is top-level index acquisition followed by either lazy partition reads during iteration or dependency caching/pinning before iteration. `NewIterator` returns an iterator whose first level is the partition index.

State and persistence: persistent input is the SST index metadata and partition index blocks. The reader may own or cache-reference the top-level index through the base class and may pin all index partitions in `partition_map_`. Approximate memory usage includes base index block usage plus object size, but only has a TODO for exact map memory.

Dependencies/integration: depends on `index_reader_common.h` and `UnorderedMap`. The reader is chosen by block-based table open logic when the table uses partitioned indexes, and its dependency caching is invoked by cache-index-and-filter-blocks/pin options.

Risks and test signals: all-or-none expectation for `partition_map_` is important; partial maps would make iterator logic unsafe. Memory usage undercounts the map. Direct tests are not present here, so coverage depends on block-based table reader tests, partitioned index tests elsewhere, and partitioned filter tests that reuse partitioned index builder semantics.
