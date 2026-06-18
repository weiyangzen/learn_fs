# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestWritableECContainerProvider.java

## Purpose
`TestWritableECContainerProvider` validates how `WritableECContainerProvider` chooses or creates writable EC containers and pipelines. It covers capacity limits based on healthy volumes, minimum pipeline counts, exclusion handling, stale container/pipeline cleanup, pipeline closing when no writable container remains, and excluded datanode forwarding.

## Important APIs, Types, and Functions
- `WritableECContainerProvider.getContainer(size, repConfig, owner, ExcludeList)` is the main API.
- `WritableECContainerProviderConfig` controls minimum pipelines and pipeline-per-volume factor.
- `PipelineChoosePolicy` implementations tested are `RandomPipelineChoosePolicy`, `HealthyPipelineChoosePolicy`, and `CapacityPipelineChoosePolicy`.
- `MockPipelineManager`, `MockNodeManager`, mocked `ContainerManager`, `ExcludeList`, `ECReplicationConfig`, and `ContainerInfo` are key collaborators.

## Control Flow
Parameterized tests create the provider for each choose policy. Setup creates a node topology, DB store, HA manager, mock pipeline manager, and mocked container manager whose `getMatchingContainer` creates and registers a container for a pipeline. Tests request containers repeatedly to fill expected pipeline limits, then assert later requests reuse existing containers. Other tests exclude pipelines, containers, or datanodes, simulate pipeline/container lookup failures, and verify provider decisions.

## State and Persistence Behavior
Pipeline and container state is maintained through `MockPipelineManager` and a local `Map<ContainerID, ContainerInfo>`. The provider adds containers to pipelines through the mocked container-manager answer. Tests mutate `usedBytes`, remove containers from pipelines, and assert that exhausted or inconsistent pipelines transition to `CLOSED`.

## Dependencies and Integration Points
The provider integrates with pipeline manager creation, container manager matching and lookup, node healthy-volume counts, topology-aware node manager initialization, and choose-policy selection. It also depends on SCM container size config to determine EC stripe space requirements.

## Risks and Edge Cases
Covered cases include all pipelines excluded, all containers excluded, soft-limit creation when exclusions prevent reuse, creation failure propagation, RocksDB creation failure, missing pipeline/container while reusing, open pipelines with removed containers, closed containers in excluded pipelines, and explicit excluded datanode pass-through. One notable behavior is that pipeline limits count all open pipelines, not only those surviving the current exclude filter.

## Test Signals
The suite gives broad regression coverage across three policies with the same provider contract. High-value signals are distinct-container allocation until the configured limit, reuse after limit, closure of stale pipelines, and Mockito verification that `createPipeline` receives the correct excluded nodes.
