<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRule.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRule.java

Purpose: `AbstractContainerSafeModeRule` is the shared base for Ratis and EC container safe-mode exit rules. It requires a configured percentage of closed or quasi-closed, non-empty containers to have their minimum replica count reported before SCM exits safe mode.

Important APIs and types: Subclasses implement `getContainerType` and `handleReportedContainer`. The base manages `initializeRule`, `reinitializeRule`, `process`, `validate`, `refresh`, `cleanup`, `isMissing`, `getCurrentContainerThreshold`, and status text. It uses `ContainerManager`, `ContainerID`, `ContainerInfo`, `NodeRegistrationContainerReport`, and `SafeModeMetrics`.

Control flow: Initialization snapshots closed/quasi-closed containers of the subclass type with keys, records each container's minimum required nodes, sets total count, and publishes the threshold metric. Processing maps container reports to IDs and delegates per-reported-container handling to subclasses. Validation either checks the report-driven threshold or, when report processing is disabled, scans manager state for any closed container with too few replicas.

State and persistence behavior: Runtime state is a concurrent map of containers still missing enough reports plus atomic totals and counters. `reinitializeRule` removes DELETED containers because datanodes will not report them during registration. The rule reads persisted SCM container state through `ContainerManager` but does not write it.

Dependencies and integration points: The rule subscribes to `SCMEvents.CONTAINER_REGISTRATION_REPORT` through `SafeModeExitRule`, updates safe-mode metrics, and is orchestrated by `SCMSafeModeManager`.

Risks: The status text says "at least N reported replica" even though Ratis and EC interpret N differently. New containers after datanode registration are intentionally not added during refresh. `isMissing` ignores containers no longer found, which is pragmatic but can hide state inconsistencies.

Test signals: Tests should cover threshold calculation, filtering by state/type/key count, report-driven counter updates in subclasses, deleted-container refresh, fallback validation against live replicas, metrics updates, cleanup, and invalid cutoff configuration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/safemode/AbstractContainerSafeModeRule.java -->
