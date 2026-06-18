# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/DefaultUpgradeFinalizationExecutor.java

## Purpose

`DefaultUpgradeFinalizationExecutor` drives the normal finalization sequence for a `BasicUpgradeFinalizer`. The complete 73-line source was read for this report.

## Important APIs, Types, and Functions

It implements `UpgradeFinalizationExecutor<T>` with `execute`. Protected `finalizeFeatures` iterates layout features and delegates to the finalizer.

## Control Flow

`execute` emits start, calls `preFinalizeUpgrade`, finalizes each unfinalized feature from the version manager, calls `postFinalizeUpgrade`, and emits finish. If any exception occurs and finalization is still needed, it resets upgrade state to `FINALIZATION_REQUIRED` and rethrows. The `finally` block marks finalization done for tests.

## State and Persistence Behavior

The executor holds no mutable state. Persistent layout/version changes are performed by the finalizer while finalizing features.

## Dependencies and Integration Points

It depends on `BasicUpgradeFinalizer`, `LayoutFeature`, `UpgradeException`, and `UpgradeFinalization.Status`. It is the default executor used by `BasicUpgradeFinalizer`.

## Risks and Edge Cases

If an exception occurs after `needsFinalization()` becomes false, it is swallowed after logging and done marking. `markFinalizationDone` is testing-oriented and can be true after failed attempts. Feature iteration order comes from the version manager.

## Test Signals

Tests should cover successful sequence ordering, exception reset behavior, no-reset behavior when finalization no longer needed, and overridden `finalizeFeatures` for injection.
