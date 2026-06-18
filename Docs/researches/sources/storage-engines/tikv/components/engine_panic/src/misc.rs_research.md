# sources/storage-engines/tikv/components/engine_panic/src/misc.rs

Purpose: Panic skeleton for miscellaneous engine operations and statistics reporting.

Important APIs and types: `PanicReporter` implements `StatisticsReporter<PanicEngine>`. `PanicEngine` implements `MiscExt` with flush, delete ranges, memtable stats, ingest slowdown, used size, path, WAL sync, manual compaction toggles, background work pause/continue, existence/lock checks, stats dumps, sequence numbers, SST size, key count, range stats, stall status, active memtable stats, accumulated flush count, and disk-engine access.

Control flow and state: Every operation panics; no reporting state exists.

Dependencies and integration: This mirrors operational APIs consumed throughout TiKV for maintenance, metrics, and safety checks.

Risks: Runtime use panics. Since this surface is large, trait changes are likely to show up here during compilation.

Test signals: No local tests.
