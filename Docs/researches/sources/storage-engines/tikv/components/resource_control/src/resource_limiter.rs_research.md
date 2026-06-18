# sources/storage-engines/tikv/components/resource_control/src/resource_limiter.rs

## Purpose
This file wraps TiKV token-bucket limiters into a reusable `ResourceLimiter` abstraction for CPU, aggregate IO, and write-only IO throttling. It records consumption/wait statistics and exposes rate-limit controls used by background, priority, and foreground admission-control paths.

## Important APIs, Types, And Functions
`ResourceType` enumerates `Cpu` and `Io` and provides label strings. `ResourceLimiter::new` constructs CPU and IO `QuotaLimiter`s, a dedicated `write_io_limiter`, a version, a background flag, and optional priority wait histogram. `consume` charges CPU micros, read/write bytes, and optionally write-only IO; it returns the maximum wait duration and records priority wait metrics. `admission_delay` probes accumulated token-bucket debt with zero consumption and includes write IO debt for writes. `async_consume` sleeps on `GLOBAL_TIMER_HANDLE`.

`QuotaLimiter` wraps `tikv_util::time::Limiter`. `set_rate_limit` treats near-zero rates as infinity. `consume` and `consume_io` update total wait, byte counters, and request count. `GroupStatistics` snapshots limiter counters and supports saturating subtraction and division by elapsed seconds.

## Control Flow
Quota adjustment workers mutate limiter rates through `get_limiter(...).set_rate_limit` and `get_write_io_limiter`. Runtime request paths call `consume` either to build debt without waiting, to wait inline, or to query debt before entering a pool via `admission_delay`. Metrics are updated at consumption time and later read by workers/services via `get_limit_statistics`.

## State And Persistence Behavior
Limiter state is in-memory token-bucket state plus atomic counters. It is not persisted. `version` is included in statistics so reporters can detect limiter replacement. The same `ResourceLimiter` can be shared by multiple resource groups, especially the global background limiter.

## Dependencies And Integration Points
The limiter depends on `file_system::IoBytes`, `tikv_util::time::Limiter`, Prometheus histograms, `GLOBAL_TIMER_HANDLE`, and `TaskPriority`. `resource_group.rs` owns manager-level limiter selection; `worker.rs` adjusts rates; `service.rs` reports background consumption; execution paths consume against the returned limiter.

## Risks
Zero and extremely small rates are normalized to infinity, so callers cannot express a complete stop with `0`. `admission_delay` increments request counters even on zero probes when rates are finite, which is useful for stats but can surprise metric consumers. Write IO pressure is separate from aggregate IO only when callers pass `skip_compaction_pressure = false`.

## Test Signals
This file has no local test module, but its behavior is heavily exercised by `resource_group.rs` admission tests, `worker.rs` background/priority limiter tests, and service background RU reporting tests.
