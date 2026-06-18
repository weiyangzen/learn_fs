<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManagerIntegration.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManagerIntegration.java

Purpose: Exercises `ContainerStateManager` and `ContainerManager` behavior for allocation, owner scoping, restart recovery, matching-container selection, concurrent allocation distribution, lifecycle transitions, and replica-map mutation.

Important APIs and types: Uses `MiniOzoneCluster`, `StorageContainerManager`, `ContainerManager`, `ContainerStateManager`, `ContainerWithPipeline`, `ContainerInfo`, `ContainerID`, `ContainerReplica`, `LifeCycleEvent`, `LifeCycleState`, `ReplicationConfig`, and datanode replica protobuf states.

Control flow: Setup starts a three-datanode cluster with pipeline limit one and exits safe mode. Tests allocate containers through SCM client protocol, call `getMatchingContainer`, restart SCM without triggering container-report safe-mode exit, submit many concurrent matching-container calls, update lifecycle state through finalization/close/delete/cleanup, and directly add/remove `ContainerReplica` objects.

State and persistence behavior: Container metadata is persisted across SCM restart. The restart test verifies `OPEN` and `CLOSING` counts after allocated containers and finalized containers are reloaded. The lifecycle test exercises in-memory and persisted container counts. Replica-map tests manipulate runtime replica sets tied to container IDs.

Dependencies and integration points: Covers client protocol allocation, pipeline-manager container ownership counts, safe-mode restart behavior, replication config conversion, state-machine transition validation, and SCM's replica tracking.

Risks: The multithreaded matching-container test is marked flaky and fires many `CompletableFuture` tasks without collecting futures before sleeping, making timing and executor completion central. Owner-specific allocation depends on configured `OZONE_SCM_PIPELINE_OWNER_CONTAINER_COUNT`. A duplicate close event is issued to an already closed container to verify counts remain stable.

Test signals: Signals include distinct allocated container IDs, owner and replication metadata, five `OPEN` and five `CLOSING` containers after restart, matching-container cycling after per-owner capacity, balanced distribution under concurrent access, exact per-state counts through lifecycle transitions, and replica set contents after add/remove/reinsert operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/container/TestContainerStateManagerIntegration.java -->
