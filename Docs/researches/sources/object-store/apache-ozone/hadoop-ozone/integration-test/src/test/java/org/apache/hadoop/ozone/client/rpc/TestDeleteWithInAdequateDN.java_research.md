# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestDeleteWithInAdequateDN.java

## Purpose
This integration test verifies delete behavior when a RATIS/THREE pipeline has an inadequate datanode during container close and block deletion. It ensures chunks are not deleted from closed replicas until the lagging follower rejoins and catches up.

## Important APIs, types, and functions
The fixture starts exactly three datanodes, limits pipelines, lengthens stale/dead/no-leader/pipeline-creation timeouts to prevent automatic early repair, and accelerates block deletion services. It uses `XceiverClientManager`, `XceiverClientSpi`, raw `CloseContainer` protobuf requests, `RatisTestHelper`, `ContainerStateMachine` metrics, `KeyValueHandler`, `BlockData`, `ChunkInfo`, `OzoneTestUtils.flushAndWaitForDeletedBlockLog`, and `StorageContainerException`.

## Control flow
The test creates key `ratis`, writes and flushes data, captures the single key location and container ID, locates leader and follower in the factor-three pipeline, and shuts down one follower. It writes again and closes the key, then sends a close-container command to the pipeline. After OM lookup, it fetches the block ID and reads chunk metadata from the leader's `KeyValueHandler`.

The key is deleted through the object-store bucket API and SCM deleted-block logs are flushed. The test then reads each chunk from the leader and expects success, proving deletion has not yet removed data while the follower is behind. It records read-state-machine metrics, evicts state-machine cache, restarts the follower, waits, asserts read-state-machine ops increased without failures, waits for deletion, and finally checks all datanodes throw `StorageContainerException` with `UNABLE_TO_FIND_CHUNK` when reading the old chunks.

## State and persistence behavior
The test observes chunk files, block deletion logs, state-machine read metrics, container closure, and follower catch-up. It validates a persistence invariant: closed replicas retain chunks until deletion is safe across the repaired replication group.

## Dependencies and integration points
This file integrates OM delete, SCM deleted block log flushing, datanode block deletion services, RATIS follower recovery, state-machine cache eviction, and low-level chunk manager reads.

## Risks and test signals
The test uses sleeps after follower restart and before final deletion checks, so timing is a risk. Assumptions skip the test if the initial key has more than one location or pipelines are unavailable. Strong signals are pre-catch-up chunk readability, post-catch-up deletion on all datanodes, and zero read-state-machine failures.
