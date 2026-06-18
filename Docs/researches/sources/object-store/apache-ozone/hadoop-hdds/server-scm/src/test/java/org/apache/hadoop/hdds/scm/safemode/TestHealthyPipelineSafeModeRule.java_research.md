# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestHealthyPipelineSafeModeRule.java

## Purpose
`TestHealthyPipelineSafeModeRule` validates the safe-mode exit rule requiring enough healthy Ratis/THREE pipelines. It covers no-pipeline behavior, pipeline report events, mixed replication factors, dynamic threshold growth, and unhealthy datanode rejection.

## Important APIs, Types, and Functions
- `HealthyPipelineSafeModeRule.validate`, `getHealthyPipelineThresholdCount`, and `getCurrentHealthyPipelineCount` are key APIs.
- The tests build `PipelineManagerImpl`, `MockRatisPipelineProvider`, `MockNodeManager`, `SCMSafeModeManager`, `SCMMetadataStoreImpl`, and `EventQueue`.
- Config keys include `HDDS_SCM_SAFEMODE_PIPELINE_CREATION`, `HDDS_SCM_SAFEMODE_HEALTHY_PIPELINE_THRESHOLD_PCT`, and `HDDS_SCM_SAFEMODE_MIN_DATANODE`.
- `firePipelineEvent` sends `SCMEvents.OPEN_PIPELINE`.

## Control Flow
Each test creates an SCM-like manager stack, creates pipelines before safe mode starts, opens them, marks them healthy, starts `SCMSafeModeManager`, then inspects the registered rule from `SafeModeRuleFactory`. Pipeline events are fired to advance rule state. The dynamic threshold test opens additional pipelines after initial validation, marks their nodes dead, verifies validation drops, then restores health and re-fires events.

## State and Persistence Behavior
Pipeline metadata is persisted in a temporary SCM metadata store. Rule state tracks reported/healthy pipeline IDs and thresholds. Node health state in `MockNodeManager` is mutated to simulate dead and recovered datanodes.

## Dependencies and Integration Points
The rule integrates pipeline manager state, open-pipeline events, node manager health, safe-mode manager lifecycle, and `SafeModeRuleFactory` global registration.

## Risks and Edge Cases
Covered edges include zero pipelines immediately satisfying the rule, ignoring Ratis/ONE pipelines for the Ratis/THREE threshold, requiring event reports before validation, increasing thresholds when more pipelines appear, and logging/rejecting pipelines with unhealthy or unregistered nodes. The tests manually stop metadata stores but do not always close pipeline managers.

## Test Signals
Strong signals include `GenericTestUtils.waitFor` on validation, explicit threshold-count assertions, and log capture when a pipeline is ignored due to bad datanode health.
