<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/pebble/main.go -->
# sources/storage-engines/pebble/internal/pacertoy/pebble/main.go

Purpose: standalone simulation of Pebble-style pacing, modeling memtable filling, flush draining, L0 compaction, compaction debt, and adaptive flush-rate throttling.

Important APIs/types: constants for rates, sizes, thresholds, and level counts; `compactionPacer`, `flushPacer`, `DB`, `newDB`, background methods `drainCompaction` and `drainMemtable`, `fillCompaction`, `delayMemtableDrain`, `fillMemtable`, `simulateWrite`, and `main`.

Control flow and state: `newDB` initializes memtables, L0, level sizes, full lower levels, limiters, and starts two background loops. User writes fill mutable memtables, flushers drain immutable memtables into L0, and compaction drains L0 into lower levels. Compaction debt reduces flush max rate when above threshold and gradually restores it otherwise. `main` prints one-second metrics until `simulateWrite` exits after a fixed write amount.

Persistence and integration: no durable DB; all structures are simulation counters protected by mutexes/atomics/conds and `rate.Limiter`. Risks include toy fidelity, infinite goroutines, reliance on `os.Exit`, possible cond signaling subtleties, and measure-latency indexing assumptions. There are no tests; its value is exploratory comparison of pacing dynamics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/pacertoy/pebble/main.go -->
