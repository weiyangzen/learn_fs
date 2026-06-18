<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/rocksdb/main.go -->
# sources/storage-engines/pebble/internal/pacertoy/rocksdb/main.go

Purpose: standalone simulation of RocksDB-style write pacing, used as a contrast with the Pebble pacer toy.

Important APIs/types: constants for compaction/write rates and thresholds; `compactionPacer`, `flushPacer`, `DB`, `newDB`, `drainCompaction`, `fillCompaction`, `drainMemtable`, `delayUserWrites`, `fillMemtable`, `simulateWrite`, and `main`.

Control flow and state: writes pass through an input limiter and a DB `writeLimiter`. Memtable fills block when dirty bytes exceed `memtableStopThreshold`. Flush and compaction loops move bytes through L0 and lower levels. `delayUserWrites` adjusts `writeLimiter`: slows when L0 count or compaction debt is high and growing, speeds when debt shrinks, and rewards recovery after prior debt.

Persistence and integration: no real storage; this is a simulation using mutexes, cond vars, atomics, and `rate.Limiter`. It prints periodic metrics including max write rate. Risks include nondeterministic seeds from time, endless execution, toy assumptions about compaction geometry, possible lock misuse around `len(db.L0)` under `db.mu` rather than `compactionMu`, and no tests. Integration is manual experimentation rather than production code.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/rocksdb/main.go -->
