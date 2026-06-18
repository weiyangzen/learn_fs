# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/server/upgrade/FinalizationCheckpoint.java

Purpose: This enum models SCM upgrade finalization progress as checkpoints derived from disk state. It lets SCM resume finalization after leader changes or restarts by interpreting two facts: whether the DB contains the finalizing mark and whether metadata layout version is behind software layout version.

Important APIs and types: Checkpoints are `FINALIZATION_REQUIRED`, `FINALIZATION_STARTED`, `MLV_EQUALS_SLV`, and `FINALIZATION_COMPLETE`. Each stores the expected finalizing-mark state, expected MLV-behind-SLV state, and the `UpgradeFinalization.Status` reported to clients. Methods include `isCurrent`, `needsFinalizingMark`, `needsMlvBehindSlv`, `hasCrossed`, and `getStatus`.

Control flow: `FinalizationStateManagerImpl.getFinalizationCheckpoint` iterates the enum values and chooses the checkpoint whose expected booleans match current disk/in-memory state. Higher-level code uses `hasCrossed` to decide whether pipelines should be frozen, datanodes should be told to finalize, and finalization should resume on leader readiness.

State and persistence behavior: The enum itself is immutable. It encodes how persistent markers map to runtime upgrade status. The ordering of enum constants is semantically significant because `hasCrossed` uses `compareTo`.

Dependencies and integration points: It is used by `FinalizationManager`, `FinalizationStateManagerImpl`, `SCMContext`, and `StorageContainerManager` initialization. Client-facing upgrade status is coupled to the status stored in each enum value.

Risks: Reordering enum constants would change checkpoint progression. Adding a new checkpoint requires updating the boolean mapping and helper logic. If the two persistent facts ever cannot map to one of these states, SCM terminates through `ExitUtils` in the state manager.

Test signals: Tests should assert all four boolean combinations map to the expected checkpoint, status mapping is stable, `hasCrossed` ordering is correct, and helper methods in `FinalizationManager` react correctly at each checkpoint.
