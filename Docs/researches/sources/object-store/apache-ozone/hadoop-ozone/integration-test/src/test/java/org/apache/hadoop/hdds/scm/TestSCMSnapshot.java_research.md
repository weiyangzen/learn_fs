# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestSCMSnapshot.java

## Purpose

`TestSCMSnapshot` tests SCM HA snapshot creation and restart recovery. It ensures SCM transaction indexes advance after replicated metadata mutations and survive SCM restart.

## Important APIs, Types, And Functions

Setup configures pipeline creation interval and `OZONE_SCM_HA_RATIS_SNAPSHOT_THRESHOLD`, then starts a MiniOzoneCluster with three datanodes. The test uses `StorageContainerManager`, `ContainerManager`, `PipelineManager`, `RatisReplicationConfig`, `ContainerInfo`, and transaction info from the SCM HA DB transaction buffer.

## Control Flow

The test records initial transaction info, allocates containers through container manager and pipeline manager, verifies transaction index advancement, restarts SCM, then asserts the post-restart transaction index is at least the snapshot index and that allocated containers/pipelines remain accessible.

## State And Persistence Behavior

Container and pipeline records are persisted through SCM HA/Ratis state and snapshots. Restart validates recovery from on-disk DB and Ratis snapshot data.

## Dependencies And Integration Points

It integrates SCM HA transaction buffering, Ratis snapshot thresholding, container allocation, pipeline management, and MiniOzoneCluster restart.

## Risks And Test Signals

Failures indicate snapshot threshold misbehavior, lost transaction indexes, or missing container/pipeline metadata after restart. Because snapshots are threshold-driven, allocation count and timing matter.
