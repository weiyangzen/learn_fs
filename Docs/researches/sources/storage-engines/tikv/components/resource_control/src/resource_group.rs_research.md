# sources/storage-engines/tikv/components/resource_control/src/resource_group.rs

## Purpose
This file is the central in-memory resource-control model for TiKV resource groups. It owns resource group metadata, read/write scheduling controllers, background/foreground limiters, virtual-time fairness, two-phase scheduling state, and admission-control delay accounting. It bridges PD-supplied `ResourceGroup` protobuf settings with TiKV scheduler priority metadata and runtime limiter state.

## Important APIs, Types, And Functions
`ResourceGroupManager` is the top-level registry. It stores `DashMap<String, ResourceGroup>`, a fast `group_count`, registered `ResourceController`s, shared priority limiters, a single shared background limiter, foreground RU trackers, and config via `VersionTrack<Config>`. `new` installs a default RU-mode group with medium priority and max RU quota. `add_resource_group`, `remove_resource_group`, and `retain` synchronize the manager registry and all derived controllers. `derive_controller` creates a read or write `ResourceController` and backfills existing groups.

`RuTracker` tracks per-group RU consumption in 30-second ring-buffer buckets. `record`, `advance`, `current_rate`, `historical_rate`, and `refresh_cached_historical_rate` support foreground admission control and two-phase scheduling. `ResourceLimiter` instances in `ru_trackers` are per foreground group and are created lazily by `record_ru_consumption` or `get_foreground_group_limiter`.

`AdmissionDecision` and `DelaySlotGuard` implement pre-pool admission control. `admission_decision` combines token-bucket debt with delayed-request caps and emits admission metrics; `delay_slot_guard` ensures delayed slots are released on cancellation.

`ResourceController` implements `yatp::queue::priority::TaskPriorityProvider`. It maps `TaskMetadata` and `CommandPri` to encoded priorities based on group priority, virtual time, command level, override priority, and optional two-phase baseline state. `GroupPriorityTracker` holds per-group RU quota, weight, virtual time, and `is_over_baseline`.

## Control Flow
PD/service code calls manager CRUD methods when resource-group config changes. Read/write pools call `derive_controller` and then use `priority_of`/`get_priority` for YATP scheduling. Work completion calls `consume_penalty` to advance virtual time. Foreground CPU measurement calls `record_ru_consumption`, while `online_adjust_resource_quota` periodically refreshes trackers, decides whether groups are above historical baseline, tightens or ramps CPU limits, emits metrics, and evicts idle trackers.

`advance_min_virtual_time` first updates two-phase group flags when fair scheduling is enabled, then asks each controller to rebalance virtual times. `update_min_virtual_time` raises lagging groups toward the max VT or subtracts `RESET_VT_THRESHOLD` near overflow.

Background control is selected through `get_background_resource_limiter_with_priority`: explicit background settings on a group win, otherwise non-default groups without background settings can fall back to the default group's configured background task types.

## State And Persistence Behavior
All state is process-local and rebuilt from PD/service config. Group names are lowercased in the manager. Background limiters are intentionally shared globally; removing the last background group resets shared limiter rates to infinity to avoid stale throttling. Foreground RU trackers are lazy and garbage-collected when idle. Virtual time is atomic per group but its global rebalance is approximate and intentionally not fully atomic because overflow/reset paths are rare.

## Dependencies And Integration Points
The file depends on `kvproto` resource-manager and RPC context types, `tikv_util::resource_control::{TaskMetadata, TaskPriority}`, YATP priority queues, `dashmap`, `parking_lot`, `VersionTrack<Config>`, and this crate's metrics and `ResourceLimiter`. It is driven by `service.rs` for PD config, `worker.rs` for periodic quota adjustment, and read/write execution paths that attach resource control metadata.

## Risks
Admission slots must be released exactly once; `DelaySlotGuard` mitigates this but callers using manual release remain sensitive. Two-phase scheduling depends on periodic worker ticks; stale `ru_trackers` or missed `online_adjust_resource_quota` calls leave phase state inaccurate. `historical_rate` intentionally dilutes missing buckets, so recently created groups can be throttled aggressively after spikes. The `Shared` background limiter design means all background groups affect each other. Several operations hold locks while iterating groups/controllers, so very large group counts could increase update latency.

## Test Signals
The inline tests cover resource group CRUD, priority encoding, virtual-time reset and overflow failpoints, retain behavior, background limiter selection/fallback, RU tracker bucket math, two-phase RU-based scheduling, foreground limiter retrieval, and admission delay/reject behavior. Worker and service tests further exercise manager integration with quota adjustment and PD meta-storage updates.
