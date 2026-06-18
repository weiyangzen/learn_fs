# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestHddsUpgradeUtils.java

Purpose: shared assertion/wait helpers for HDDS upgrade integration tests. It centralizes expected pre-upgrade and post-upgrade SCM/DN states, finalization polling, and SCM-visible datanode health checks.

Important APIs/types/functions: `waitForFinalizationFromClient`, `testPreUpgradeConditionsSCM`, `testPostUpgradeConditionsSCM` for list and single SCM, `testPreUpgradeConditionsDataNodes`, `testPostUpgradeConditionsDataNodes`, and `testDataNodesStateOnSCM` for list and single SCM. It uses `StorageContainerLocationProtocol`, `StorageContainerManager`, `HDDSLayoutVersionManager`, `FinalizationCheckpoint`, `PipelineManager`, `ContainerInfo`, `HddsDatanodeService`, `DatanodeStateMachine`, and `ContainerProtos.ContainerDataProto.State`.

Control flow: finalization polling repeatedly queries `queryUpgradeFinalizationProgress` until `FINALIZATION_DONE` or `ALREADY_FINALIZED`. Pre-SCM checks require initial MLV and all containers OPEN. Post-SCM checks require checkpoint crossing `FINALIZATION_COMPLETE`, MLV equal to SLV, at least one open RATIS THREE pipeline, SCM node health HEALTHY or HEALTHY_READONLY, and all containers in closed/deleting/quasi-closed states. Pre-DN checks require DN MLV 0 and open containers. Post-DN checks wait for every DN upgrade status to finish, then assert MLV equals SLV and containers are in provided closed states or default CLOSED/QUASI_CLOSED. Node-state helpers iterate all SCM-known nodes and compare health to expected/alternate states.

State and persistence: no own persistence; it observes live SCM metadata layout versions, finalization checkpoints, pipeline manager state, DN version managers, container controllers, and SCM node manager health.

Dependencies and integration points: JUnit assertions, AssertJ, `GenericTestUtils.waitFor`, `LambdaTestUtils.await`, SCM node manager, pipeline manager, and datanode upgrade status RPCs.

Risks: wait durations are fixed and broad, which can make failures slow. It assumes at least one RATIS THREE pipeline after upgrade and at least one pre-upgrade container for DN preconditions. Alternate node-state support deliberately accepts timing races, so tests using it trade precision for stability.

Test signals: this file is not itself a test class but provides core pass/fail signals for upgrade suites: layout version equality/progression, finalization checkpoint crossing, pipeline availability, container state closure, and DN health transitions.
