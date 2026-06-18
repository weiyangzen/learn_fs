<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.h -->
# sources/storage-engines/rocksdb/db/malloc_stats.h

## Purpose
Declares the allocator diagnostic hook `DumpMallocStats()`.

## Important APIs, Types, And Functions
The header exposes `void DumpMallocStats(std::string*)` in the RocksDB namespace. The function appends allocator statistics to the provided string when supported by the build/runtime environment.

## Control Flow
Callers pass a mutable string buffer. The implementation decides at compile time and runtime whether jemalloc stats can be collected.

## State And Persistence Behavior
The API is diagnostic only. It does not own state and does not persist results except by appending to the caller's string.

## Dependencies And Integration Points
Includes `<string>` and RocksDB namespace configuration. It is used by DB diagnostics and logging paths that collect memory allocator state.

## Risks And Edge Cases
Callers must accept that output can be empty. The function takes a raw pointer and assumes it is valid. It should not be used as a correctness signal because availability depends on build flags and allocator linkage.

## Test Signals
Tests are mostly configuration-level: no-op builds should link and run, jemalloc builds should return without crashing and produce bounded diagnostic text when jemalloc is active.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.h -->
