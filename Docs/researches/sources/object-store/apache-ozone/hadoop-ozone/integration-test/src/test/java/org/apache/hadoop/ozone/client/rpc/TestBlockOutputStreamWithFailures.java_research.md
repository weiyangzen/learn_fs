# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestBlockOutputStreamWithFailures.java

## Purpose
`TestBlockOutputStreamWithFailures` extends the baseline stream checks into failure handling. It verifies that `KeyOutputStream` and `RatisBlockOutputStream` recover from container closure, dead datanodes, single-node RATIS failures, and preallocated block failures while preserving committed data and cleaning up retry state.

## Important APIs, types, and functions
The file imports constants and helpers from `TestBlockOutputStream`, so it uses the same chunk/flush/block geometry and client configuration matrix. It directly inspects `KeyOutputStream`, `RatisBlockOutputStream`, `XceiverClientRatis`, `Pipeline`, and `commitInfoMap`. Failure classification uses `HddsClientUtils.checkForException` and accepts `ContainerNotOpenException`, `RaftRetryFailureException`, or `GroupMismatchException` depending on race timing. `stopAndRemove(DatanodeDetails)` removes a datanode service from the cluster list and stops it.

## Control flow
The class starts a 25-datanode cluster to leave enough replacement capacity. `testContainerClose` runs several private scenarios against each client configuration: close-container during watch-for-commit, factor-one RATIS close handling, writes larger than max flush size, and exception during close. Separate parameterized tests cover one datanode failure, two datanode failure, single-node pipeline failure, and failure with preallocated blocks.

Most scenarios first write `MAX_FLUSH_SIZE + CHUNK_SIZE`, force a flush, capture the `RatisBlockOutputStream`, then inject a failure by closing the container through `TestHelper.waitForContainerClose` or stopping datanodes. The next write/flush forces the stream to discard failed chunks or blocks, allocate a new block, and retry the data. Final assertions validate stream-entry count transitions, retry count reset, exception type, buffer drain, and complete readback of either one copy or two concatenated copies of the data.

## State and persistence behavior
The tests focus on state handoff after failure. They confirm `retryCount` resets to zero after exception handling, `commitIndex2flushedDataMap` is drained, buffered data is zero after close, location/stream entries are discarded where appropriate, and `commitInfoMap` remains stable when no datanode actually fails. Persistence is validated by reading object data after recovery, including cases where the same data is intentionally written before and after failure.

## Dependencies and integration points
Integration spans client retry logic, SCM block allocation, RATIS commit tracking, container close handling, datanode lifecycle methods, and the MiniOzoneCluster service list. Factor-one and factor-three paths are both covered. Preallocation uses `createKey(..., 3 * BLOCK_SIZE, ReplicationFactor.ONE)` to ensure unused entries exist before the failure.

## Risks and test signals
The class is marked `@Flaky("HDDS-11849")`; accepted exception classes show that SCM pipeline destruction, container closure, and RATIS retry exhaustion are timing dependent. The important regression signals are no data loss after reallocation, no leaked buffered bytes or stream entries, proper exception unwrapping, and retry-count reset. Cluster mutation through `stopAndRemove` is powerful but risky because it changes MiniOzoneCluster internals directly.
