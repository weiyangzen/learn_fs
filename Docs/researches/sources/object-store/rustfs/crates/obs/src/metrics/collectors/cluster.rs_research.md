# sources/object-store/rustfs/crates/obs/src/metrics/collectors/cluster.rs

Purpose: provides cluster-wide capacity and object/bucket count metric conversion. It is the base aggregate cluster collector for raw capacity, usable capacity, used/free bytes, stale/missing capacity observations, object count, and bucket count.

Important APIs/types: `ClusterStats` is a `Debug + Clone + Default` DTO with eight unsigned counters/gauges. `collect_cluster_metrics(&ClusterStats) -> Vec<PrometheusMetric>` is the sole exported collector function.

Control flow: the collector creates a fixed eight-element vector. Each field maps directly to one descriptor in `schema::cluster` through `PrometheusMetric::from_descriptor`, with numeric conversion to `f64` and no labels.

State/persistence: stateless conversion only. It does not read storage or cache data; callers populate `ClusterStats` from `stats_collector::collect_cluster_and_health_stats`.

Dependencies/integration: depends on `report::PrometheusMetric` and `schema::cluster::*`. The scheduler's cluster task combines this output with `collect_cluster_health_metrics` and passes the aggregate vector to `report_metrics`.

Risks: semantic correctness depends on caller-populated capacity values and consistent byte units. Unsigned `u64` to `f64` conversion can lose integer precision for very large byte totals, a common Prometheus client tradeoff. No labels means accidental per-node values would overwrite aggregate semantics.

Test signals: tests assert eight metrics, exact values for raw capacity/used/object/bucket metrics, zero/default behavior, empty label vectors, and default struct field values.
