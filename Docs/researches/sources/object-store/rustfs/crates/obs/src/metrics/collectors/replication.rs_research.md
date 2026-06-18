# sources/object-store/rustfs/crates/obs/src/metrics/collectors/replication.rs

Purpose: reports cluster-wide replication queue, worker, transfer-rate, and backlog metrics.

Important APIs/types: `ReplicationStats` includes averages, current values, last-minute queued bytes/count, maximums, and recent backlog count. `collect_replication_metrics(&ReplicationStats)` emits thirteen metrics.

Control flow: fixed vector construction with no labels. Integer fields are converted to `f64`; rate/average fields already use `f64` or signed averages for queued bytes/count.

State/persistence: no local state. Historical averages and maximums are maintained by upstream replication monitoring.

Dependencies/integration: used in the scheduler's bucket replication bandwidth task after bandwidth/detail stats are collected. This places global replication metrics on the same interval as bucket replication bandwidth by default.

Risks: `average_queued_bytes` and `average_queued_count` are signed `i64`; negative values would be emitted if upstream produces them. Mixed metric semantics in one struct require careful descriptor maintenance. No labels means multi-site/target-specific replication must be represented elsewhere.

Test signals: tests assert thirteen outputs, exact active/current and average active worker values, `report_metrics` compatibility, and default zero/no-label behavior.
