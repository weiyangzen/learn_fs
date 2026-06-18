# sources/storage-engines/tikv/components/resource_control/src/worker.rs

## Purpose
`worker.rs` contains periodic adaptive quota workers for resource control. It samples process CPU and IO usage, adjusts the global background limiter, adjusts foreground per-group admission-control limits, applies compaction-pressure write IO throttling, and manages priority-class CPU limiters.

## Important APIs, Types, And Functions
`ResourceStatsProvider` abstracts system sampling. `SysQuotaGetter` implements it with process CPU stats, `SysQuota::cpu_cores_quota`, `fetch_io_bytes`, and configured IO bandwidth.

`GroupQuotaAdjustWorker` drives background and foreground control. `adjust_quota` enforces a minimum one-second interval, reads CPU once, calls `background_adjust_quota`, then feeds CPU utilization to `ResourceGroupManager::online_adjust_resource_quota`. Background adjustment caps configured utilization at `fg_cpu_throttle_threshold`, linearly scales from target to a floor between `bg_cpu_throttle_threshold` and foreground threshold, only tightens while under pressure, and recovers by 10 percent when idle. It also updates background metrics and the manager's `bg_cpu_at_floor` flag. `adjust_write_io_by_compaction_pressure` controls the write-only IO limiter between configured floor and ceiling.

`PriorityLimiterAdjustWorker` adjusts medium/low priority CPU limiters. It fast-paths single-group and low-CPU cases to infinity, derives per-priority CPU and wait stats, reserves high priority, and assigns remaining quota to lower priorities according to `priority_ctl_strategy`.

## Control Flow
External scheduling invokes workers periodically, nominally every `QUOTA_ADJUST_DURATION`. The background worker uses cumulative limiter stats to compute per-second background consumption and system utilization. Foreground throttling occurs only after background CPU is at its floor. Priority adjustment reads limiter and YATP wait histograms, then sets CPU rate limits on priority limiters.

## State And Persistence Behavior
Worker state is in-memory: last adjustment time, previous limiter statistics, previous background presence, histogram baselines, and last low/single-group flags. It does not persist across restart. When no background groups exist, background is considered at floor so foreground logic may proceed without waiting for background squeezing.

## Dependencies And Integration Points
The file depends on `file_system` IO counters, `tikv_util` process stats, system quota, thread names, YATP metrics, Prometheus metrics from this crate, `ResourceGroupManager`, and `ResourceLimiter`. It is the periodic companion to `resource_group.rs` and the source of dynamic rate-limit changes used by runtime request paths.

## Risks
Quota behavior is sensitive to sampling interval and process-stat accuracy. IO utilization uses bytes since last sample and returns zero if sampled too frequently. Background recovery is intentionally gradual and only occurs under low utilization, so stale throttling can persist after load drops. Shared background limiter semantics mean all background groups are globally throttled. Priority logic assumes YATP histograms are registered for the named pools/priorities.

## Test Signals
Tests cover background limiter adjustment, infinite-RU foreground groups with background throttling, priority limiter adjustment, tiered load shedding, compaction-pressure write IO throttling, and the invariant that multiple background groups share one global budget rather than splitting it.
