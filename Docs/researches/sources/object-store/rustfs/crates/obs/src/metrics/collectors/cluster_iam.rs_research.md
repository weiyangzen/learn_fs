# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster_iam.rs

Purpose: exposes IAM synchronization and plugin authentication service metrics, including sync durations, request/failure counts, age since last authn request, RTTs, and sync success/failure counts.

Important APIs/types: `IamStats` contains ten `u64` fields. `collect_iam_metrics(&IamStats)` returns ten descriptor-backed metrics from `schema::cluster_iam`.

Control flow: fixed vector conversion. Every field maps directly to one metric; there are no labels or conditional branches.

State/persistence: pure DTO conversion. Sync counters and timestamps are maintained by IAM/runtime sources outside this file.

Dependencies/integration: scheduler's supplementary cluster task calls `collect_iam_stats().await`; when it returns `Some`, these metrics are appended with cluster config, erasure set, and usage metrics before reporting.

Risks: mixed units are easy to confuse: duration fields are milliseconds, last authn request ages are seconds, RTT fields are milliseconds, and minute-window counters are counts for the last full minute. Dashboards and alerts must use descriptor help text and names rather than assuming a uniform unit.

Test signals: tests verify ten metrics, exact sync success descriptor/value, `report_metrics` compatibility, and zero/default behavior with empty labels.
