# sources/storage-engines/tikv/components/concurrency_manager/src/lib.rs

Purpose: public API for TiKV transaction concurrency management. It combines an in-memory lock table with monotonic `max_ts` tracking guarded by PD-derived exact/drifted limits.

Important APIs and types: `ConcurrencyManager`, `TSOProvider`, `ActionOnInvalidMaxTs`, `AtomicActionOnInvalidMaxTs`, `InvalidMaxTsUpdate`, `MaxTsUpdateSource`, `IntoErrorSource`, `ValueDisplay`, and re-exported `KeyHandle`, `KeyHandleGuard`, `LockTable`. Prometheus gauges expose `max_ts` and `max_ts_limit`.

Control flow: `update_max_ts` ignores `TimeStamp::max`, selects an exact limit for non-TiDB checked request origins or a drifted limit otherwise, validates the update, optionally double-checks with PD TSO under timeout, reports/panics/errors based on configured action, then atomically raises `max_ts`. `set_max_ts_limit` stores monotonic exact and drifted limits. `lock_key` and `lock_keys` acquire per-key guards, sorting multi-key locks to avoid deadlock. Read checks delegate to the lock table. Global-min methods iterate lock handles.

State and persistence: all state is in-memory: atomics for max-ts and config, `AtomicCell<MaxTsLimit>`, lock table, optional TSO provider, and time provider. No disk persistence.

Dependencies and integration: integrates with PD client, request-origin protobufs, transaction locks/timestamps, failpoints, Prometheus, TiKV logging, and `LockTable`.

Risks: PD double-check is synchronous through `block_on_timeout` and can add latency on invalid paths. Safety depends on lock guards being held while memory locks should be visible. Drifted limits trade availability against false positives; exact checks for non-TiDB origins reduce that tolerance.

Test signals: unit tests cover locking order, max-ts monotonicity, exact-vs-drifted request-origin behavior, limit expiry, PD TSO double-check, panic/error/log actions, and network partition tolerance.
