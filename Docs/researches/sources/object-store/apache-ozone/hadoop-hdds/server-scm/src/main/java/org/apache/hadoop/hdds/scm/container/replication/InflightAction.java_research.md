# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/InflightAction.java

Purpose: `InflightAction` is a small value object that records an in-flight replication-related action target and start time. It is used by replication tracking code to remember which datanode an operation targets and when it began.

Important APIs and behavior: the constructor stores a `DatanodeDetails` and a `long` timestamp. `getDatanode` is annotated `@VisibleForTesting`, while `getTime` is public production API.

Control flow: there is no branching or command flow in this class. It is a passive wrapper.

State and persistence: instances are immutable after construction. They are not persisted by this class; any timeout or ledger behavior belongs to the container pending-op or queue components that hold these objects.

Dependencies and integration: it depends only on `DatanodeDetails` and Guava's testing annotation. It sits in the replication package beside `InflightType`, `ContainerReplicaOp`, and pending-operation tracking.

Risks: because `getDatanode` is testing-visible rather than ordinary public API, production code should not rely on inspecting targets through this class unless visibility is intentionally changed. The timestamp has no unit encoded in the type; callers must consistently use the same clock and unit.

Test signals: direct tests are likely indirect through pending-operation timeout and command-tracking tests, especially `TestContainerReplicaPendingOps` and replication processor tests that assert in-flight scheduling and expiry behavior.
