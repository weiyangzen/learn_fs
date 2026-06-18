# sources/object-store/rustfs/crates/io-core/src/backpressure.rs

Purpose: lightweight concurrency backpressure monitor for I/O operations.

Important APIs/types: `BackpressureConfig` defines `max_concurrent`, high/low water marks, cooldown, and enable flag. `BackpressureState` is `Normal`, `Warning`, or `Critical`. `BackpressureMonitor` exposes `try_acquire`, `release`, counters, rejection rate, state, and `should_apply_backpressure`.

Control flow: `try_acquire` uses a compare-exchange loop on `current` so enabled mode never exceeds `max_concurrent` under contention. It increments processed on successful acquisition and rejected at capacity. State transitions use mutex-protected `state` and `last_state_change`; critical/active is reached near the high threshold, warning near low threshold. `release` decrements `current` and clears active when count drops near the low threshold. Disabled mode bypasses the cap and always increments current/processed.

State and persistence: all state is in memory: atomic counters, an atomic active flag, and mutexes for state and last transition time. There is no RAII permit type, so callers must release manually.

Dependencies and integration: pure standard library plus `thiserror`; re-exported from `lib.rs`. It is demonstrated by the scheduler example.

Risks: manual `release` creates leak/underflow risk if callers forget or double-release; `fetch_sub` on zero would wrap. State updates compare against the pre-increment value, so thresholds can be off by one. `cooldown` is only consulted by `should_apply_backpressure`, not by `try_acquire`, so it is advisory. Disabled mode can grow `current` without capacity bounds.

Test signals: tests validate config thresholds, invalid config, acquire/reject behavior, rejection rate, and disabled always-allow behavior.
