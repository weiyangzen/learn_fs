# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMUpgradeFinalization.java

Purpose: This HA upgrade test verifies that OM upgrade finalization can complete while one OM is down and that the restarted OM catches up to the finalized metadata layout version. It also checks audit logging for prepare, cancel, and finalize operations.

Important APIs and types: The file uses `MiniOzoneHAClusterImpl`, `OzoneManagerProtocol`, `OMUpgradeTestUtils.assertClusterPrepared`, `waitForFinalization`, `OMStorage.TESTING_INIT_LAYOUT_VERSION_KEY`, `OMLayoutFeature.INITIAL_VERSION`, `OMLayoutVersionManager.maxLayoutVersion`, `OzoneManagerStateMachine`, Ratis `LifeCycle`, `LAYOUT_VERSION_KEY`, and audit helpers for `OMAction.UPGRADE_PREPARE`, `UPGRADE_CANCEL`, and `UPGRADE_FINALIZE`.

Control flow: The test builds a three-OM HA cluster initialized at the initial layout version, stops one OM, prepares the remaining active OMs to compact/purge logs, verifies prepare state and audit success, cancels prepare, finalizes upgrade through the OM client, waits for finalization, restarts the downed OM, waits through any state-machine pause/resume window, and finally checks the restarted OM's layout version and metadata table value.

State and persistence behavior: Persistent state includes OM upgrade metadata, the meta table's `LAYOUT_VERSION_KEY`, Ratis logs/snapshots affected by prepare/finalize, and audit log records. The downed OM starts with older local state and must replay or install finalized state until its version manager and DB metadata match `maxLayoutVersion()`.

Dependencies and integration points: It integrates HA OM lifecycle, upgrade prepare/cancel/finalize RPCs, Ratis state-machine lifecycle, audit logging, metadata layout version management, and cluster restart with catch-up.

Risks: The test is timing-sensitive around state-machine pause states and uses a fallback assertion if pausing is not observed before timeout. It validates one downed-OM scenario but not multiple failures or partial finalization errors.

Test signals: Signals include stopped OM state, successful cluster prepare index on running OMs, audit log success records for prepare/cancel/finalize, finalization completion, state machine leaving paused states after restart, version manager metadata layout equal to `maxLayoutVersion()`, and a non-null DB `LAYOUT_VERSION_KEY` matching the same version.
