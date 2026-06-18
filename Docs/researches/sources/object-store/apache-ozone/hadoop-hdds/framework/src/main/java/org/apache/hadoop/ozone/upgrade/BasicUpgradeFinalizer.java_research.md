# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/upgrade/BasicUpgradeFinalizer.java

## Purpose

`BasicUpgradeFinalizer` is the base class for service-specific upgrade finalizers. It coordinates one finalization run, client ownership of status messages, layout feature finalization actions, VERSION file updates, and status transitions. The complete 343-line source was read for this report.

## Important APIs, Types, and Functions

Important methods are `finalize`, `reportStatus`, `getStatus`, `preFinalizeUpgrade`, `postFinalizeUpgrade`, `finalizeAndWaitForCompletion`, `isFinalizationDone`, `markFinalizationDone`, `getVersionManager`, abstract `finalizeLayoutFeature`, protected `finalizeLayoutFeature(LayoutFeature, Optional<UpgradeAction>, Storage)`, `runFinalizationAction`, `updateLayoutVersionInVersionFile`, and message/log helpers.

## Control Flow

`finalize` first returns finalized status if already done, then uses a `ReentrantLock` to ensure only one finalization thread runs. `initFinalize` validates current upgrade state and client ID ownership, transitions required finalization to `STARTING_FINALIZATION`, and records the initiating client/component. If required or interrupted in-progress, the executor runs finalization. `reportStatus` optionally transfers client ownership, verifies client ID, drains queued messages, and returns current state. `finalizeAndWaitForCompletion` starts finalization and polls status until timeout.

## State and Persistence Behavior

State includes version manager reference, initiating client ID, component context, executor, finalization lock, message queue, and testing done flag. Persistent state changes happen when `updateLayoutVersionInVersionFile` sets a `Storage` layout version and calls `persistCurrentState`; on write failure it rolls back the in-memory layout version before throwing.

## Dependencies and Integration Points

It depends on `AbstractLayoutVersionManager`, `DefaultUpgradeFinalizationExecutor`, `UpgradeFinalization`, `UpgradeException`, `LayoutFeature.UpgradeAction`, `Storage`, Ratis `NotLeaderException`, and Hadoop `Time`. Component finalizers subclass it to define per-feature finalization.

## Risks and Edge Cases

The executor is invoked while holding the finalization lock in this implementation, so long finalization blocks concurrent `finalize` calls but not synchronized status polling. `clientID` and message handling are synchronization-sensitive. Inconsistent version manager state results in invalid-request exceptions. Persistent VERSION update failure must roll back correctly. `isDone` is not volatile and is testing-focused.

## Test Signals

Tests should cover already-finalized, required, in-progress, and inconsistent states; one-run locking; client takeover/status message draining; wait timeout; feature action success/failure; VERSION update rollback; NotLeader handling; and injected executor failures.
