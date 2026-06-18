# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/TestReconContainerManager.java

## Purpose
Unit/integration tests for `ReconContainerManager` using the real fixture from `AbstractReconContainerManagerTest`. It verifies new container insertion, DB persistence, state transitions inferred from datanode replica reports, pipeline bookkeeping, and replica history maintenance.

## Important APIs, types, and functions
- Exercises `addNewContainer`, `checkAndAddNewContainer`, `checkAndAddNewContainerBatch`, `transitionOpenToClosing`, `updateContainerReplica`, `removeContainerReplica`, `containerExist`, `getContainers`, and `getPipelineToOpenContainer`.
- Uses HDDS `ContainerInfo`, `ContainerID`, `ContainerWithPipeline`, `ContainerReplica`, `ContainerReplicaHistory`, `Pipeline`, `ContainerChecksums`, and replica proto states.
- Verifies SCM client calls with Mockito, especially that some transitions avoid `getContainerWithPipeline`.

## Control flow
The first tests add open and closed containers and verify in-memory state plus DB existence after closing the transaction buffer. Batch-add tests feed container replica protos for IDs 200-299 and then repeat the call to prove idempotency. Transition tests cover open-to-closing from CLOSING/CLOSED replica reports, no SCM lookup for open-to-closing, failure handling that leaves open-container counts unchanged, and ignoring unhealthy/invalid/deleted replica reports for open or closing containers. Replica-history tests add and update replicas from two datanodes, then remove one. The final test ensures adding a container with an unknown pipeline first registers that pipeline.

## State and persistence behavior
Container state is tracked in the manager and written to RocksDB. Open containers update pipeline-to-open-container counts; moving out of open removes that mapping. Replica history is an in-memory map keyed by container id and datanode id, preserving first/last seen time, BCS ID, and checksum. Adding a container can also persist/register a missing pipeline.

## Dependencies and integration points
The tests cover interactions among Recon's container state machine, SCM DB transaction buffer, pipeline manager, SCM service-provider fallback, and datanode replica report processing.

## Risks and edge cases
State-machine behavior is intentionally conservative: only open and closing states advance from replica reports; unhealthy/invalid/deleted reports must not downgrade or retire live containers. Regression risk is high around count updates if transition failures occur after partial bookkeeping changes.

## Test signals
Signals include exact lifecycle states, DB table existence, open-container pipeline map contents, no unexpected SCM lookup calls, exception preservation for missing containers, replica history map size/content/timestamps/checksums, and successful handling of duplicate or missing-pipeline additions.
