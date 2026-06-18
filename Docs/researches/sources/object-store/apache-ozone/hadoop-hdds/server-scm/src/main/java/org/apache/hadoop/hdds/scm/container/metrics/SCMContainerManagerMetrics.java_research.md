# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/metrics/SCMContainerManagerMetrics.java

Purpose: Hadoop metrics source for SCM ContainerManager operation and report counters.

Important APIs: static `create`, `unRegister`, increment methods for create/delete/list/container-report/ICR success and failure, and getters for all counters.

Control flow and state: private constructor; `create()` registers a new metrics source with `DefaultMetricsSystem` under source name `SCMContainerManagerMetrics`. Counters are mutable metrics objects reset by process restart and unregistered explicitly.

Dependencies and integration: used by ContainerManager and report handlers to expose operational counters in Ozone metrics context.

Risks: repeated `create()` without unregister may conflict depending on metrics system behavior; no idempotent get-existing logic unlike placement metrics. Counter fields are injected by metrics framework, so direct construction outside registration would leave null counters. Test signals should verify registration/unregistration and report handler increments for success/failure paths.
