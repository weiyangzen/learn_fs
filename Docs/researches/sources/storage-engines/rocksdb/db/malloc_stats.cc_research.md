<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.cc -->
# sources/storage-engines/rocksdb/db/malloc_stats.cc

## Purpose
Implements optional allocator statistics dumping for builds linked with jemalloc. It appends jemalloc's `malloc_stats_print()` output into a caller-provided string when jemalloc is available; otherwise it is a no-op.

## Important APIs, Types, And Functions
`DumpMallocStats(std::string* stats)` is the only exported function. Under `ROCKSDB_JEMALLOC`, helper struct `MallocStatus` tracks the current and end pointer of a fixed-size buffer. `GetJemallocStatus()` is the callback passed to `malloc_stats_print()`; it copies each emitted status chunk into the remaining buffer and advances the cursor.

## Control Flow
When compiled with jemalloc support, `DumpMallocStats()` first checks `HasJemalloc()`. If false, it returns without modification. If true, it allocates a 1,000,001-byte buffer, initializes callback cursor bounds, invokes `malloc_stats_print(GetJemallocStatus, &mstat, "")`, then appends the collected C string to `stats`. Without jemalloc support, the function body is empty.

## State And Persistence Behavior
The function only reads allocator process state and appends diagnostic text to memory. It does not persist data or mutate RocksDB state. Output is bounded by the fixed buffer size; callback chunks that do not fit are ignored.

## Dependencies And Integration Points
Depends on `db/malloc_stats.h`, `<cstring>`, `<memory>`, and `port/jemalloc_helper.h`. It is used by diagnostics/statistics code paths that want allocator-level visibility in logs or status reports.

## Risks And Edge Cases
The callback uses `snprintf()` and advances by `status_len`; if jemalloc emits more than the fixed buffer, excess output is silently dropped. The buffer is default-initialized through `new char[]` and appended as a C string after callback writes, relying on allocation/value behavior and callback termination semantics to leave a valid string. Build-time and runtime jemalloc availability can differ, so callers must tolerate empty output.

## Test Signals
Coverage is usually build-configuration dependent. Tests can assert no-op behavior without jemalloc and non-crashing bounded output when `ROCKSDB_JEMALLOC` and `HasJemalloc()` are true.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/malloc_stats.cc -->
