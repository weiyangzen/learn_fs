<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/progress.rs -->
# sources/object-store/rustfs/crates/heal/src/heal/progress.rs

## Purpose

`progress.rs` defines lightweight serializable progress and aggregate statistics models for heal tasks. It is an in-memory/status-reporting layer used by tasks and manager code, separate from durable resume/checkpoint persistence.

## Important APIs, types, and functions

- `HealProgress` stores scanned/healed/failed object counts, processed bytes, current object, progress percentage, start time, last update time, and estimated completion time.
- `HealProgress::new` initializes start and last update timestamps.
- `update_progress` sets counters and bytes, updates last-update time, and computes `progress_percentage`.
- `set_current_object` updates current object and timestamp.
- `is_completed` checks either percentage >= 100 or healed+failed >= scanned when scanned is positive.
- `get_success_rate` computes healed / (healed + failed).
- `HealStatistics` stores total/successful/failed/running tasks, total healed objects/bytes, and last update time.
- `HealStatistics::new`/`Default` initialize zero counters.
- Statistics mutators update completion counts, running counts, healed object/byte totals, and timestamps.
- `HealStatistics::get_success_rate` computes successful tasks / completed tasks.

## Control flow

All methods are synchronous data updates. `update_progress` replaces the counters rather than incrementing them. Its percentage denominator is `scanned + healed + failed`, so it behaves more like a ratio of healed to all reported counters than a conventional processed/scanned percentage. Completion can still be detected when `objects_healed + objects_failed >= objects_scanned`.

## State and persistence behavior

Both structs derive `Serialize` and `Deserialize`, but this file does not persist them. Timestamps are `SystemTime`. `estimated_completion_time` is present but not computed by this implementation. Consumers wrap these structs in locks or embed them in task state.

## Dependencies and integration points

The file depends only on `serde` and `std::time::SystemTime`. `HealManager` owns `HealStatistics`, `HealTask` and `ErasureSetHealer` use `HealProgress`, and channel/status APIs can return progress through manager methods.

## Risks and edge cases

- The progress percentage formula can be surprising: with `scanned=10`, `healed=8`, and `failed=2`, percentage is 40 rather than 100, because scanned is included in the denominator along with outcomes.
- `is_completed` may report complete even when `progress_percentage` is below 100 if healed+failed reaches scanned.
- No rate or ETA calculation is implemented despite the ETA field.
- `update_progress` can move counters backward if the caller supplies smaller values.
- Statistics do not decrement `running_tasks` automatically; callers must set the count correctly.

## Test signals

Tests cover initialization, progress updates including zero and all-healed cases, current-object timestamp updates, completion checks by percentage and processed counts, progress success rate, statistics defaults, completion updates, running count updates, healed object accumulation, and statistics success rate. Additional useful tests would document the progress-percentage semantics explicitly for UI/API consumers.

<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/heal/src/heal/progress.rs -->
