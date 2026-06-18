# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestPipelineStateMap.java

## Purpose
`TestPipelineStateMap` validates the lightweight `PipelineStateMap` count indexes for standalone, Ratis, and EC pipelines. It ensures open and closed pipelines are counted independently by exact `ReplicationConfig`.

## Important APIs, Types, and Functions
- `PipelineStateMap.addPipeline`, `updatePipelineState`, and `getPipelineCount` are the focus.
- `MockPipeline.createPipeline`, `createRatisPipeline`, and `createEcPipeline` provide representative pipelines.
- `StandaloneReplicationConfig`, `RatisReplicationConfig`, and `ECReplicationConfig` exercise config equality and index bucketing.

## Control Flow
The test creates three groups of pipelines: standalone, Ratis, and EC. In each group it adds multiple open pipelines and marks one pipeline closed. It then asserts open and closed counts for each replication config, including a zero-count EC config that was never added.

## State and Persistence Behavior
This is in-memory state only. It validates that updates move a pipeline between state buckets without losing replication-config grouping.

## Dependencies and Integration Points
The file integrates with `MockPipeline` helpers and the production `PipelineStateMap` type. It is a focused regression test for indexing behavior used by state managers and pipeline managers.

## Risks and Edge Cases
The main edge case is exact EC replication config matching: EC(3,2) has counts while EC(6,3) returns zero. The test does not cover deletion, duplicate adds, or concurrent updates.

## Test Signals
The assertions provide a compact signal that state transitions update count indexes correctly across all supported replication families represented in SCM.
