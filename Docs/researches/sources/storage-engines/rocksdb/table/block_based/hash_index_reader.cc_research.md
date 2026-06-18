# sources/storage-engines/rocksdb/table/block_based/hash_index_reader.cc

## Purpose
Implements the table-level hash index reader for block-based tables configured with `kHashSearch`. It combines the normal binary-search index block with optional prefix-hash metadata blocks to accelerate prefix-based index seeks.

## Important APIs, Types, And Functions
`HashIndexReader::Create` reads or prepares the primary index block, locates `kHashIndexPrefixesBlock` and `kHashIndexPrefixesMetadataBlock`, fetches those blocks, and creates a `BlockPrefixIndex`. `NewIterator` returns an index iterator over the primary index block, optionally supplied with `prefix_index_`.

## Control Flow
Creation can prefetch/pin the primary index block according to cache flags. After constructing the reader, it tries to find and read hash-index prefix metablocks through the meta-index. Missing prefix metadata is treated as non-fatal, so the reader still works through binary search. If both prefix blocks read and parse successfully, the `BlockPrefixIndex` is attached. Iterator creation reads or reuses the index block, handles errors by invalidating or returning an error iterator, and calls `Block::NewIndexIterator` with comparator and index-format flags.

## State And Persistence Behavior
The reader may hold a cached/owned primary index block via `IndexReaderCommon` and optionally owns an in-memory `BlockPrefixIndex` parsed from persisted prefix metadata blocks. It does not modify table files.

## Dependencies And Integration Points
Depends on `FindMetaBlock`, `BlockFetcher`, `BlockPrefixIndex`, table prefix extractor, footer/decompressor/cache options, memory allocator, and `IndexReaderCommon`. It integrates with table open/read paths for hash-search indexes created by `HashIndexBuilder`.

## Risks And Edge Cases
Prefix-index creation failures intentionally fall back to binary-search behavior, but primary index read failures are hard errors. The code asserts a table prefix extractor exists when creating the prefix index. Metadata block read or parse problems should not create false negatives because the primary index remains authoritative.

## Test Signals
Coverage is indirect through block-based table hash-search tests, prefix seek behavior, and table open compatibility tests where hash index metadata is missing or unreadable.
