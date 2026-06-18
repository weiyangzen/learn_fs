# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/ozone/upgrade/TestDefaultUpgradeFinalizationExecutor.java

Purpose: Tests exception propagation policy in `DefaultUpgradeFinalizationExecutor`.

Important APIs/types/functions: `DefaultUpgradeFinalizationExecutor.execute`, anonymous `BasicUpgradeFinalizer`, `preFinalizeUpgrade`, `postFinalizeUpgrade`, `finalizeLayoutFeature`, and `AbstractLayoutVersionManager.needsFinalization`.

Control flow: The first test creates a finalizer whose pre-finalize step throws and asserts `execute` propagates the `IOException`. The second creates a finalizer whose post-finalize step throws while finalization is no longer needed and asserts the executor completes without throwing.

State and persistence behavior: State is mocked through `needsFinalization`; no persisted layout files are used.

Dependencies and integration points: Uses Mockito to mock the layout version manager and JUnit exception assertions.

Risks: Raw generic usage hides type-safety issues. Tests do not cover exceptions during individual feature finalization.

Test signals: Focused signal for pre-finalize hard failure versus post-finalize soft failure behavior.
