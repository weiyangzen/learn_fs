# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailureOnRead.java

## Purpose
`TestContainerStateMachineFailureOnRead` verifies that a read-state-machine failure causes SCM to close the affected RATIS pipeline. The injected failure is deletion of the leader's container directory while a follower is temporarily stopped and then restarted.

## Important APIs, types, and functions
The test configures short report intervals, long stale/pipeline destroy timeouts, one datanode pipeline limit, RATIS request/watch timeouts, and suppresses noisy `GrpcLogAppender` logs. It uses `RatisReplicationConfig`, `RatisTestHelper`, `XceiverClientRatis`, `TestOzoneContainer.createContainerForTesting`, `KeyOutputStream`, `OmKeyLocationInfo`, `PipelineManager`, and `PipelineNotFoundException`.

## Control flow
The test locates the single factor-three RATIS pipeline, finds a follower, and shuts it down. Before creating the Ozone key, it verifies the pipeline is still usable by creating a test container through a raw `XceiverClientRatis`. It then writes and flushes a RATIS/THREE key and captures the container location. After finding the current leader, it deletes that leader's container directory, restarts the stopped follower, waits for cluster readiness and an additional fixed delay, and then checks the original pipeline state.

If the pipeline still exists in SCM, it must be `CLOSED`; if it was already removed, `PipelineNotFoundException` is treated as acceptable.

## State and persistence behavior
The persistent fault is a deleted leader container directory. The expected state transition is pipeline closure or removal after the restarted follower catches up and the state machine hits read failure. The key's container location ties the on-disk deletion to the active pipeline.

## Dependencies and integration points
This test spans SCM pipeline management, RATIS role detection, low-level xceiver client container creation, Ozone key writes, datanode restart, and container state-machine read paths. It intentionally separates pipeline health from later read-state failure.

## Risks and test signals
The test uses `Thread.sleep(10000)` after restart, so it may be timing-sensitive on slow environments. It prints stack traces inside role-detection lambdas instead of failing immediately. The primary signal is that the damaged pipeline is no longer open: it is either `CLOSED` or absent.
