# sources/object-store/rustfs/crates/io-core/src/lock_optimizer.rs

Purpose: instrumentation and adaptive spin helper for lock-heavy paths.

Important APIs/types: `LockOptimizeConfig` enables/disables tracking, sets acquire timeout, max hold warning threshold, adaptive spin flag, and max spin iterations. `LockStats` records acquisitions, early releases, total/max hold time, contentions, and spin successes/failures. `LockOptimizer` exposes event hooks, `try_spin`, stats/config access, spin count, hold-time warning check, and reset. `LockGuard` is an RAII helper that records acquire on construction and release on drop.

Control flow: `try_spin` loads current spin count, repeatedly calls a caller-provided nonblocking acquire closure, issues `std::hint::spin_loop` on failure, records success/failure, and doubles/halves future spin count within bounds. Release tracking records duration and counts releases shorter than half the configured acquire timeout as early.

State and persistence: all metrics are in-memory atomics. `current_spin` is per optimizer instance.

Dependencies and integration: pure std; re-exported from `lib.rs` and demonstrated in the scheduler example.

Risks: this module does not acquire locks itself; correctness depends on callers placing hooks accurately. Adaptive spinning can burn CPU if used around locks that are not expected to become available quickly. Early release semantics are based on `acquire_timeout / 2`, which may not represent meaningful lock-hold quality. Average hold time divides total release duration by acquisitions, so unmatched acquire/release calls distort metrics.

Test signals: tests cover stats math, contention and spin rates, RAII guard duration tracking, adaptive spin changes, and disabled optimizer no-op behavior.
