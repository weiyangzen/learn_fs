# `sources/test-tools/filebench/stats.h`

Purpose: Defines Filebench flow statistics data and exposes the stats clear/snapshot API.

Important APIs and types: `struct flowstats` tracks operation counts, read/write counts, byte totals, read/write bytes, 64 latency distribution buckets, total latency, max/min latency, and start/end timestamps used by global stats. Functions `stats_clear()` and `stats_snap()` are the exported commands. Macros classify active/IO flowops and derive IOPS-style counters.

Control flow and integration: Flowops update embedded `fo_stats` during execution. `stats.c` reads these fields at snapshot time and rolls them into global and master-flowop aggregates. The header is included by flowop, variable, and stats consumers that need the struct layout.

State and persistence: The struct is embedded in flowop/threadflow runtime structures and allocated in global arrays for reporting. Values are per-run, reset by `stats_clear()`, and not persisted outside logs.

Dependencies: Includes `filebench.h` and `fbtime.h` for common types and high-resolution time.

Risks and test signals: `STAT_CPUTIME` and `STAT_OHEADTIME` reference fields not present in this struct, suggesting stale macros or external expectations that should be checked before use. Tests should compile all stats macro consumers and validate min/max latency initialization and bucket array bounds.
