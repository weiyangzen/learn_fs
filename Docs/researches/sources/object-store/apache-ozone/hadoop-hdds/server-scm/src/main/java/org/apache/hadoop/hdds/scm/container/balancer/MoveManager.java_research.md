# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/balancer/MoveManager.java

Purpose: schedules, tracks, and completes balancer replica moves as a two-phase operation: replicate to target, then delete from source.

Important APIs/types: `move`, `opCompleted`, timeout setters, `setIncludeNonStandardContainers`, `getPendingMove`, `resetState`, nested `MoveOperation`, and `MoveResult`. It implements `ContainerReplicaPendingOpsSubscriber`.

Control flow and state: `move()` validates source/target health and in-service status, source existence, target absence, container lifecycle, health before and after projected move, and no pending ADD/DELETE ops. It stores one pending move per `ContainerID` in a `ConcurrentHashMap`, sends a low-priority replicate command, then reacts to pending-op callbacks. Successful ADD triggers source delete if future health remains acceptable; successful DELETE completes the future. Expired ADD/DELETE complete with timeout-specific results.

Dependencies and integration: depends on `ReplicationManager`, `ContainerManager`, pending ops notifications, node status, container health results, Ratis leader checks, and replica indexes. Heavily tested by `TestMoveManager` and balancer task/node-limit tests.

Risks: synchronization is on `ContainerInfo`, but pending-op notifications can race with health changes; TODO notes lock coupling with pending ops. `includeNonStandardContainers` relaxes over-replication/quasi-closed rules and needs focused coverage. Unexpected exception paths complete futures but callback failure may leave map entries in some branches. Test signals should include every `MoveResult`, timeout callback ordering, quasi-closed/over-replicated moves, source disappearing after add, duplicate move requests, and leader loss.
