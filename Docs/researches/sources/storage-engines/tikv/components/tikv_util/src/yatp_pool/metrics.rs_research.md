# sources/storage-engines/tikv/components/tikv_util/src/yatp_pool/metrics.rs

Purpose: Prometheus metrics for YATP future pools and schedule latency.

Important APIs/types/functions: `FUTUREPOOL_RUNNING_TASK_VEC`, `FUTUREPOOL_HANDLED_TASK_VEC`, `YATP_POOL_SCHEDULE_WAIT_DURATION_VEC`, and `YATP_POOL_SCHEDULE_EXEC_DURATION_VEC`.

Control flow: lazy-static registration creates gauges/counters and histograms labeled by pool name and priority. Histogram buckets span roughly 10 microseconds to 42 seconds.

State and persistence: process metric state only.

Dependencies/integration: consumed by `future_pool.rs` and `yatp_pool/mod.rs` local histogram flushing.

Risks: label cardinality follows pool names and priority strings; changing names changes metric continuity.

Test signals: schedule wait histogram counts are asserted in YATP pool tests.
