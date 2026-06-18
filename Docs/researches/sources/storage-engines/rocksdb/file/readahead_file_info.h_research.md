# sources/storage-engines/rocksdb/file/readahead_file_info.h

## Purpose

`readahead_file_info.h` defines a small state carrier for readahead information passed between files during iteration. Its goal is to let iterators continue an established automatic prefetch size and read count when moving to the next file in a level, instead of restarting from the initial readahead state.

## Important APIs, Types, and Functions

- `struct ReadaheadFileInfo` contains two `ReadaheadInfo` members:
  - `data_block_readahead_info` for data block iterators.
  - `index_block_readahead_info` for index block iterators.
- Nested `struct ReadaheadInfo` stores:
  - `size_t readahead_size = 0`.
  - `int64_t num_file_reads = 0`.

## Control Flow and State

The header has no functions. It defines plain value state that can be copied or updated by iterator/prefetch components. The state is in-memory only and is not persisted to DB files or manifests.

## Dependencies and Integration Points

It depends only on standard integer/size headers and the RocksDB namespace header. It integrates with block iterators and prefetchers that need separate carry-over state for data and index block read streams.

## Risks and Edge Cases

- Both counters default to zero, so callers must distinguish uninitialized/new-file state from a deliberate zero readahead policy.
- Data and index streams are separate; mixing them would produce incorrect adaptive behavior.
- The struct has no synchronization; it should be updated according to iterator ownership/threading rules.

## Test Signals

`prefetch_test.cc` verifies this behavior indirectly in `DBIterLevelReadAhead` and `DBIterLevelReadAheadWithAsyncIO`, where sync points assert readahead state is carried to subsequent files and grows beyond the initial 8 KiB size during sequential scans.
