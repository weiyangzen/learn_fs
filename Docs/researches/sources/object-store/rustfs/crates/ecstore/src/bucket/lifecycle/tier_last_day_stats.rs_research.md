# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/tier_last_day_stats.rs

Purpose: Maintains rolling 24-hour tier usage counters for lifecycle transition accounting. `DailyAllTierStats` maps tier names to `LastDayTierStats`, and each `LastDayTierStats` stores 24 hourly `TierStats` bins plus the last update timestamp.

Important APIs and types: `LastDayTierStats::add_stats` advances the ring to the current UTC hour and adds a `rustfs_data_usage::TierStats` value into the current bin. `total` folds all bins using `TierStats::add`. `forward_to` is the key time-window maintenance method: it clears bins crossed since `updated_at`, or clears all bins if 24 or more hours have elapsed. The private `merge` helper aligns two snapshots to the newer timestamp before adding bins.

Control flow and state: The file is in-memory only. State mutation happens by hour, keyed from `OffsetDateTime::now_utc().hour()`. A timestamp with Unix value `0` is treated as unset and replaced with current time. The rolling window depends on wall-clock UTC and not a monotonic clock.

Dependencies and integration: Depends on `rustfs_data_usage::TierStats` arithmetic and `time::OffsetDateTime`. It is expected to be consumed by lifecycle/tier accounting code that aggregates transitioned object statistics by storage tier.

Risks: Clock jumps can clear or preserve bins unexpectedly because elapsed time is computed from wall-clock timestamps. `merge` is dead code and untested in current use. The hourly array is indexed by UTC hour, so sparse updates across day boundaries are handled, but only at hour precision.

Test signals: One unit test verifies that `total` sums multiple added records. There is no test for `forward_to` window clearing, day rollover, or `merge` alignment.
