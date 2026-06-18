<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.cc -->
# sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.cc

## Purpose
Implements lazy creation and lookup for `PrefetchBufferCollection`, a small blob-compaction helper that keeps one `FilePrefetchBuffer` per blob file number.

## Important APIs, Types, And Functions
The sole function is `FilePrefetchBuffer* PrefetchBufferCollection::GetOrCreatePrefetchBuffer(uint64_t file_number)`. It uses `ReadaheadParams` and `FilePrefetchBuffer` from RocksDB file prefetch infrastructure.

## Control Flow
The method indexes `prefetch_buffers_` by `file_number`, creating an empty map entry when none exists. If the `unique_ptr` is null, it builds `ReadaheadParams` with both `initial_readahead_size` and `max_readahead_size` set to the collection's fixed `readahead_size_`, constructs a `FilePrefetchBuffer`, stores it in the map, and returns the raw pointer. Later calls for the same file number return the existing buffer.

## State And Persistence Behavior
There is no on-disk persistence. State is in-memory only: an unordered map from blob file number to owned prefetch buffer. The collection lifetime owns all buffers, and callers receive non-owning pointers whose validity is bounded by the collection lifetime and map entry lifetime.

## Dependencies And Integration Points
The implementation depends on `db/blob/prefetch_buffer_collection.h` and indirectly on `file/file_prefetch_buffer.h`. It is designed for compaction readahead when blob-backed records need reads from potentially many blob files. Each subcompaction should have its own collection because access is intentionally single-threaded.

## Risks And Edge Cases
`operator[]` mutates the map even on lookup, so every distinct requested file number consumes a map entry and potentially a buffer. The class has no locking; sharing it across subcompactions would race and could corrupt buffer state. The fixed initial/max readahead sizes avoid growth but also mean incorrect sizing cannot adapt dynamically within this helper.

## Test Signals
No direct tests appear in this file. Behavioral coverage is expected through blob compaction and blob-index/wide-column tests that exercise blob fetching and compaction readahead paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.cc -->
