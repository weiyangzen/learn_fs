# sources/storage-engines/tikv/components/backup/src/softlimit.rs

## Purpose
Provides backup-side concurrency throttling. `SoftLimit` is a tokio semaphore wrapper whose capacity can grow or shrink at runtime, and `SoftLimitByCpu` computes a target concurrency from observed per-thread CPU usage.

## APIs, Types, And Functions
`SoftLimit::new`, `guard`, `resize`, and `current_cap` are the production-facing surface. Test-only `shrink` and `grow` exercise explicit permit changes. Internally, `take_tokens` acquires and forgets semaphore permits to reduce capacity, while `grant_tokens` adds permits. `CpuStatistics` abstracts CPU sampling; `ThreadInfoStatistics` implements it. `SoftLimitByCpu::get_quota` calculates available task slots as idle CPUs minus a reserved remainder with a floor of one.

## Control Flow
A caller awaits `guard()` before running work; dropping the permit releases concurrency. `resize` swaps the stored cap first, then either acquires permits to shrink or adds permits to grow. CPU-based callers sample usage, exclude selected thread names, compute quota, and then resize the shared limit.

## State And Persistence
All state is in memory: semaphore permits, an atomic capacity, CPU sampler state, total CPU quota, and `keep_remain`. There is no disk persistence. Shrinking can block until enough in-flight guards are released, which is the intended backpressure mechanism.

## Dependencies And Integration Points
Uses `tokio::sync::Semaphore`, TiKV `ThreadInfoStatistics`, and `SysQuota::cpu_cores_quota`. Backup workers can use it to dynamically avoid saturating the node while leaving CPU headroom for foreground workloads.

## Risks And Test Signals
The main risk is capacity/counter drift if semaphore operations fail or callers forget that shrinking waits for live work. CPU quota is approximate and can be inaccurate when non-TiKV processes share CPUs. Tests cover resizing under live tasks and CPU quota behavior with mocked usage and reserved cores.
