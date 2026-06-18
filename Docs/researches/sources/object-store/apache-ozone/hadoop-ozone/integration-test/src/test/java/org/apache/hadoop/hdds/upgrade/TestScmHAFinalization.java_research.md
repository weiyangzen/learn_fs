# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/upgrade/TestScmHAFinalization.java

Purpose: SCM HA-specific upgrade finalization tests. It validates finalization survival across leader loss, full SCM restart, inactive SCM snapshot catch-up, and mid-finalization checkpoint semantics including pipeline creation freeze/unfreeze.

Important APIs/types/functions: `init`, `injectionPointsToTest`, `testFinalizationWithLeaderChange`, `testFinalizationWithRestart`, `testSnapshotFinalization`, `waitForScmsToFinalize`, `waitForScmToFinalize`, `checkMidFinalizationConditions`. It uses `UpgradeTestUtils.newPausingFinalizationExecutor`, `newTerminatingFinalizationExecutor`, `DefaultUpgradeFinalizationExecutor`, `FinalizationCheckpoint`, `FinalizationStateManagerImpl`, `MiniOzoneHAClusterImpl`, and `StorageContainerLocationProtocol`.

Control flow: `init` starts a 3-SCM HA cluster at initial layout version with configurable inactive SCM count and immediately submits `finalizeScmUpgrade` on a background executor. Parameterized tests pause/terminate finalization after pre-finalize, complete-finalization, or post-finalize checkpoints. Leader-change test stops the active leader during the pause, waits for new leadership, validates mid-state on remaining SCMs, restarts the old leader as follower, resumes finalization, waits for client and all SCMs. Restart test terminates at a checkpoint, switches new SCMs to normal finalization executor, restarts all SCMs, validates persisted mid-state, and relies on automatic resume after election. Snapshot test leaves one SCM inactive, finalizes active SCMs, advances SCM raft log by allocating/closing containers, starts inactive SCM, and checks it finalizes via snapshot install.

State and persistence: SCM HA finalization checkpoint, pipeline creation frozen flag, SCM metadata layout version, raft log/snapshot state, inactive SCM startup state, and DN finalization. Log capture observes snapshot receipt.

Dependencies and integration points: SCM HA Ratis, SCM client failover, upgrade finalization executors, latches/futures for controlled concurrency, `TestHddsUpgradeUtils`, and mini-cluster SCM lifecycle methods.

Risks: restart test is marked flaky. Client futures may complete after IOException from interrupted leader, which is expected. Mid-finalization assertions account for leader-applied raft entries while followers may lag, so they use "at least one" and filtered all-match checks rather than all-SCM equality.

Test signals: finalization checkpoint crossing, pipeline creation freeze at `FINALIZATION_STARTED`, unfreeze at later checkpoints, leadership change, all SCMs reaching `FINALIZATION_COMPLETE`, post-upgrade SCM/DN assertions, and log evidence for snapshot-based metadata layout catch-up.
