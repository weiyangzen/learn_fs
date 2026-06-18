# sources/object-store/rustfs/crates/obs/src/metrics/collectors/ilm.rs

Purpose: reports Information Lifecycle Management task and scan metrics: expiry pending tasks, transition active/pending tasks, immediate transition misses, queue backpressure, compensation scheduling/running, and versions scanned.

Important APIs/types: `IlmStats` has nine `u64` fields. `collect_ilm_metrics(&IlmStats)` returns a nine-metric vector using descriptors from `schema::ilm`.

Control flow: direct fixed vector creation with no labels or conditional branches.

State/persistence: no local state. ILM scheduler/task state is collected elsewhere and passed in as a snapshot.

Dependencies/integration: the metrics scheduler's background workflow task calls `collect_ilm_metric_stats().await`; when present, ILM metrics are emitted together with scanner metrics.

Risks: several fields distinguish different transition enqueue/backpressure states; if upstream naming changes, descriptor mapping must stay semantically aligned. Default zero values can hide absence of ILM instrumentation if optional source handling is bypassed.

Test signals: tests assert nine metrics, representative pending/scanned values, and default zero/no-label behavior.
