# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOmTableInsightTaskStaleCounterAfterReinit.java

Purpose: End-to-end regression test for a stale in-memory counter bug after `ReconTaskControllerImpl.reInitializeTasks`. It proves the registered `OmTableInsightTask` must reload its maps after staged DB replacement so later delta events use the rebuilt base count.

Important APIs and control flow: Setup creates a real Recon OM metadata manager, Recon SQL DB, `ReconGlobalStatsManager`, and controller with status updater mocks. The test writes initial volumes, spies an `OmTableInsightTask` whose `getStagedTask` returns a fresh task, registers it, performs initial `reprocess`, adds more volumes, calls `reInitializeTasks`, then routes a PUT delta through the task returned by `getRegisteredTasks`.

State and persistence behavior: The key persisted state is `volumeTableCount` in Recon global stats. Phase 1 writes count 5; reinitialization over the staged task writes count 8; subsequent delta PUT must write 9. Without calling `init` on the live/registered task after the staged DB swap, the old task would retain base 5 and write 6.

Dependencies and integration points: Integrates `ReconTaskControllerImpl`, `ReconOmTask.getStagedTask`, staged Recon DB provider behavior, `ReconGlobalStatsManager.reinitialize`, `OmTableInsightTask.init`, `ReconTaskStatusUpdater`, and OM volume table writes.

Risks and test signals: Very strong signal for reinit correctness across object identity and DB replacement boundaries. It depends on production controller behavior and real SQL-backed global stats, making it more valuable than a narrow mock test but also more setup-sensitive.
