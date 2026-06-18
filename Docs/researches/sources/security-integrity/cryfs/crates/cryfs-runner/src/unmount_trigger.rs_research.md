# sources/security-integrity/cryfs/crates/cryfs-runner/src/unmount_trigger.rs

## Purpose
Defines a clonable cancellation trigger used to stop the mounted filesystem because of idle timeout or integrity violation.

## Important APIs, types, and functions
- `TriggerReason::{UnmountIdle, IntegrityViolation}` records why cancellation happened.
- `UnmountTrigger::new`, `trigger_after_idle_timeout`, `trigger_now`, `waiter`, and `trigger_reason`.
- Internally uses `tokio_util::sync::CancellationToken` and `Arc<Mutex<Option<TriggerReason>>>`.

## Control flow
Idle timeout spawns a tokio task that polls `last_filesystem_access_time.elapsed()` once per second. If the threshold is exceeded, it calls `trigger_now`. `trigger_now` stores the reason under mutex before cancelling the token, ensuring mount shutdown code can read the reason after cancellation.

## State and persistence behavior
All state is runtime-only: cancellation token, trigger reason, and access timestamp reference. No disk persistence.

## Dependencies and integration points
Used by `runner.rs` to pass a waiter into `Backend::mount` and to convert post-unmount reason into success or `CliErrorKind::IntegrityViolation`.

## Risks and edge cases
The idle polling task runs until it triggers; there is no explicit cancellation if mount ends for another reason. `Mutex` poisoning would panic on unwrap. Time is based on `AtomicInstant` relaxed loads and wall-clock-ish elapsed behavior.

## Test signals
The file has a TODO for tests. Needed tests include trigger reason ordering, idle timeout firing after access gap, no early idle fire after access update, and integrity violation reason propagation.
