# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryTimeout.java

## Purpose
`TestClientRetryTimeout` is a timing-focused integration test. It verifies that write and watch operations fail or recover within acceptable bounds when pipelines, followers, leaders, or all datanodes are unavailable. The class documents expected timeout budgets for newer retry configuration and guards against regressions to multi-minute or multi-ten-minute hangs.

## Important APIs, types, and functions
The setup creates a seven-datanode `MiniOzoneCluster` with small chunk/flush/block sizes, stream buffer flush delay disabled, fast leader election, high stale-node interval, and expanded pipeline limits. Tests unwrap `OzoneOutputStream` into `KeyOutputStream`, `RatisBlockOutputStream`, `XceiverClientRatis`, and `Pipeline`. Datanode role checks use `RatisTestHelper.isRatisFollower` and `isRatisLeader`. Helper methods are `getKeyName()`, `createKey(...)`, and `generateData(int)`.

## Control flow
The ordered tests progressively damage the cluster. `testWriteToDeadPipelineFailsFast` establishes a pipeline, shuts down all nodes in that pipeline, writes more data, measures write/flush/close time, and restarts the nodes. `testWatchForCommitWithDeadFollowersFailsFast` shuts down one follower so majority write can succeed but all-committed watch can fail or fall back. `testWriteWithLeaderFailureFailsFast` kills the current leader mid-stream. `testEndToEndWriteWithAllDatanodesDownFailsFast` shuts down every datanode, attempts another write, and measures total Ozone-level retry time.

Each test catches `IOException` as an expected outcome and treats successful recovery as acceptable if it completes within the same budget. Durations are measured with `System.nanoTime()` and asserted with AssertJ against `MAX_SINGLE_CYCLE_DURATION`, `MAX_WATCH_DURATION`, or `MAX_TOTAL_WRITE_DURATION`.

## State and persistence behavior
The test manipulates process liveness rather than on-disk data. Initial writes establish block streams and pipelines; subsequent writes test retry state after shutdowns. Datanodes are restarted between ordered tests, and the cluster waits for readiness after restarts.

## Dependencies and integration points
This file integrates client retry policy, RATIS leader/follower behavior, pipeline allocation, datanode lifecycle control, and MiniOzoneCluster readiness. The comments explicitly connect expected durations to RPC write timeout, watch timeout, exponential backoff, and Ozone max retries.

## Risks and test signals
These tests are inherently long-running: acceptable bounds are 2, 4, and 10 minutes. They are also sensitive to hardware and CI load. The important signal is not exact exception type, but elapsed time remaining below the documented thresholds. Ordered execution matters because cluster state is reused and repaired across tests.
