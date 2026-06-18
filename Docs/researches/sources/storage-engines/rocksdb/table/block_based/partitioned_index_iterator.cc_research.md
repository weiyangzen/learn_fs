# sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.cc

Purpose: implements `PartitionedIndexIterator`, a two-level index iterator for partitioned block-based indexes when partition blocks are not pre-pinned into a map. It exposes a flattened stream of `IndexValue` entries from top-level index partitions.

Important APIs/types/functions: main operations are `Seek`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `SeekImpl`, `InitPartitionedIndexBlock`, `FindKeyForward`, `FindBlockForward`, and `FindKeyBackward`.

Control flow: `SeekImpl` saves the previous top-level block offset, positions the top-level index iterator, loads the pointed partition block, seeks inside it, then advances to the next non-empty partition if needed. `Next` advances the current partition iterator and calls `FindKeyForward`; if the partition is exhausted, `FindBlockForward` resets the partition iterator, advances the top-level iterator, loads the next partition, and seeks to first. Backward iteration mirrors this with `Prev`, `SeekToLast`, and `FindKeyBackward`.

State and persistence: no persistent writes. Runtime state is split between `index_iter_` for top-level partitions and `block_iter_` for the current index partition. `prev_block_offset_` avoids refetching the same partition on reseek, unless the previous read was incomplete. `BlockPrefetcher` carries readahead state.

Dependencies/integration: depends on `BlockBasedTable::NewDataBlockIterator`, `BlockPrefetcher`, `ReadOptions`, `BlockCacheLookupContext`, `IndexBlockIter`, and table `Rep` index metadata flags. It uses the table block cache path with `BlockType::kIndex`.

Risks and test signals: risks include stale `prev_block_offset_` reuse if handles share offsets unexpectedly, status propagation from partition iterators, skipped upper-bound checks, and readahead option handling. Direct tests are outside this subset; partitioned index behavior is indirectly exercised by partitioned filter tests through top-level index iteration and by block-based table reader tests elsewhere.
