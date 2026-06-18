## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestReplicationSupervisor.java

Purpose: Comprehensive behavioral suite for `ReplicationSupervisor`, covering task lifecycle, metrics, deduplication, deadlines, SCM term filtering, EC reconstruction, reconciliation, priority ordering, queue limits, and dynamic thread-pool scaling.

Important APIs/types/functions: `ReplicationSupervisor`, `ReplicationSupervisorMetrics`, `ReplicationTask`, `ECReconstructionCoordinatorTask`, `ReconcileContainerTask`, `ReplicateContainerCommand`, `ReconstructECContainersCommand`, `ReconcileContainerCommand`, `ReplicationServer.ReplicationConfig`, `DatanodeConfiguration`, `StateContext`, `FakeReplicator`, `FakeECReconstructionCoordinator`, `BlockingTask`, and `OrderedTask`.

Control flow: Tests use direct executors for deterministic immediate execution, a discarding executor for stalled in-flight tasks, and a single-thread executor for queue-size checks. Normal/duplicate/failure tests assert request, success, failure, skipped, in-flight, queue, and container counts. Deadline tests fast-forward a `TestClock`; obsolete SCM term tasks are dropped. Multiple-replication tests mix replication and EC tasks and verify per-metric-name counters. Reconciliation tests validate success/failure/timeout metrics and duplicate reconcile command deduplication by container ID. Priority ordering blocks the executor, queues NORMAL and LOW tasks at different logical times, then validates priority-before-age order. State update tests verify stream-limit scaling for maintenance/decommission and queue limit doubling.

State and persistence behavior: Uses in-memory `ContainerSet` plus temporary tar metadata for import reserve-space tests. `ReplicationSupervisor` tracks in-flight queues, metrics, request timing, and dedupe keys. Some tests create real `MutableVolumeSet` committed-byte state.

Dependencies and integration points: Integrates replication commands, EC reconstruction, datanode operational state, container import/download, volume accounting, metrics collection, and SCM term context.

Risks and test signals: This is the central regression suite for replication scheduling. Timing and async wait loops can be flaky if executor behavior changes. The fake replicators assume same-thread execution in several tests, so executor choice is part of the contract.
