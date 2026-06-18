# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestBasicUpgradeFinalizer.java

Purpose: Tests `BasicUpgradeFinalizer` phase ordering, already-finalized short-circuiting, and concurrent finalization status behavior.

Important APIs/types/functions: `BasicUpgradeFinalizer`, `UpgradeFinalizer`, `UpgradeFinalization.StatusAndMessages`, `finalize`, `reportStatus`, `getStatus`, `isFinalizationDone`, `preFinalizeUpgrade`, `finalizeLayoutFeature`, `postFinalizeUpgrade`, and `UpgradeTestUtils.newPausingFinalizationExecutor`.

Control flow: One test spies a simple finalizer and verifies pre-finalize, feature finalization, and post-finalize occur in order and persist storage layout versions. Another confirms no phases run when metadata is already final. The concurrency test pauses finalization at an injected point, checks simultaneous finalize/status calls report in-progress, resumes, and verifies subsequent status calls report done.

State and persistence behavior: Mock layout version managers hold version state. Mock `Storage` receives layout version and `persistCurrentState` calls during feature finalization.

Dependencies and integration points: Uses injected executor, mock layout features from `TestUpgradeFinalizerActions`, Java futures/latches/executors, Mockito in-order verification, and SLF4J.

Risks: Executors are created per submitted task and not explicitly shut down, which can leave transient threads. Concurrency behavior depends on latch placement.

Test signals: High-value signal for upgrade finalizer state machine, phase ordering, finalization idempotence, and client-visible concurrent statuses.
