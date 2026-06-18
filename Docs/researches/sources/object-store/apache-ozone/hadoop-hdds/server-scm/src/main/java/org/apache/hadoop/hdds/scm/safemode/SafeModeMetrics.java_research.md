# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/SafeModeMetrics.java

Purpose: `SafeModeMetrics` is the metrics source for observing SCM safe mode progress. It reports configured thresholds, current progress counters, safe mode state, refresh activity, and exit duration while SCM is starting and waiting for required datanode, container, and pipeline signals.

Important APIs and types: `create()` registers the source with `DefaultMetricsSystem` under `SafeModeMetrics`. Setters update gauges for container thresholds, pipeline thresholds, datanode thresholds, current healthy pipelines, current safe mode flag, safe mode exit duration, and last container-rule refresh durations by replication type. Increment methods update counters for reported RATIS containers, EC data replicas, pipeline reports, registered datanodes, and refresh calls.

Control flow: Safe mode rules and the manager call these methods as reports arrive or as state is refreshed. `setNumContainerReportedThreshold` and `setLastContainerSafeModeRuleRefreshDurationMs` branch on `HddsProtos.ReplicationType`, with RATIS and EC using separate gauges. Unsupported container threshold types fail fast with `IllegalArgumentException`.

State and persistence behavior: Metrics are in-memory Hadoop metrics objects. They are not persisted to RocksDB or local files. `unRegister()` removes the source from the default metrics system during shutdown.

Dependencies and integration points: The class depends on Hadoop metrics2 annotations and mutable metric primitives, and is consumed by `SCMSafeModeManager` plus concrete safe mode rules. It is externally visible through SCM metrics scraping and JMX-style metric endpoints.

Risks: Counters such as current reported container counts are monotonic unless callers explicitly reset by replacing the metrics instance, so tests and restarts must avoid reusing registered sources. Unsupported replication types in threshold setters will break callers if future replication modes are added without metric handling.

Test signals: Tests should assert metric registration/unregistration, threshold gauge values, safe mode flag 1/0 transitions, RATIS versus EC branch behavior, refresh counters, and exit duration publication.
