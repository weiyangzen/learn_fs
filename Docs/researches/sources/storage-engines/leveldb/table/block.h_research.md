# sources/storage-engines/leveldb/table/block.h

## Purpose
`block.h` declares the immutable in-memory representation of one decoded LevelDB table block.

## Important APIs, Types, and Functions
`Block` exposes `Block(const BlockContents&)`, `~Block`, `size()`, and `NewIterator(const Comparator*)`. It stores `data_`, `size_`, `restart_offset_`, and `owned_`, with nested iterator implementation hidden in the `.cc` file.

## Control Flow
Clients construct a `Block` from `BlockContents` returned by `ReadBlock`, request iterators, and destroy the block when cached or iterator cleanup releases it.

## State, Dependencies, and Integration
The block either borrows file-backed memory or owns a heap buffer. It depends on `leveldb::Iterator`, `Comparator`, and `BlockContents`. It is the bridge between table format bytes and query iteration.

## Risks and Test Signals
Ownership is the key risk: `owned_` must match `BlockContents::heap_allocated` to avoid leaks or invalid deletes. Table and block tests validate iteration and malformed block behavior.
