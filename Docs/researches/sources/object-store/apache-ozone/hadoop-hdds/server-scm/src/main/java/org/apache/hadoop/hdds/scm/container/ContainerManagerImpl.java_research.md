<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManagerImpl.java

## Purpose
Implements the SCM `ContainerManager` facade. It coordinates pipeline selection, container ID generation, persistent container-state mutations, in-memory replica updates, block allocation matching, and container-manager metrics.

## Important APIs, Types, And Functions
The constructor builds a `ContainerStateManagerImpl` through its HA proxy and registers `SCMContainerManagerMetrics`. `allocateContainer(ReplicationConfig, owner)` selects or creates an open pipeline, then calls private `allocateContainer(Pipeline, owner)`. `updateContainerState`, `transitionDeletingOrDeletedToTargetState`, `updateContainerInfo`, and `deleteContainer` delegate locked mutations to `ContainerStateManager`. Replica methods validate existence before delegating. `getMatchingContainer` uses pipeline container IDs, owner filtering, open-container limits, exclusions, and round-robin state-manager matching.

## Control Flow
Allocation first reads open pipelines under the pipeline-manager read lock and local lock. If none exist, it creates a pipeline, opens EC pipelines, waits for readiness, then retries selection. New container creation obtains a sequence ID, checks and records pipeline space, builds `ContainerInfoProto`, and adds it to the state manager. Matching-container selection synchronizes on pipeline ID, may allocate if the pipeline is below its open-container limit, filters by owner and exclusions, and allocates again if no existing container has space.

## State And Persistence
Persistent state is delegated to `ContainerStateManager` and the SCM DB transaction buffer. Replica sets are in-memory state-manager entries. The class also updates metrics for create/delete/list/report outcomes and uses pipeline-manager allocation accounting.

## Dependencies And Integration Points
Depends on `PipelineManager`, `SCMHAManager`, `SequenceIdGenerator`, `ContainerReplicaPendingOps`, `SCMContainerManagerMetrics`, `ContainerStateManagerImpl`, replication configs, and the container table. It sits between SCM APIs/report handlers and the replicated container state manager.

## Risks And Test Signals
Lock ordering with pipeline-manager read locks and the local lock is important for allocation. `allocateContainer` can return null when a selected pipeline lacks space, so callers must handle that. `getContainersForOwner` mutates the navigable set returned by pipeline manager and logs missing container metadata. Tests should cover no-pipeline allocation, EC pipeline opening, pipeline space exhaustion, owner filtering, excluded containers, lifecycle mutation errors, replica validation, delete metrics, and reinitialization.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerManagerImpl.java -->
