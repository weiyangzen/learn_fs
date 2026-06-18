## sources/object-store/rustfs/crates/targets/src/runtime/tls/metrics.rs

Purpose: declares and records metrics for per-target TLS reload behavior.

Important APIs/types/functions: `init_target_tls_metrics()` describes counters, gauges, and histograms for reload attempts, skipped reloads, current generation, reload duration, publication failures, and stale generation observations. `record_target_tls_reload_result(target, result, duration_secs, generation)` increments attempts, records duration, and updates generation. `record_target_tls_reload_skipped`, `record_target_tls_publication_fail`, and `record_target_tls_stale_generation` provide focused counters.

Control flow and state: no in-memory state beyond metrics recorder side effects. Labels use `target_id`, `result`, and `reason` with owned strings so target labels can be dynamic.

Dependencies and integration points: used by the target TLS coordinator and potentially by target send paths that detect stale generation. It depends on the `metrics` crate macros.

Risks: unbounded `target_id` labels can increase metric cardinality if target labels include user-generated or high-churn values. The histogram is recorded for successes in the coordinator; some failure paths use only publication-fail counters and do not record reload duration/result.

Test signals: no local tests. Indirect signal comes from coordinator paths invoking these functions; metric registration correctness depends on runtime metrics backend behavior.
