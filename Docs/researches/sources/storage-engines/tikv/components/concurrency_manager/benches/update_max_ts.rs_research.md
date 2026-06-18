# sources/storage-engines/tikv/components/concurrency_manager/benches/update_max_ts.rs

Purpose: Criterion benchmark for the fast path of `ConcurrencyManager::update_max_ts`.

Important APIs and types: `benchmark_update_max_ts` creates a manager with `ActionOnInvalidMaxTs::Error`, no TSO provider, zero drift allowance, and a pre-set max-ts limit.

Control flow: the benchmark repeatedly calls `cm.update_max_ts(new_ts, || format!("benchmark-{}", new_ts))` with `new_ts` below the configured limit. The source closure is intentionally passed to exercise the generic `IntoErrorSource` path, though on the valid fast path it should not be evaluated into an error source.

State and persistence: updates only in-memory atomics and Prometheus gauges. Repeated calls mostly become no-ops after the first successful max-ts increase because `fetch_max` preserves the current maximum.

Dependencies and integration: depends on Criterion, `txn_types::TimeStamp`, and public concurrency manager APIs.

Risks: benchmark measures a stable, non-error path and does not cover PD double-check latency, expired limits, exact request-origin checks, or panic/error actions.

Test signals: performance signal for max-ts update overhead under normal conditions.
