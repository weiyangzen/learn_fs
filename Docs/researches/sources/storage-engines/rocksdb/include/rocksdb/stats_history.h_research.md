# Research: sources/storage-engines/rocksdb/include/rocksdb/stats_history.h

- **Purpose:** Exposes `StatsHistoryIterator`, the user-facing iterator for snapshots of statistics automatically recorded by RocksDB.
- **Important APIs/types/functions:** `StatsHistoryIterator::Valid()`, `Next()`, `GetStatsTime()`, `GetStatsMap()`, and `status()` define the read contract. `GetFormatVersion()` remains as a deprecated stub returning `-1`.
- **Control flow:** Callers obtain an iterator from `DB::GetStatsHistory(start, end, &iter)`, then loop while `Valid()`, read the timestamp and stat map, call `Next()`, and check `status()` for terminal errors.
- **State and persistence:** The history source can be in memory or on disk depending on DB options. Returned maps are only valid until the iterator is modified. Timestamps are documented as seconds, even though users often choose time ranges using environment clock values.
- **Dependencies:** Depends on `statistics.h` names, `Status`, and DB internals that materialize snapshots. The forward declaration of `DBImpl` signals implementation ownership outside the public header.
- **Integration points:** Used by monitoring and diagnostics code that wants historical stat snapshots rather than current cumulative counters.
- **Risks:** Lifetime of the returned map is easy to misuse. Time-unit confusion can produce empty ranges. Deprecated format-version plumbing should not be used for feature detection.
- **Test signals:** Tests should cover empty history, bounded time ranges, iterator advancement, map lifetime assumptions, and error reporting via `status()`.
