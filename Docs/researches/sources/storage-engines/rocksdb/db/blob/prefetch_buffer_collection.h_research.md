<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.h -->
# sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.h

## Purpose
Declares `PrefetchBufferCollection`, an owner for per-blob-file `FilePrefetchBuffer` objects used to implement compaction readahead for blob files.

## Important APIs, Types, And Functions
The public API is `explicit PrefetchBufferCollection(uint64_t readahead_size)` and `FilePrefetchBuffer* GetOrCreatePrefetchBuffer(uint64_t file_number)`. Private state is `uint64_t readahead_size_` and `std::unordered_map<uint64_t, std::unique_ptr<FilePrefetchBuffer>> prefetch_buffers_`.

## Control Flow
Construction records the configured readahead size and asserts it is positive. Lookup/creation is implemented in the `.cc` file and returns a stable non-owning pointer to the buffer associated with a file number. The map key is the blob file number, not a path or cache key.

## State And Persistence Behavior
All state is transient memory owned by the collection. It has no explicit cleanup method because `unique_ptr` members release buffers when the collection is destroyed. The comments state it is single-thread-only and each subcompaction should maintain its own collection because even reads from the same blob file can happen from different positions.

## Dependencies And Integration Points
The header includes `file/file_prefetch_buffer.h` and RocksDB namespace definitions. It integrates with blob compaction/read code that needs readahead without sharing `FilePrefetchBuffer` instances between independent scan streams.

## Risks And Edge Cases
The constructor only asserts positive `readahead_size_`; release builds rely on callers to pass a meaningful nonzero value. There is no concurrency protection, and buffer pointers should not escape longer than the collection. Since buffers are keyed only by file number, callers requiring multiple independent streams over the same blob file need separate collections.

## Test Signals
The header has no standalone tests. Indirect test signals should come from compaction tests that compare blob read behavior, lazy resolution, and performance/statistics when blob files are read during compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/prefetch_buffer_collection.h -->
