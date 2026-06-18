# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOMUpgradeFinalizer.java

## Purpose
`TestOMUpgradeFinalizer` validates OM layout finalization status reporting, client ownership/takeover behavior, execution of upgrade actions, storage layout version advancement, and failure handling.

## Important APIs, Types, and Functions
- `OMUpgradeFinalizer.finalize(clientId, OzoneManager)` starts finalization.
- `reportStatus(clientId, takeover)` reports finalization status and enforces client ownership unless takeover is requested.
- `OMLayoutVersionManager` supplies upgrade state, `needsFinalization`, and `unfinalizedFeatures`.
- `OMLayoutFeature.action()` may provide an `OmUpgradeAction`.
- `OMStorage.setLayoutVersion` persists finalized layout versions.

## Control Flow
Already-finalized state returns `ALREADY_FINALIZED`. Required-finalization setup supplies mocked feature iterables and expects `STARTING_FINALIZATION`, then later `FINALIZATION_DONE`. Report status from a different client fails unless takeover is true. Action tests attach an upgrade action to the first feature, assert it calls `OzoneManager.getVersion`, and verify both feature layout versions are written. Failure tests throw from the first action and assert an `UpgradeException` with `LAYOUT_FEATURE_FINALIZATION_FAILED`, with no storage version updates.

## State and Persistence Behavior
Persistent state is modeled through `OMStorage.setLayoutVersion` and an in-test `storedLayoutVersion` field. The finalizer also holds client ownership and completion status in memory. Messages accumulated by finalization are expected to be non-empty after completion/failure.

## Dependencies and Integration Points
The test uses `UpgradeFinalization.Status`, `UpgradeException`, `LayoutFeature`, `OMLayoutFeature`, `OmUpgradeAction`, `OzoneManager`, and `OMStorage`. It protects the transition point from feature-level actions to durable OM layout version storage.

## Risks and Edge Cases
Covered risks include incorrect already-finalized behavior, unknown client status polling, missing takeover support, action execution order, and version persistence after failure. The current test notes that finalization runs synchronously; if behavior becomes background/state-machine-driven, in-progress status tests must be updated.

## Test Signals
This is the primary unit signal for finalization sequencing and failure atomicity: failed feature actions must not advance stored layout versions.
