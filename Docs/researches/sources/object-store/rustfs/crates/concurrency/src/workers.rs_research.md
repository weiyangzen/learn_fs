# sources/object-store/rustfs/crates/concurrency/src/workers.rs

## Purpose
Implements a cooperative async worker-slot limiter for long-running background workflows.

## Important APIs, types, and functions
`Workers` contains a Tokio `Mutex<usize>` for available slots, `Notify` for waiters, and fixed `limit`. Public methods are `new`, `take`, `give`, `wait`, and `available`.

## Control flow
`new` rejects zero capacity and returns an `Arc<Self>`. `take` loops until a slot is available, otherwise waits on `Notify`. `give` saturating-adds a slot, clamps to the limit, and notifies one waiter. `wait` loops until all slots are available, waiting on notifications between checks.

## State and persistence behavior
All state is in-memory slot count. Over-release is clamped, preventing the available count from exceeding the configured limit.

## Dependencies and integration points
Uses Tokio synchronization primitives and `tracing` debug/trace events. Background scanners, healers, or migration jobs can share an `Arc<Workers>` to bound concurrency.

## Risks and edge cases
This is not a fair semaphore; notified task ordering is Tokio scheduling dependent. If a task takes a slot and exits without `give`, `wait` can block forever. The test intentionally over-releases, so callers should still pair take/give carefully.

## Test signals
Tests cover concurrent task slot use and `wait`, plus over-release clamping to the limit.
