# sources/storage-engines/rocksdb/table/block_based/index_builder.h

## Purpose
Declares the index-builder abstraction and concrete builders for block-based table primary indexes: shortened binary-search indexes, hash-search indexes with prefix metadata, and partitioned two-level indexes.

## Important APIs, Types, And Functions
`IndexBuilder` declares `CreateIndexBuilder`, `IndexBlocks`, `AddIndexEntry`, the `PreparedIndexEntry` pipeline, `OnKeyAdded`, `Finish`, `IndexSize`, `NumUniformIndexBlocks`, `CurrentIndexSizeEstimate`, and separator-mode helpers. `ShortenedIndexBuilder` manages primary index block construction, optional first-key storage in `IndexValue`, separator shortening, delta-encoded handles, and parallel prepare/finish. `HashIndexBuilder` wraps a shortened primary index and emits hash-prefix metadata blocks. `PartitionedIndexBuilder` builds multiple shortened sub-indexes plus a top-level index and coordinates partition cuts with filters.

## Control Flow
Table builder calls `OnKeyAdded` for keys and `AddIndexEntry` or the prepare/finish pipeline for each data block. `ShortenedIndexBuilder` computes a separator between the last key of one block and the first key of the next, tracks whether sequence numbers are required, and adds encoded `IndexValue`s to one of two block builders. `HashIndexBuilder` counts restart indexes and groups adjacent keys by extracted prefix, flushing prefix metadata when the prefix changes. `PartitionedIndexBuilder` cuts sub-index partitions, then emits them one by one before emitting a top-level index.

## State And Persistence Behavior
Persistent output is `IndexBlocks::index_block_contents` plus optional `meta_blocks`. Hash search writes `kHashIndexPrefixesBlock` and `kHashIndexPrefixesMetadataBlock`, where prefixes are concatenated separately from metadata triples. Partitioned indexes persist partition index blocks and a final index-on-index block. Runtime state includes block builders, pending prefix metadata, active partition builders, cached size estimates, and flags for timestamp persistence and sequence-number separator mode.

## Dependencies And Integration Points
Depends on `InternalKeyComparator`, `InternalKeySliceTransform`, `BlockBuilder`, `FlushBlockPolicy`, block-based table options, and table format helpers. Integrated with `HashIndexReader`, partitioned filter builders, table property accounting, and parallel compression/construction.

## Risks And Edge Cases
User-defined timestamp persistence affects whether timestamps are stripped from index keys and first internal keys. Key shortening must be disabled or fall back when comparator shortening cannot produce a valid separator. Hash prefix metadata assumes sorted keys and a stable prefix extractor. `CurrentIndexSizeEstimate` for `HashIndexBuilder` currently returns zero, so callers relying on estimates get no useful signal for hash indexes.

## Test Signals
Look for tests around binary search with first key, hash search prefix lookup, partitioned index finishing, partition/filter alignment, user-defined timestamps, and table open/read compatibility.
