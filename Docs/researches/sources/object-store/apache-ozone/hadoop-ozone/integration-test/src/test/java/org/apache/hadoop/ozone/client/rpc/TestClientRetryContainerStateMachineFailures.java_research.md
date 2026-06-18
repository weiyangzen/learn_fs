# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestClientRetryContainerStateMachineFailures.java

## Purpose
This integration test verifies that client writes can retry successfully when the container state machine encounters leader or follower write failures caused by simulated full datanode volumes. It targets RATIS factor-three writes and checks retry behavior for first-chunk, next-chunk, small, and multi-megabyte writes.

## Important APIs, types, and functions
The fixture creates a three-datanode `MiniOzoneCluster`, configures a single pipeline, disables stream buffer flush delay, shortens RATIS watch timeouts, and sets snapshot threshold to one. It uses `OzoneOutputStream`, `ObjectStore`, `ReplicationConfig.fromTypeAndFactor`, `StorageVolume.incrementUsedSpace/decrementUsedSpace`, `XceiverServerRatis`, and `RaftServer` APIs. `checkDnPipelineIfLeader(OzoneContainer, AtomicBoolean)` scans RATIS groups and marks whether a datanode is leader for a three-peer group. `generateData(int)` fills deterministic data.

## Control flow
Every test creates or primes a RATIS/THREE key to ensure a pipeline exists, identifies leader or follower datanode volumes, records each volume's available space, and increments used space to exhaust that volume. Writes are then attempted through normal object-store APIs. The leader tests either run ten concurrent small key writes, one 5 MB key write, or a second chunk write after the first chunk has flushed. Follower tests exhaust one non-leader volume either before a 1 KB write or before writing the second chunk.

All tests restore volume usage in `finally`, so the cluster should remain usable. Failures inside asynchronous writer tasks call `fail`, and a `GenericTestUtils.waitFor` loop waits until all concurrent tasks decrement an `AtomicLong` counter.

## State and persistence behavior
The persistent state under manipulation is datanode volume accounting. By artificially consuming all available bytes, the tests induce container write failures without deleting files or stopping processes. State restoration is explicit and uses the recorded `(StorageVolume, availableBytes)` pairs. Success is mostly defined by the absence of `IOException` from create/write/flush under retry; this validates that client-side retry can allocate or continue correctly after state-machine write failure.

## Dependencies and integration points
The file integrates Ozone client writes, SCM pipeline limits, container volume usage, datanode `OzoneContainer`, RATIS server leadership, and client retry. It depends on heartbeat and close-container timing configuration to keep the test focused on write retry rather than node death.

## Risks and test signals
The concurrent test uses `CompletableFuture.runAsync` without collecting futures, so assertion failures inside workers rely on JUnit `fail` being thrown in asynchronous threads and the counter reaching zero. The use of direct volume-space mutation is effective but must always be balanced in `finally`. Strong signals are successful flush completion under leader/follower volume-full conditions and bounded wait completion for the parallel writers.
