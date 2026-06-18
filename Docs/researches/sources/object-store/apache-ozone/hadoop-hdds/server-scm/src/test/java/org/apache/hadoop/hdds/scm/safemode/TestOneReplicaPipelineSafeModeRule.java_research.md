# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestOneReplicaPipelineSafeModeRule.java

## Purpose
`TestOneReplicaPipelineSafeModeRule` verifies the safe-mode rule requiring enough Ratis/THREE pipelines to have at least one datanode report. It covers pure factor-THREE pipelines, mixed factor-ONE and factor-THREE pipelines, and direct validation without report processing.

## Important APIs, Types, and Functions
- `OneReplicaPipelineSafeModeRule.validate`, `getReportedPipelineIDSet`, `getCurrentReportedPipelineCount`, and `setValidateBasedOnReportProcessing` are central.
- `PipelineManagerImpl`, `MockRatisPipelineProvider`, `MockNodeManager`, `SCMSafeModeManager`, and `SafeModeRuleFactory` provide the SCM context.
- `firePipelineEvent` builds `PipelineReportsProto` per datanode and fires `SCMEvents.PIPELINE_REPORT`.

## Control Flow
Setup creates requested numbers of Ratis/THREE and Ratis/ONE pipelines before starting safe mode. Tests fire reports for all but one factor-THREE pipeline, verify the rule remains false and logs reported counts, then fire the final report and wait for validation. Mixed tests prove factor-ONE reports do not satisfy the factor-THREE rule. The non-report-processing test uses mocks to make a pipeline first return an empty node set and then a non-empty node set.

## State and Persistence Behavior
Pipelines are stored in a temporary SCM metadata store through `PipelineManagerImpl`. Rule state tracks reported pipeline IDs. The event helper derives datanode-to-pipeline membership from `MockNodeManager` maps.

## Dependencies and Integration Points
The rule integrates with datanode heartbeat pipeline reports, pipeline manager queries by replication config and state, node-to-pipeline maps, and safe-mode manager metrics/logging.

## Risks and Edge Cases
Key edge cases include ignoring factor-ONE pipelines, threshold ceil behavior for 90 percent of seven pipelines, pipeline-not-found during report construction, and direct manager-state validation when report processing is disabled.

## Test Signals
Log-captured reported counts and final `waitFor(rule.validate())` provide strong evidence that only qualifying factor-THREE pipeline reports advance the rule.
