# sources/storage-engines/rocksdb/table/block_based/index_reader_common.h

## Purpose
Declares `BlockBasedTable::IndexReaderCommon`, a base class for index readers that need shared access to the primary index block regardless of whether it is owned, cached, pinned, or lazily read.

## Important APIs, Types, And Functions
The constructor stores a table pointer and movable `CachableEntry<Block>`. Public `EraseFromCacheBeforeDestruction` is overridden from `IndexReader`. Protected helpers include `ReadIndexBlock`, `table`, `internal_comparator`, `index_has_first_key`, `index_key_includes_seq`, `index_value_is_full`, `cache_index_blocks`, `user_defined_timestamps_persisted`, `GetOrReadIndexBlock`, and `ApproximateIndexBlockMemoryUsage`.

## Control Flow
Derived readers call `GetOrReadIndexBlock` before creating iterators. Helper accessors expose immutable table representation flags needed to configure `Block::NewIndexIterator`.

## State And Persistence Behavior
Runtime state is a non-owning `BlockBasedTable` pointer and `CachableEntry<Block>` for the index block. The class does not write table bytes.

## Dependencies And Integration Points
Depends on `block_based_table_reader.h` and `reader_common.h`. It is inherited by `HashIndexReader` and other index-reader implementations in the block-based table reader.

## Risks And Edge Cases
All helper methods assert a valid table representation, so lifetime is critical. Derived classes must transfer cache handles to returned iterators when needed to keep block contents alive.

## Test Signals
Indirect signals are successful iterator creation over cached and uncached index blocks, accurate memory usage, and safe cache erasure on reader destruction.
