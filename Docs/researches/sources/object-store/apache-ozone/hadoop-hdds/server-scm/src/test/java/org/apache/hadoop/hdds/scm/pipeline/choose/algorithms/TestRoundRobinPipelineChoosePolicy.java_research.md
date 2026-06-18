# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestRoundRobinPipelineChoosePolicy.java

## Purpose
`TestRoundRobinPipelineChoosePolicy` validates deterministic round-robin selection across stable and changing pipeline availability lists. It protects the policy's moving index behavior when available pipelines are added or removed.

## Important APIs, Types, and Functions
- `RoundRobinPipelineChoosePolicy.init(NodeManager)` and `choosePipeline` are under test.
- `MockPipeline.createPipeline` and `MockRatisPipelineProvider.markPipelineHealthy` produce four healthy pipelines.
- `verifySelectedCountMap` checks exact per-pipeline selection counts.

## Control Flow
Setup creates four datanodes and four pipelines, each containing three datanodes. The first test calls `choosePipeline` 100 times with all pipelines and expects exact modulo ordering and equal counts. The second test mutates the available-pipeline list from one pipeline to four, then removes one, checking the expected offset and distribution after each phase.

## State and Persistence Behavior
The policy maintains in-memory selection position across calls and across different input lists. No persistent SCM state is touched.

## Dependencies and Integration Points
The test integrates with `PipelineChoosePolicy` interface expectations and mock pipeline health marking used by production policies.

## Risks and Edge Cases
The key risk is incorrect index handling when the candidate list changes. This test covers growing and shrinking lists, but not empty lists or concurrent access.

## Test Signals
Exact expected pipeline identity for every call makes this a strong behavioral lock for deterministic round-robin semantics.
