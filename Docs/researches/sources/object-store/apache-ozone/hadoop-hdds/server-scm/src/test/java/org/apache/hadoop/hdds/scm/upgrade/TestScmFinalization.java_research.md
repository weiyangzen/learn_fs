# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/upgrade/TestScmFinalization.java

Purpose: This suite verifies SCM upgrade finalization as a checkpointed state machine. It locks down checkpoint ordering, maps persisted upgrade state into checkpoints, and verifies that finalization resumes from the correct step after failure, leader change, or restart.

Important APIs and types: Key types include `FinalizationCheckpoint`, `FinalizationManager`, `FinalizationStateManager`, `SCMUpgradeFinalizer`, `SCMUpgradeFinalizationContext`, `HDDSLayoutVersionManager`, `HDDSLayoutFeature`, `SCMContext`, `PipelineManager`, `NodeManager`, `SCMStorageConfig`, `DBTransactionBuffer`, `Table<String, String>`, and `UpgradeFinalization.StatusAndMessages`.

Control flow: `testCheckpointOrder` asserts enum order because ordering determines `hasCrossed` semantics. `testUpgradeStateToCheckpointMapping` builds a state manager with mocked persistence, adds a finalizing mark, finalizes layout features until MLV equals SLV, removes the mark, and checks the checkpoint after each phase. The parameterized resume test builds mock table and version-manager state for every checkpoint, calls `finalizeUpgrade`, and uses Mockito `InOrder` to verify only not-yet-crossed operations run.

State and persistence behavior: The tests model persistent finalization state with `OzoneConsts.FINALIZING_KEY` and `OzoneConsts.LAYOUT_VERSION_KEY` in the finalization table. They also model SCM layout version persistence by verifying `SCMStorageConfig.setLayoutVersion` and `persistCurrentState`, transaction-buffer writes/removes, and in-memory `SCMContext` checkpoint updates.

Dependencies and integration points: The suite integrates upgrade finalizer logic with HA transaction buffering, Ratis-facing state managers, SCM storage VERSION files, pipeline creation freeze/resume state, and node health transitions through `forceNodesToHealthyReadOnly`.

Risks: It relies on enum order as behavior, so reordering checkpoints is a functional change. Mocked pipeline state may not cover all production pipeline recovery paths. The table mock only answers the initial finalizing-key read; later state is assumed to be held in memory.

Test signals: Signals include exact checkpoint order, `crossedCheckpoint` truth table, status `FINALIZED_MSG` versus `STARTING_MSG`, ordered writes of finalizing mark and layout version, `freezePipelineCreation`, per-feature storage persistence, forced healthy-readonly transition at max layout version, and final removal of the finalizing mark.
