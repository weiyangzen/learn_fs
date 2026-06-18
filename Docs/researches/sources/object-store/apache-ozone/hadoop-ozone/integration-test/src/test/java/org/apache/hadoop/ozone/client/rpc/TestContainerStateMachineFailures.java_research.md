# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestContainerStateMachineFailures.java

## Purpose
This large integration test suite covers container state-machine failure handling for missing RATIS pipelines, datanode ID changes, corrupt containers, unhealthy metadata persistence, failed apply transactions, idempotent close/write behavior on closed containers, and client retry after follower failures.

## Important APIs, types, and functions
The shared fixture starts a ten-datanode cluster with fast reports/heartbeats, short stale/dead intervals, close-container wait duration, pipeline scrub/destroy timeouts, RATIS client/server timeouts, snapshot threshold one, and stream buffer flush delay disabled. It uses `ContainerStateMachine`, `XceiverServerRatis`, `XceiverClientManager`, `HddsDispatcher`, `ContainerDataYaml`, `KeyValueContainerData`, `CloseContainerCommand`, `RatisHelper`, `SimpleStateMachineStorage`, `FileInfo`, `ContainerTestHelper`, and `LambdaTestUtils`.

## Control flow
`testContainerStateMachineCloseOnMissingPipeline` removes RATIS groups with `notifyGroupRemove`, queues SCM close commands, and waits for containers to become `QUASI_CLOSED`. `testContainerStateMachineRestartWithDNChangePipeline` deletes a datanode's data volumes and datanode ID file, restarts it, and waits until a retry write allocates a new location. The ordered final `testContainerStateMachineFailures` deletes a container directory, expects `UNHEALTHY`, changes the RATIS storage dir before restart, and verifies the unhealthy container is not loaded into the regular set.

`testUnhealthyContainer` deletes chunks, verifies both in-memory and YAML `.container` state become `UNHEALTHY`, restarts, rereads metadata, and asserts close-container dispatch returns `CONTAINER_UNHEALTHY`. `testApplyTransactionFailure` deletes the container path before a close-container command, expects send failure, waits for the state machine to become unhealthy, verifies `takeSnapshot()` fails with `StateMachineException`, checks BCSID is unchanged, and waits for the snapshot/group directory to be removed. The idempotency tests close containers and issue duplicate or racing write-chunk commands to ensure the state machine remains healthy and snapshots advance. The retry tests delete follower chunk directories and verify data is still readable with expected OM location counts.

## State and persistence behavior
This file directly mutates storage directories, chunk paths, datanode ID files, RATIS group membership, SCM command queues, and container metadata YAML. It observes container states `QUASI_CLOSED`, `UNHEALTHY`, and `CLOSED`; snapshot file paths; block commit sequence IDs; state-machine health; key location counts; and readback bytes.

## Dependencies and integration points
The tests integrate nearly every layer involved in RATIS container writes: client stream retry, SCM node commands, datanode dispatcher, container metadata persistence, RATIS storage, state-machine snapshots, OM key lookup, and raw container protocol requests.

## Risks and test signals
This file is highly timing- and order-sensitive; one test is explicitly ordered last because changing RATIS storage location leaves pipelines dirty. There appears to be a likely typo in `testContainerStateMachineDualFailureRetry`: it writes key `ratis2` but validates `ratis1`. Important signals include state-machine health remaining true for idempotent closed-container writes, redacted failed write messages, failed snapshot after unhealthy state, YAML state persistence, and successful readback after follower chunk loss.
