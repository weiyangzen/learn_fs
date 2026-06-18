## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/metrics/ContainerHealthTaskMetrics.java

Purpose: Hadoop Metrics2 source for `ContainerHealthTask` runtime, success, and failure counters.

Important APIs/types/functions: static `create`; `unRegister`; `addRunTime`; `incrSuccess`; `incrFailure` (present after the read continuation); annotated `MutableRate` and `MutableCounterLong` fields.

Control flow: `create` registers a new metrics source named after the class with `DefaultMetricsSystem`; task code updates counters/rates during each run; `unRegister` removes the source.

State and persistence: in-memory metrics only. Integration with `ContainerHealthTask` and Hadoop Metrics2/Ozone metrics context.

Risks: duplicate registration can fail or replace depending on Metrics2 behavior if multiple task instances are created. Tests should cover counter/rate updates and unregister lifecycle; task tests should assert success/failure paths increment expected metrics.
