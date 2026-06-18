# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateManagerImpl.java

## Purpose
`TestPipelineStateManagerImpl` verifies the persisted and in-memory behavior of `PipelineStateManagerImpl`: pipeline admission, duplicate rejection, query indexes by replication config/state, state transitions, container membership, and removal constraints. It is an integration-style unit test around a real SCM metadata table backed by a temporary `DBStore`, with mocked SCM HA and node-management collaborators.

## Important APIs, Types, and Functions
- `PipelineStateManagerImpl.newBuilder()` wires `SCMDBDefinition.PIPELINES`, a Ratis server, `NodeManager`, and the SCM DB transaction buffer.
- `PipelineStateManager` methods under test include `addPipeline`, `getPipeline`, `getPipelines`, `updatePipelineState`, `addContainerToPipeline`, `removeContainerFromPipeline`, `getContainers`, and `removePipeline`.
- Helper methods `createDummyPipeline`, `openPipeline`, `finalizePipeline`, `deactivatePipeline`, and `removePipeline` centralize construction and state transitions.
- `Pipeline`, `PipelineID`, `ContainerID`, `ReplicationConfig`, `RatisReplicationConfig`, and `HddsProtos.Pipeline` are the main data objects crossing protobuf and domain boundaries.

## Control Flow
Setup creates an isolated SCM configuration and RocksDB store, then builds a fresh state manager for each test. Tests add pipelines as protobuf messages, optionally mutate them through `updatePipelineState`, and then assert query or mutation behavior against the manager. The broadest tests create matrices of RATIS and STAND_ALONE pipelines for every replication factor and every pipeline state, then check that indexed queries return exact counts and matching type/state fields. Cleanup paths finalize and remove generated pipelines.

## State and Persistence Behavior
The test intentionally uses the real pipeline table from `SCMDBDefinition`, so pipeline metadata is persisted through the test DB store and transaction buffer path rather than only held in memory. It confirms duplicate pipeline IDs are rejected, closed pipelines can be removed only after legal state/container conditions, and container membership is associated with the pipeline in the manager state. It also checks idempotent state transitions for already-open and already-closed pipelines.

## Dependencies and Integration Points
Dependencies include `SCMHAManagerStub`, `MockNodeManager`, `DBStoreBuilder`, `SCMTestUtils`, and Ozone replication config/protobuf classes. The integration point of highest importance is the conversion between `Pipeline` domain objects and `HddsProtos.Pipeline` via `getProtobufMessage(ClientVersion.CURRENT_VERSION)`.

## Risks and Edge Cases
The tests cover mismatched replication factor versus node count, duplicate IDs, removed pipeline access, container addition after removal, attempts to remove non-closed/non-empty pipelines, and idempotent finalize/open transitions. A risk not deeply covered is restart recovery: the test uses persistent tables but does not rebuild a second manager from the same DB after writes.

## Test Signals
Strong signals are exact query counts across type/factor/state combinations, assertion of exception messages for invalid operations, and explicit verification that container sets track additions/removals. The tests are sensitive to future enum additions because they iterate all `ReplicationFactor` and `PipelineState` values.
