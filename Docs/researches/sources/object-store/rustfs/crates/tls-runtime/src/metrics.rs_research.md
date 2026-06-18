## sources/object-store/rustfs/crates/tls-runtime/src/metrics.rs

Purpose: declares shared TLS runtime metrics for global outbound publication, reload attempts, generations, skipped reloads, publication failures, and stale consumer generations.

Important APIs/types/functions: constants identify foundation and outbound consumers. `record_outbound_tls_publication` records publication count and gauges root/mTLS presence. `record_tls_generation`, `record_tls_reload_result`, `record_tls_reload_skipped`, `record_tls_publication_fail`, and `record_tls_consumer_stale_generation` update generic TLS metrics. `init_tls_metrics` registers descriptions for counters, gauges, and histogram.

Control flow and state: no local state; all effects go through `metrics` macros. `record_tls_reload_result` optionally records duration and generation, allowing callers with partial information such as server resolver reloads.

Dependencies and integration points: used by shared coordinator, outbound publisher, and reloadable server resolver. Labels use static `consumer`, `result`, and `reason` values.

Risks: using static consumer labels avoids cardinality problems, but downstream callers should not pass unbounded dynamic strings. Publication failure metrics do not include error classification.

Test signals: no direct tests. Runtime correctness depends on exercising reload paths and metrics backend integration.
