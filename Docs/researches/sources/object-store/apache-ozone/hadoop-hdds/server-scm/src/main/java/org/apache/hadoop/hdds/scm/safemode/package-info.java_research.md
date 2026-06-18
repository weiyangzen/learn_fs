# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/package-info.java

Purpose: This package descriptor documents the SCM safe mode package. The package groups the manager, rule factory, exit rules, and metrics used to delay SCM serving unsafe operations until startup conditions are satisfied.

Important APIs and types: The visible package members include the `SafeModeManager` status interface, `SafeModeExitRule` base class, `SafeModeRuleFactory`, `SafeModeMetrics`, and concrete rules for datanode, container, EC container, pipeline, and HA state-machine readiness.

Control flow: There is no executable control flow in this file. Package-level behavior is event-driven: datanode heartbeats and reports enter the SCM event queue, safe mode rules process those events, and the safe mode manager exits once required rules validate.

State and persistence behavior: No state is stored here. Package implementations keep runtime counters in memory and rely on SCM metadata managers, Ratis, and event handlers for durable state where applicable.

Dependencies and integration points: The package integrates SCM startup, datanode reports, container managers, pipeline managers, HA state-machine readiness, and metrics. It is part of the `server-scm` module and backs client-visible `inSafeMode` and rule-status APIs.

Risks: Package-info files can drift from real behavior because they are not executable. The concrete source files are the authoritative contract for safe mode rule ordering and semantics.

Test signals: Coverage should come from concrete safe mode manager/rule tests rather than this descriptor.
