# sources/storage-engines/foundationdb/fdbserver/workloads/LowLatency.cpp

## Purpose
Latency guard workload for high-priority read-version and commit operations. It periodically runs a system-immediate, lock-aware transaction and fails if latency exceeds configured thresholds.

## Important APIs, types, and functions
`LowLatencyWorkload` tracks `testDuration`, `maxGRVLatency`, `maxCommitLatency`, `checkDelay`, `testWrites`, `testKey`, `operations`, `retries`, and `ok`. `setup` adjusts worst-fit candidacy delay knobs in simulation; `_start` performs the latency checks.

## Control flow
Client 0 loops until `testDuration`, sleeping `checkDelay` between attempts. Each operation randomly chooses commit or GRV when writes are enabled, sets transaction options `PRIORITY_SYSTEM_IMMEDIATE` and `LOCK_AWARE`, either writes `testKey` and commits or calls `getReadVersion`, retries on errors, and compares elapsed time to the matching maximum.

## State and persistence behavior
When write testing is enabled, the workload repeatedly writes an empty value to `testKey`. It also changes simulated server knobs for candidacy delay. Runtime state is the `ok` flag and counters.

## Dependencies and integration points
Integrates with transaction priority options, database locks, GRV path, commit path, server knob plumbing, and tester failure-injection coordination. It disables Attrition.

## Risks and test signals
Thresholds are wall-clock simulation sensitive, and retry loops can hide transient errors while still causing latency failures. Signals are `LatencyTooLarge`, unsuppressed transaction failure traces, and metrics for operations/sec, operations, and retries.
