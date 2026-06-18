# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/algorithms/SCMContainerPlacementMetrics.java

Purpose: Hadoop metrics source for topology-aware container placement activity.

Important APIs: static `create`, increment methods for request, attempt, success, and fallback counts, `unRegister`, testing getters, and `getMetrics`.

Control flow and state: `create()` returns an already registered source if available; otherwise it initializes a static `MetricsRegistry` and registers a new metrics source. `getMetrics()` snapshots the static registry into a record.

Dependencies and integration: used by placement policies to count allocation attempts and fallback choices. Tested indirectly by rack-aware/rack-scatter placement tests and metrics getters.

Risks: `registry` is static while metric fields are instance fields; after unregister/re-register sequences, stale registry behavior should be tested. Direct construction without `create()` may leave metric fields uninitialized. Test signals should include idempotent create and unregister behavior.
