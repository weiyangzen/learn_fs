# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/safemode/TestSCMSafeModeManager.java

## Purpose
`TestSCMSafeModeManager` is the main integration test suite for SCM safe mode. It verifies safe-mode entry/exit, container thresholds for Ratis and EC, datanode prechecks, pipeline rules, state-machine readiness, invalid threshold configuration, safe-mode disabling, pipeline creation gating, metrics, rule status text, and periodic logging shutdown.

## Important APIs, Types, and Functions
- `SCMSafeModeManager.start`, `getInSafeMode`, `forceExitSafeMode`, `getPreCheckComplete`, `validateSafeModeExitRules`, `getRuleStatus`, and `getSafeModeMetrics` are central.
- Rule classes retrieved through `SafeModeRuleFactory` include `RatisContainerSafeModeRule`, `ECContainerSafeModeRule`, `HealthyPipelineSafeModeRule`, `OneReplicaPipelineSafeModeRule`, and `StateMachineReadyRule`.
- Helpers `testContainerThreshold`, `testECContainerThreshold`, `firePipelineEvent`, `checkHealthy`, and `checkOpen` simulate SCM events.
- The fixture uses `SCMMetadataStoreImpl`, `PipelineManagerImpl`, `MockNodeManager`, `MockRatisPipelineProvider`, `ContainerManagerImpl`, `EventQueue`, and `SCMContext`.

## Control Flow
Setup creates common config with safe-mode pipeline creation disabled and a temporary metadata store. Tests build container lists, set lifecycle state/key counts, configure mocked or real container managers, start the safe-mode manager, fire node-registration/container-registration/pipeline-report events, and wait for metrics or state transitions. Parameterized tests vary container counts, datanode counts, pipeline counts, threshold percentages, and EC data/parity combinations.

## State and Persistence Behavior
Some tests use mocked container managers with in-memory lists; EC tests persist containers into the metadata table and use `ContainerManagerImpl`. Pipeline tests persist pipeline records through `PipelineManagerImpl`. Safe-mode manager state includes current safe-mode flag, precheck completion, validated rules, metrics gauges, periodic logger task, and thresholds derived from config and current SCM state.

## Dependencies and Integration Points
This suite exercises integration among SCM event queue, node manager, pipeline manager, container manager, Ratis HA stubs, SCM context/state machine readiness, metrics, and `SafeModeRuleFactory`. It also checks server-facing status text used in logs and rule status maps.

## Risks and Edge Cases
Covered risks include zero containers, empty and non-empty closed containers, open containers excluded from threshold, empty closed containers excluded, EC requiring data-block-number reports, invalid threshold percentages outside [0,1], safe mode disabled by config, no datanode requirement, precheck gating before pipeline creation, force-exit and normal-exit periodic logging cleanup, and leader state-machine readiness. The tests are timing-sensitive due to event processing and periodic logging waits.

## Test Signals
The strongest signals are end-to-end safe-mode exit waits, exact metrics threshold/current values, rule status substring checks, and verification that final logs show `OUT_OF_SAFE_MODE` and stopped periodic logging. Parameterized pipeline threshold tests protect interactions between healthy-pipeline and one-replica-pipeline rules.
