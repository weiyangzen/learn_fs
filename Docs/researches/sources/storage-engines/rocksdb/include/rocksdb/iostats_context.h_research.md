# Research: sources/storage-engines/rocksdb/include/rocksdb/iostats_context.h

## Purpose

`iostats_context.h` declares the thread-local I/O statistics context used by RocksDB to collect low-overhead per-thread counters and timing values for file operations. It complements `perf_context` and is enabled according to the configured `PerfLevel`.

## Important APIs, Types, and Functions

`FileIOByTemperature` stores read byte and read count counters for hot, warm, cool, cold, ice, and unknown file temperature categories. `IOStatsContext` exposes `Reset()`, `ToString(bool exclude_zero_counters)`, counters for bytes read/written, open/allocation/write/read/range-sync/fsync/prepare-write/logger/cpu timings, a `thread_pool_id`, nested temperature stats, and `disable_iostats`. `get_iostats_context()` returns a non-null pointer to the active context.

## Control Flow

Callers obtain `get_iostats_context()`, optionally `Reset()`, execute I/O, and inspect counters or stringify the result. The implementation in `monitoring/iostats_context.cc` returns a `thread_local IOStatsContext` unless `NIOSTATS_CONTEXT` is defined. `Reset()` zeros counters and sets `thread_pool_id` to `Env::Priority::TOTAL`. `ToString()` appends counters, optionally skipping zeros.

## State and Persistence Behavior

The state is process-local and normally thread-local, so counters are isolated per worker thread. It is not persisted in the DB. Under `NIOSTATS_CONTEXT`, the implementation returns a global no-op object and updates are ignored, making reads empty/no-op. `disable_iostats` is an escape hatch used to avoid polluting counters for selected file operations such as logging or backup paths.

## Dependencies and Integration Points

The header depends on `rocksdb/perf_level.h`. Usage appears in DB compaction tests, sequence number time tests, DB misc tests, backup engine code, DB implementation, and `monitoring/iostats_context_test.cc`. Temperature counters integrate with tiered storage and file temperature metadata.

## Risks and Edge Cases

Because counters are per-thread, aggregate operation analysis must collect from the correct thread or use surrounding infrastructure to sum threads. BackupEngine relies on some counters regardless of PerfLevel, so broad changes to enabling rules can break existing metrics. The implementation's `ToString()` currently prints many, but not all, temperature counters declared in the header, so consumers should prefer direct fields when exact coverage matters. `disable_iostats` can intentionally hide file operations, which is useful but can surprise tests expecting bytes to move.

## Test Signals

`monitoring/iostats_context_test.cc` validates string output and zero filtering. DB and compaction tests reset the context, perform reads or compactions, and assert byte/timing counters and temperature buckets. Backup-related tests indirectly exercise the guarantee that required counter metrics remain available even when timer-oriented PerfLevel behavior differs.
