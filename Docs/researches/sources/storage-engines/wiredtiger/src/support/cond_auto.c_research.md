# sources/storage-engines/wiredtiger/src/support/cond_auto.c

## Purpose
Implements adaptive condition-variable waits. Wait intervals reset to a configured minimum when useful progress or a signal occurs, and grow toward a maximum when wakeups are unproductive.

## Important APIs, Types, and Functions
- `__wt_cond_auto_alloc(session, name, min, max, condp)` allocates a condition variable and initializes `min_wait`, `max_wait`, and `prev_wait`.
- `__wt_cond_auto_wait_signal(session, cond, progress, run_func, signalled)` adjusts the wait and calls `__wt_cond_wait_signal`.
- `__wt_cond_auto_wait(session, cond, progress, run_func)` is a wrapper that ignores the signalled output.

## Control Flow
On each wait, the code asserts auto-wait initialization. If the caller reports progress, it resets `prev_wait` to `min_wait`. Otherwise it computes a tenth-of-range delta and attempts an atomic compare-and-swap to increase `prev_wait` without exceeding `max_wait`. It then waits for `prev_wait`; a signal resets the next wait to minimum.

## State and Persistence Behavior
No durable state. Runtime state is in `WT_CONDVAR` wait fields and connection statistics (`cond_auto_wait`, skipped CAS, reset). Concurrent waiters may race to update `prev_wait`; losing the CAS is acceptable and counted.

## Dependencies and Integration Points
Wraps the lower-level WiredTiger condition-variable API and is used by background/server loops that want low latency during active work and lower wake frequency when idle. It depends on atomic CAS, wait/signal functions, optional run predicates, and stats.

## Risks
Incorrect min/max configuration can cause either busy waking or sluggish response. Because waiters update shared wait state concurrently, callers must accept approximate adaptation. A missing signal reset could leave a service slow to respond after idle periods.

## Test Signals
Unit tests should validate allocation fields, progress reset, no-progress growth capped at max, CAS-race tolerance, signal reset, stats increments, and behavior with a `run_func` that ends waits early.
