# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/SCMUpgradeFinalizer.java

Purpose: `SCMUpgradeFinalizer` provides SCM-specific actions for the generic Ozone `BasicUpgradeFinalizer`. The leader drives disruptive upgrade finalization while followers apply replicated state manager operations.

Important APIs and types: It extends `BasicUpgradeFinalizer<SCMUpgradeFinalizationContext, HDDSLayoutVersionManager>`. Overridden methods are `preFinalizeUpgrade`, `finalizeLayoutFeature`, and `postFinalizeUpgrade`. Helper methods include `replicatedFinalizationSteps`, `closePipelinesBeforeFinalization`, and `createPipelinesAfterFinalization`.

Control flow: Pre-finalization ensures the finalizing mark exists, publishes `FINALIZATION_STARTED`, and closes existing non-closed pipelines if MLV has not yet reached SLV. Pipeline creation must already be frozen by checkpoint publication. Each layout feature is finalized by calling `FinalizationStateManager.finalizeLayoutFeature`, which runs replicated finalization steps and updates DB/VERSION state. Post-finalization logs that MLV equals SLV, waits for at least one open RATIS/THREE pipeline if finalization is not complete, and removes the finalizing mark.

State and persistence behavior: The finalizer does not write DB state directly; it delegates replicated mutations to the state manager. `replicatedFinalizationSteps` runs layout-feature upgrade actions and writes the VERSION-file layout version through the superclass. Pipeline close and post-finalization wait mutate runtime cluster state, not RocksDB directly.

Dependencies and integration points: It depends on `PipelineManager`, `ReplicationConfig`, SCM leader term checks in `SCMContext`, `HDDSLayoutFeature.scmAction`, and the generic upgrade executor. It is coordinated with `FinalizationStateManagerImpl.publishCheckpoint`, which freezes/resumes pipeline creation and changes node states.

Risks: `closePipelinesBeforeFinalization` throws if pipeline creation was not frozen first, enforcing checkpoint ordering. `createPipelinesAfterFinalization` loops until an open RATIS/THREE pipeline exists and checks leader term to stop if leadership is lost; insufficient datanodes or disabled pipeline creation can delay completion. Interrupted sleep resets the interrupt flag but continues the loop. Any layout action failure is wrapped as `LAYOUT_FEATURE_FINALIZATION_FAILED`.

Test signals: Tests should cover finalizing mark creation idempotence, pipeline freeze precondition, closing all non-closed pipelines, layout feature delegation and exception wrapping, post-finalization wait behavior, leader-loss exit through `NotLeaderException`, and finalizing mark removal only after MLV reaches SLV and a pipeline is available.
