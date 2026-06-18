# sources/storage-engines/leveldb/table/table.cc

## Purpose
`table.cc` opens and queries immutable SSTable files.

## Important APIs, Types, and Functions
`Table::Open`, `ReadMeta`, `ReadFilter`, `NewIterator`, `InternalGet`, `ApproximateOffsetOf`, and static `BlockReader` are central. `Table::Rep` owns options, file pointer, cache id, filter reader/data, metaindex handle, and index block.

## Control Flow
Open reads the fixed footer, decodes handles, reads the index block, constructs `Rep`, assigns a block-cache id, and loads optional filter metadata. Iteration uses `NewTwoLevelIterator` over the index block and `BlockReader`. `InternalGet` seeks the index, optionally skips a block via filter, reads the block, seeks the key, and invokes the result callback. Block reads consult `block_cache`, inserting cachable blocks with cleanup callbacks.

## State, Persistence, and Integration
Persistent table bytes are read through `RandomAccessFile`; in-memory state includes index block, filter block, and block-cache handles. It integrates with `format`, `block`, `filter_block`, cache API, and DB table cache code.

## Risks and Test Signals
Meta/filter read errors are intentionally ignored to keep tables usable. Cache key construction combines table cache id and block offset; bad ids or ownership would corrupt cache behavior. Table tests cover iteration, comparators, approximate offsets, compressed data, and DB integration.
