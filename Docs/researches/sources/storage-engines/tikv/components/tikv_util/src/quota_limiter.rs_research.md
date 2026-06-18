# sources/storage-engines/tikv/components/tikv_util/src/quota_limiter.rs

## Purpose
Implements foreground/background throttling for CPU time, read/write bandwidth, and background IOPS so TiKV tasks can trade completion latency for stable resource usage.

## Important APIs, Types, and Functions
- `LimiterItems` bundles CPU, write bandwidth, read bandwidth, and IOPS `Limiter`s.
- `QuotaLimiter::new` builds separate foreground/background limiters and stores max delay plus auto-tune flag.
- `Sample` accumulates read bytes, write bytes, CPU time, IOPS, and CPU-limit enablement.
- `Sample::observe_cpu` and `observe_cpu_async` measure thread CPU time with `cpu_time::ThreadTime`.
- `QuotaLimiter::consume_sample` consumes a sample asynchronously and delays via `GLOBAL_TIMER_HANDLE`.
- `QuotaLimitConfigManager` applies online config changes.

## Control Flow
Callers create a sample for foreground or background work, record resource usage as the task runs, then call `consume_sample`. The limiter computes independent delay durations for CPU microseconds, write bytes, read bytes, and IOPS. The chosen delay is the maximum of those durations, capped by `max_delay_duration` when nonzero, and awaited through the global timer. Online config dispatch mutates individual limiter speeds and flags.

## State and Persistence Behavior
Limiter buckets, consumed counters, max delay, and auto-tune flags are in memory. Atomic fields allow concurrent reads/updates of config knobs. No throttling state persists beyond process lifetime.

## Dependencies and Integration Points
Depends on `crate::time::Limiter`, `GLOBAL_TIMER_HANDLE`, `ReadableDuration`, `ReadableSize`, `online_config::ConfigManager`, `cpu_time::ThreadTime`, and `futures` compatibility adapters. It integrates with runtime paths that can sample IO/CPU work units.

## Risks
CPU tracking measures thread CPU during guarded scopes or future polls, so uninstrumented work is invisible. `ThreadTime` is declared `Send` only through an unsafe wrapper because it is used within each poll. Max-delay capping can intentionally under-enforce configured rates. Config key names must match online config producers exactly.

## Test Signals
The unit test exercises foreground and background CPU, read/write bandwidth, max-delay capping, zero-as-unlimited behavior, dynamic limiter changes, IOPS-only limiting, and combined IOPS/read throttling.
