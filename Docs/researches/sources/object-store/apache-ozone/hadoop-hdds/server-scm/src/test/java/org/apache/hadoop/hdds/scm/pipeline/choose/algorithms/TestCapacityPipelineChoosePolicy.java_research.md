# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/choose/algorithms/TestCapacityPipelineChoosePolicy.java

## Purpose
`TestCapacityPipelineChoosePolicy` validates that capacity-aware pipeline selection favors pipelines whose datanodes have lower used capacity. It constructs a controlled four-datanode scenario where each possible three-node pipeline has a predictable relative score.

## Important APIs, Types, and Functions
- `CapacityPipelineChoosePolicy.init(NodeManager)` and `choosePipeline` are under test.
- `NodeManager.getNodeStat` returns synthetic `SCMNodeMetric` values.
- `MockPipeline.createPipeline` and `MockRatisPipelineProvider.markPipelineHealthy` prepare selectable pipelines.

## Control Flow
The test mocks four datanode metrics with increasing used values. It builds four pipelines, each missing a different datanode. It calls `choosePipeline` 1,000 times and counts selections, then asserts the expected ranking from least-used aggregate membership to most-used aggregate membership.

## State and Persistence Behavior
Selection state is in-memory and probabilistic/weighted. No SCM persistence is involved.

## Dependencies and Integration Points
This test connects pipeline choice to node capacity metrics exposed by `NodeManager`, and to healthy pipeline marking expected by choose policies.

## Risks and Edge Cases
The test validates relative ordering over many runs instead of exact counts, making it robust to weighted randomness while still catching inverted ranking. It does not test null metrics, empty lists, or unhealthy pipelines.

## Test Signals
The ordered selection-count assertions protect the intended policy behavior: the pipeline containing lower-used datanodes should be chosen more frequently.
