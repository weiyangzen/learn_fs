## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ReconScmContainerSyncMetrics.java

Purpose: custom Metrics2 source for SCM container sync status, total duration, per-state sync duration, and per-state count drift.

Important APIs/types/functions: static `create`; `unRegister`; setters/getters for overall status/duration and state gauges; `getMetrics` snapshots gauges; status constants for in-progress/success/failure.

Control flow: constructor initializes gauges and metric names for OPEN, QUASI_CLOSED, CLOSED, and DELETED states. Metric names are generated from enum names via Guava `CaseFormat`. Unknown states passed to setters are ignored.

State and persistence: in-memory atomic gauges; no DB writes. Integrates with SCM container sync tasks and Metrics2 collector.

Risks: only selected lifecycle states are exported; other states silently return zero/ignore updates. Tests should cover metric-name generation, collector output, ignored states, concurrency through atomic values, and unregister lifecycle.
