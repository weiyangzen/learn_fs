# sources/storage-engines/rocksdb/table/block_based/hash_index_reader.h

## Purpose
Declares `HashIndexReader`, the `IndexReader` implementation that augments block-based table index iteration with a prefix hash index.

## Important APIs, Types, And Functions
`Create` is the factory used during table open. `NewIterator` returns an `InternalIteratorBase<IndexValue>` over index entries. `ApproximateMemoryUsage` combines inherited index-block usage with reader and prefix-index memory. Private construction accepts a table pointer and movable `CachableEntry<Block>`.

## Control Flow
The factory builds a reader around the main index block and optional prefix index metadata. Read operations obtain an iterator through `NewIterator`, which delegates to the underlying index block and passes `prefix_index_.get()` when available.

## State And Persistence Behavior
Runtime state is inherited `IndexReaderCommon` plus an owned `std::unique_ptr<BlockPrefixIndex>`. Persistent state is read from primary index and hash-prefix metablocks written by `HashIndexBuilder`.

## Dependencies And Integration Points
Depends on `index_reader_common.h`, `BlockBasedTable`, `FilePrefetchBuffer`, `InternalIterator`, `IndexBlockIter`, `GetContext`, and block cache lookup context. It plugs into the block-based table reader's index-reader factory selection.

## Risks And Edge Cases
Memory accounting differs under `ROCKSDB_MALLOC_USABLE_SIZE`; without it, prefix-index memory is explicitly added. The reader must remain correct when `prefix_index_` is null by relying on ordinary index lookup.

## Test Signals
Hash-search table tests should show successful point/prefix lookup with and without prefix-index metadata and stable approximate memory usage.
