# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/pipeline/TestRatisPipelineProvider.java

## Purpose
`TestRatisPipelineProvider` validates Ratis pipeline allocation behavior under node health, pipeline-per-node limits, explicit node lists, exclusions, placement policy selection, and space requirements. It checks both successful pipeline construction and error messages when no suitable nodes are available.

## Important APIs, Types, and Functions
- `RatisPipelineProvider.create(...)`, `createForRead(...)`, and explicit-node overloads are the main APIs.
- `MockRatisPipelineProvider`, `MockNodeManager`, `PipelineStateManagerImpl`, `SCMHAManagerStub`, and the SCM pipeline table provide an SCM-like test environment.
- Config keys include `OZONE_DATANODE_PIPELINE_LIMIT`, `OZONE_SCM_PIPELINE_PLACEMENT_IMPL_KEY`, `OZONE_SCM_CONTAINER_SIZE`, and `OZONE_DATANODE_RATIS_VOLUME_FREE_SPACE_MIN`.
- Helpers `assertPipelineProperties`, `createPipelineAndAssertions`, `addPipeline`, and `createContainerReplicas` define reusable expectations.

## Control Flow
Initialization creates a real DB store, a mock node manager with configurable pipeline quota, a state manager, and a mock Ratis provider. Basic tests create factor ONE and THREE pipelines, add them to state and node managers, and assert properties and limited overlap. Other tests saturate selected datanodes with open or closed pipelines, configure placement policy and limits, or inflate required space so pipeline creation must fail.

## State and Persistence Behavior
Pipelines are added to both `PipelineStateManager` and `MockNodeManager` to mirror SCM state and node-to-pipeline engagement. The provider itself produces allocated pipelines unless explicit nodes are supplied, in which case pipelines are open. Per-datanode engagement and state of existing open/closed pipelines directly affect future placement.

## Dependencies and Integration Points
The provider integrates with node status filtering, pipeline placement policy, replication configs, container replica read pipelines, and SCM configuration. Rack-scatter placement is tested by setting the placement implementation class. Space checks depend on container size and Ratis metadata free-space config.

## Risks and Edge Cases
Covered risks include reuse of identical datanode sets, excluded node enforcement, default and explicit per-DN pipeline limits, insufficient data or metadata space, and behavior when only closed-pipeline members remain available. The tests also protect specific exception text, making them sensitive to message changes.

## Test Signals
High-value signals are no full overlap when alternatives exist, exact exception messages for limit exhaustion, and confirmed fallback to closed-pipeline members when open members are saturated. Parameterized limit cases guard both one- and two-pipeline-per-node quota behavior.
