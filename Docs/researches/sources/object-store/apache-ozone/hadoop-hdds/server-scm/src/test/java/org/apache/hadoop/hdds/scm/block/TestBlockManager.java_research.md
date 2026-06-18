# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/block/TestBlockManager.java

## Purpose

This test class validates SCM block allocation behavior through a realistic in-process `StorageContainerManager` fixture. It covers successful allocation, pipeline exclusion, concurrent allocation, distribution across containers and disks, safe mode checks, oversized blocks, pipeline creation fallback, and reopening containers after close events.

## Important APIs, Types, and Functions

- `BlockManagerImpl.allocateBlock` is the primary API under test.
- `PipelineManagerImpl`, `MockRatisPipelineProvider`, `ContainerManagerImpl`, `SCMMetadataStoreImpl`, `SequenceIdGenerator`, `SCMSafeModeManager`, and `StorageContainerManager` form the fixture.
- `ExcludeList` influences pipeline selection.
- `CloseContainerEventHandler` and `DatanodeCommandHandler` simulate SCM event-driven container and pipeline lifecycle.
- `verifyNumberOfContainersInPipelines` and `expectedContainersPerPipeline` validate pipeline container counts.

## Control Flow and State Behavior

`setUp` builds a temporary SCM stack with safemode disabled, a mock node manager, HA stubs, metadata tables, pipeline manager, container manager, event queue, lease manager, and SCM context moved out of safe mode. Tests create and open RATIS pipelines, then call `allocateBlock` with a fixed 128 MB size and owner `OzoneConsts.OZONE`.

Allocation tests assert that excluded pipelines are avoided when alternatives exist but may be reused when all pipelines are excluded. Concurrent tests launch single-thread executors and require all futures to complete. Distribution tests constrain pipeline-per-datanode and healthy volume counts, then verify blocks are spread across the expected number of open containers. Safe mode tests move SCM context into `PRE_CHECKS_PASSED` and expect the safe-mode precheck error, then verify allocation after exiting safe mode. Closed-container tests fill pipelines, fire `CLOSE_CONTAINER` events for each container, wait for counts to drop, and confirm allocation recreates the expected container count.

## State and Persistence

The fixture uses a real temporary SCM metadata store and sequence-id table. Pipeline and container state are persisted in the test DB during the test lifecycle and closed in `cleanup`. Event queue state is in-memory. No state survives beyond the temp directory.

## Dependencies and Integration Points

The test integrates block manager allocation with pipeline creation/opening, container allocation, SCM metadata tables, event publishing, safe-mode state, HA transaction stubs, lease management, and node capacity/volume reporting from `MockNodeManager`.

## Risks and Test Signals

Risk areas include race conditions in parallel allocation, container-count accounting under multi-disk limits, stale excluded-pipeline logic, and hidden dependence on event timing. Signals are strong because the tests use production managers rather than pure mocks and assert exact container distribution and safe-mode error text.
