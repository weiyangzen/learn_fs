# sources/distributed-fs/tahoe-lafs/src/allmydata/stats.py

## Purpose
Provides node statistics aggregation and CPU usage monitoring as Twisted services.

## Important APIs, Types, and Functions
`CPUUsageMonitor` implements `IStatsProducer`, samples wall/process CPU time every 60 seconds, and reports 1/5/15-minute CPU fractions plus total CPU. `StatsProvider` stores counters, registers producers, and returns `{"counters": ..., "stats": ...}` from `get_stats()`.

## Control Flow
`CPUUsageMonitor.startService()` records initial CPU time. A `TimerService` calls `check()` to append bounded samples. `_average_N_minutes()` calculates process CPU delta divided by wall-clock delta when enough samples exist. `StatsProvider.get_stats()` queries registered producers and logs the combined result.

## State and Persistence Behavior
State is in memory only: a bounded `deque` of CPU samples, a Unicode-key counter dictionary, and producer references. There is no disk persistence.

## Dependencies and Integration Points
Depends on Twisted service/TimerService, `IStatsProducer`, `dictutil.UnicodeKeyDict`, and Tahoe logging. The node web/status paths consume `StatsProvider.get_stats()` output.

## Risks and Edge Cases
CPU fraction can exceed 1.0 on multi-core workloads because it uses process CPU time over wall time. No guard exists for zero wall delta, though one-minute sampling makes that unlikely. Producer failures would propagate out of `get_stats()`.

## Test Signals
Test coverage is mostly indirect through status/statistics web and CLI tests. Dedicated producer registration/counter tests would strengthen confidence in edge cases.
