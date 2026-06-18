# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MultiNodePipelineBlockAllocator.java

## Purpose
`MultiNodePipelineBlockAllocator` is a deterministic test block allocator for pipelines with multiple datanodes, primarily EC tests. It pre-creates a mock cluster and allocates block pipelines using a sliding-window node selection model.

## Important APIs, Types, And Functions
The constructor receives configuration, required pipeline node count, and cluster size, then creates `DatanodeDetailsProto` members with stable UUID bits and RATIS ports. `getClusterDns` exposes those nodes for tests. `allocateBlock` builds a pipeline with replication info from `KeyArgs`, adds members through `addMembers`, sets EC config when needed, and returns one `KeyLocation` with a sequential local block ID and configured SCM block size.

## Control Flow
`addMembers` advances a `start` cursor through the cluster, skipping datanodes present in the provided `ExcludeList`. For EC, it also assigns replica indexes starting at 1. If it cannot find enough non-excluded nodes in one pass through the cluster, it throws `IllegalStateException`.

## State And Persistence Behavior
State includes `blockId`, `requiredNodes`, immutable `conf`, prebuilt `clusterDns`, and the mutable sliding-window `start` cursor. It creates deterministic but in-memory allocation state only.

## Dependencies And Integration Points
It implements `MockBlockAllocator` for `MockOmTransport`, uses `OzoneConfigKeys.OZONE_SCM_BLOCK_SIZE`, and integrates with EC output-stream tests that assert predictable block groups, failed-node exclusions, and retry allocation.

## Risks And Edge Cases
The allocator uses one fixed pipeline ID for all allocations and fixed container ID 1, simplifying reality. It does not model SCM capacity, pipeline lifecycle, rack awareness, or container selection. If excluded nodes grow too large, allocation fails immediately with `IllegalStateException`, which some tests intentionally assert.

## Test Signals
`TestOzoneClient.testPutKeyWithECReplicationConfig` and many `TestOzoneECClient` cases depend on deterministic multi-node allocation, including retry tests that expect storage counts and block group counts to match sliding-window allocation.
