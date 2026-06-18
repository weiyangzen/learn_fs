# sources/storage-engines/rocksdb/table/block_based/index_builder.cc

## Purpose
Implements block-based table index builder factories and the non-inline behavior for shortened single-level indexes and partitioned two-level indexes.

## Important APIs, Types, And Functions
`IndexBuilder::CreateIndexBuilder` selects `ShortenedIndexBuilder`, `HashIndexBuilder`, or `PartitionedIndexBuilder`. `ShortenedIndexBuilder::FindShortestInternalKeySeparator`, `FindShortInternalKeySuccessor`, and `UpdateIndexSizeEstimate` implement separator shortening and cached size estimates. `PartitionedIndexBuilder` implements `CreateIndexBuilder`, constructor, `MakeNewSubIndexBuilder`, `RequestPartitionCut`, `CreatePreparedIndexEntry`, `PrepareIndexEntry`, `MaybeFlush`, `FinishIndexEntry`, `AddIndexEntry`, `Finish`, `NumPartitions`, and `UpdateIndexSizeEstimate`.

## Control Flow
Factory selection follows `BlockBasedTableOptions::IndexType`. Shortened indexes compute separators from neighboring block keys and may omit sequence numbers when safe. Partitioned indexes maintain a list of sub-index builders; as entries are added, `MaybeFlush` cuts a partition when requested or when the metadata block-size policy says the active partition is large enough. `Finish` is multi-step: each call returns one partition index with `Status::Incomplete`, then later calls feed the just-written partition handle into the top-level index until the final top-level index is returned with `Status::OK`.

## State And Persistence Behavior
The file writes no table bytes directly but populates `IndexBlocks` with index block contents and metadata. Partitioned indexes persist first-level partition blocks plus a top-level index. Runtime state tracks partition list, current sub-builder, flush policy, handle delta encoding, cached size estimates, sequence-number separator mode, and uniform-index block counts.

## Dependencies And Integration Points
Depends on internal key formatting/comparators, `BlockBuilder`, `BlockHandle`, flush block policies, partitioned filter coordination, table options, and statistics. It is called by block-based table builder when finalizing data blocks and table metadata.

## Risks And Edge Cases
Separator shortening must preserve total ordering with internal keys and user-defined timestamps. Once any partition requires key-plus-sequence separators, the mode must be applied consistently to all sub-index builders. Parallel compression splits prepare/finish work across threads, so cached estimates and mode flags use relaxed atomics. The finish protocol is easy to misuse because callers must keep calling while status is incomplete and provide the last written partition handle.

## Test Signals
Index builder tests elsewhere should validate index type selection, key shortening, first-key inclusion, partition counts, partition/filter alignment, user-defined timestamp stripping, value delta encoding, and current index size estimates.
