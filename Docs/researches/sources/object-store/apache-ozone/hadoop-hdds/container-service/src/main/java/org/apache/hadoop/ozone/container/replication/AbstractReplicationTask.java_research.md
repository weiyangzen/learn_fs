# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/AbstractReplicationTask.java

Purpose: supplies common lifecycle, priority, timing, and identity fields for datanode-side replication-like tasks executed by `ReplicationSupervisor`.

Important APIs and types: subclasses implement `runTask()`, `getMetricName()`, and `getMetricDescriptionSegment()`. Public accessors expose container ID, queued time, deadline, SCM term, priority, status, and whether the task may run only on in-service datanodes. `Status` enumerates `QUEUED`, `IN_PROGRESS`, `FAILED`, `DONE`, and `SKIPPED`. `setPriority`, `setStatus`, and `setShouldOnlyRunOnInServiceDatanodes` are mutation hooks for subclasses and supervisors.

Control flow and state: status is volatile to be visible across executor and observer threads. The queued timestamp is captured at construction using an injectable `Clock`, which allows deterministic tests. Deadline zero means no deadline. Priority defaults to normal and affects queue ordering through supervisor task runners.

Dependencies and integration: references SCM `ReplicationCommandPriority` and feeds metric names into supervisor counters. `ReplicationTask` is the main concrete subclass in this package.

Risks and test signals: uniqueness semantics are defined by subclasses, not this class. Tests should verify deadline interpretation, queued-time injection, status visibility, priority ordering values, and that out-of-service execution flags are set only for task types that need them.
