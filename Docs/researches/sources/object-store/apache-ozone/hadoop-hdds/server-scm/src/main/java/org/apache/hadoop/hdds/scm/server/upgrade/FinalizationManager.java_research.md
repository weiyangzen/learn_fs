# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationManager.java

Purpose: This interface defines the SCM service API for upgrade finalization. It starts finalization, reports progress, exposes checkpoint state, builds the upgrade context after managers are available, reinitializes state after snapshot install, and reacts when an SCM becomes leader.

Important APIs and types: Methods include `finalizeUpgrade`, `queryUpgradeFinalizationProgress`, `getUpgradeFinalizer`, `crossedCheckpoint`, `getCheckpoint`, `buildUpgradeContext`, `reinitialize`, and `onLeaderReady`. Static helpers `shouldCreateNewPipelines` and `shouldTellDatanodesToFinalize` encode checkpoint-dependent behavior.

Control flow: `StorageContainerManager` constructs the implementation during system manager initialization, builds the finalization context after node and pipeline managers are available, and places the current checkpoint into `SCMContext`. Protocol code can then call `finalizeUpgrade` or query progress. Leader readiness may trigger background resume if finalization was interrupted.

State and persistence behavior: The interface itself owns no state. Implementations persist finalization marks and layout versions through an SCM metadata table and the storage VERSION file. The static helpers are pure functions over checkpoints.

Dependencies and integration points: It links upgrade finalization to `NodeManager`, `PipelineManager`, `SCMContext`, `HDDSLayoutVersionManager`, `Table<String,String>`, and `BasicUpgradeFinalizer`. Other SCM components read the checkpoint to decide whether to create pipelines or tell datanodes to finalize.

Risks: Callers must invoke `buildUpgradeContext` before `finalizeUpgrade`; otherwise the implementation rejects finalization. The static helper semantics are subtle: pipeline creation is allowed before finalization starts or after MLV reaches SLV, but frozen in between.

Test signals: Tests should cover checkpoint helper truth tables, finalize/query delegation, reinitialize after snapshot install, context-build preconditions, and leader-ready resume behavior.
