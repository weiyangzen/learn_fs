<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/tranquilizer.rs -->
# sources/object-store/garage/src/util/tranquilizer.rs

## Purpose
Adaptive throttling helper for background operations, sleeping or returning a throttled worker state based on recent work durations.

## Important APIs, types, and functions
`Tranquilizer` stores a bounded observation window and exposes `new`, `tranquilize`, `tranquilize_worker`, `reset`, and `clear`.

## Control flow
Each call observes time since the previous step, maintains a moving sum, computes delay as `tranquility * average_step_time`, and either sleeps or returns `WorkerState::Throttled`.

## State and persistence behavior
All state is in-memory timing data. It influences background workload pacing but is reset on process restart.

## Dependencies and integration points
Used by background workers that need to avoid consuming excessive resources. Integrates with Tokio sleep and `WorkerState`.

## Risks and test signals
Large first observations can over-throttle until the window rolls forward. `clear` does not reset `last_step_begin`; callers may need `reset`. Tests can use controlled durations or assert state transitions rather than exact sleep time.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/tranquilizer.rs -->
