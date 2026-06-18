# sources/storage-engines/rocksdb/monitoring/stats_history_test.cc

Purpose: Integration tests for stats dump scheduling, stats persist scheduling, in-memory stats history, persistent stats history, persistent stats CF behavior, read-only reopen, and stats-CF flush ordering.

Important APIs/types/functions: `StatsHistoryTest` extends `DBTestBase`, installs a `MockSystemClock`, wraps the Env with `CompositeEnvWrapper`, and overrides periodic-task scheduler timers through a sync point. Tests include `RunStatsDumpPeriodSec`, `StatsPersistScheduling`, `PersistentStatsFreshInstall`, `GetStatsHistoryInMemory`, `InMemoryStatsHistoryPurging`, `GetStatsHistoryFromDisk`, `PersitentStatsVerifyValue`, `PersistentStatsCreateColumnFamilies`, `PersistentStatsReadOnly`, and `ForceManualFlushStatsCF`.

Control flow: Tests reopen DBs with stats options, advance mock time through `TEST_WaitForPeriodicTaskRun`, inspect callbacks/counters, call `GetStatsHistory`, iterate maps, and check persistent stats CF contents using iterators. Several tests create extra column families and verify stats survive reopen.

State and persistence behavior: Exercises both `DBImpl::stats_history_` memory snapshots and the persistent stats column family. Disk tests verify monotonic key growth, preserved non-zero counters after reopen, reserved CF name behavior, and read-only compatibility.

Dependencies/integration: Uses DB internals, column-family handles, periodic scheduler, sync points, cache/rate-limiter includes, persistent stats helpers, mock time, and test utilities.

Risks/test signals: Tests are time-sensitive but controlled by mock clock and scheduler wait hooks. `PersitentStatsVerifyValue` has a misspelled test name. Coverage is broad and gives the strongest integration signal for stats-history behavior.
