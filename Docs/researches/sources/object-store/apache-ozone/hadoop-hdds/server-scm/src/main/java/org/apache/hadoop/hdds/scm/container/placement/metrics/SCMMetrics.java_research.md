# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/placement/metrics/SCMMetrics.java

Purpose: Storage Container Manager metrics source for container report totals, last report gauges, DB checkpoint metrics, and bounded Ratis event text.

Important APIs: static `create`, setters/increment/decrement methods for container stats, `setLastContainerStat`, `incrContainerStat`, `decrContainerStat`, `addRatisEvent`, metric getter `getRatisEvents`, `getDBCheckpointMetrics`, and `unRegister`.

Control flow and state: registers with `DefaultMetricsSystem`; creates `DBCheckpointMetrics`; keeps a synchronized `LinkedList` of formatted Ratis events capped by configured max size.

Dependencies and integration: used by SCM report processing and Ratis event tracking; reads `OZONE_SCM_RATIS_EVENTS_MAX_LIMIT` from config.

Risks: `create()` is not idempotent; repeated registration can conflict. Counter decrements are implemented as negative increments, so totals can go negative. Tests should cover bounded event eviction, stat gauge/counter updates, unregister behavior, and DB checkpoint metrics creation.
