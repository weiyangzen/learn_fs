# sources/storage-engines/rocksdb/table/block_based/partitioned_filter_block.h

Purpose: declares the partitioned filter builder/reader interfaces used by block-based SST construction and reads. It is the public local contract between table building, filter policy code, partitioned index construction, and table-reader filter lookups.

Important APIs/types/functions: `PartitionedFilterBlockBuilder` derives from `FullFilterBlockBuilder` and overrides key addition, empty checks, size estimates, data-block-finalization updates, finish/previous-key hooks, reset, and post-verification behavior. It owns `FilterEntry` records containing separator/internal key, filter owner, and slice. `PartitionedFilterBlockReader` derives from `FilterBlockReaderCommon<Block_kFilterPartitionIndex>` and overrides single-key, multiget, prefix, memory, cache dependency, and cache erase operations.

Control flow: the header reveals a two-level build contract. Filter partitions are queued in `filters_`; `Finish` alternates between returning a partition and consuming the handle of the previously written partition before producing the top-level index. Reader flow is top-level index lookup, partition block retrieval, then full-filter reader delegation.

State and persistence: builder state includes the partitioned index builder pointer, timestamp sizing, decoupling flag, atomic completed partition size, total built entries, construction status, debug previous-key validators, and top-level index builders for internal-key and user-key variants. Reader state includes `filter_map_`, a cache of pinned partition blocks keyed by offset.

Dependencies/integration: depends on `block_cache.h`, filter common readers, full filter block code, `PartitionedIndexBuilder`, `BlockBuilder`, timestamp-aware comparators, and cache entry wrappers. It also exposes typed cache behavior through inherited `FilterBlockReaderCommon`.

Risks and test signals: lifetime risk exists for the raw `PartitionedIndexBuilder*` and prefix extractor/filter bits builder inherited from full filters. Parallel compression requires atomic estimates and thread-safe update paths. The tests in `partitioned_filter_block_test.cc` are strong for functional partitioning but mostly use mocked in-memory block maps rather than real file/cache IO failures.
