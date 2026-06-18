# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestSimplePipelineProvider.java

## Purpose
`TestSimplePipelineProvider` verifies standalone pipeline creation, both with provider-selected nodes and with explicitly supplied nodes. It ensures standalone pipelines are immediately open and have node counts matching their replication factor.

## Important APIs, Types, and Functions
- `SimplePipelineProvider.create(StandaloneReplicationConfig)` and `create(config, nodes)` are the core APIs.
- The setup uses `MockNodeManager`, `PipelineStateManagerImpl`, `SCMHAManagerStub`, and the SCM pipeline table.
- `createListOfNodes` builds arbitrary datanode lists for explicit-node creation.

## Control Flow
Each test initializes an SCM-like state manager and provider. The factor test creates THREE and ONE standalone pipelines, persists them into the state manager, and asserts type, replication factor, state, and node count. The explicit-node test bypasses node selection and asserts the same properties.

## State and Persistence Behavior
For provider-selected pipelines, the test adds protobuf pipeline records to `PipelineStateManager`. The provider returns `OPEN` standalone pipelines, unlike Ratis creation paths that often start as `ALLOCATED`.

## Dependencies and Integration Points
The provider depends on `NodeManager` for selecting nodes and on `PipelineStateManager` for awareness of existing pipelines. It integrates with `StandaloneReplicationConfig` and the pipeline protobuf conversion path.

## Risks and Edge Cases
The file covers factors ONE and THREE but not invalid node counts or lack of healthy nodes. It assumes standalone pipelines should not need a later open transition.

## Test Signals
The assertions are straightforward regression signals for standalone pipeline shape and state, especially the difference that standalone pipelines are open immediately.
