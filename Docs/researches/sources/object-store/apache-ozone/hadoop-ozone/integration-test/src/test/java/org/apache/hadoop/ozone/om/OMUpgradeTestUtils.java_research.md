# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/OMUpgradeTestUtils.java

## Purpose
`OMUpgradeTestUtils` provides small polling helpers for OM upgrade and prepare-state integration tests. It verifies that all OMs enter prepare at the expected transaction index and waits for upgrade finalization to complete.

## Important APIs, Types, and Functions
- `assertClusterPrepared(long preparedIndex, List<OzoneManager> ozoneManagers)` loops over OMs and uses `LambdaTestUtils.await` until each running OM reports `PREPARE_COMPLETED` at the expected index.
- `waitForFinalization(OzoneManagerProtocol omClient)` polls `queryUpgradeFinalizationProgress("finalize-test", false, false)` until status is `FINALIZATION_DONE`.

## Control Flow
The prepare helper skips progress until the OM is running, then checks prepare status. If an OM is prepared at the wrong index, it throws immediately to break out rather than waiting until timeout. The finalization helper catches `IOException`, fails the test with the message, and keeps polling otherwise.

## State and Persistence Behavior
The utilities inspect persisted/replicated OM prepare state and upgrade finalization state through live OM objects or protocol calls, but they do not mutate state themselves.

## Dependencies and Integration Points
Dependencies include `OzoneManagerPrepareState.State`, `OzoneManagerProtocol`, `UpgradeFinalization.StatusAndMessages`, `GenericTestUtils.waitFor`, and `LambdaTestUtils.await`.

## Risks and Test Signals
Risks are timeout sensitivity and hard-coded client ID `"finalize-test"`. Test signals are all OMs prepared at one exact index and finalization status reaching `FINALIZATION_DONE`.
