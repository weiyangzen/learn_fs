# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/scm/pipeline/MockPipeline.java

## Purpose
Provides factory helpers for constructing test `Pipeline` instances with standalone, Ratis, and EC replication configurations.

## Important APIs, types, and functions
- Public helpers include `createSingleNodePipeline`, overloaded `createPipeline`, `createRatisPipeline`, and overloaded `createEcPipeline`.
- Uses `Pipeline.Builder`, `PipelineID`, `DatanodeDetails`, `MockDatanodeDetails`, `DatanodeID`, `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `ECReplicationConfig`.
- Builds replica-index maps for EC pipelines and node lists for replicated pipelines.

## Control flow
Factory methods allocate or accept datanodes, choose replication config, build the datanode list and optional replica-index map, assign a random pipeline ID, set pipeline state, and return a fully constructed `Pipeline`.

## State and persistence behavior
The helper creates in-memory test objects only. No real SCM pipeline state is persisted.

## Dependencies and integration points
Many tests use these helpers to create valid pipeline objects without standing up SCM or datanodes.

## Risks and test signals
Because it is test infrastructure, stale defaults can hide production contract changes. EC replica-index generation and node-count assumptions are the main maintenance risks.
