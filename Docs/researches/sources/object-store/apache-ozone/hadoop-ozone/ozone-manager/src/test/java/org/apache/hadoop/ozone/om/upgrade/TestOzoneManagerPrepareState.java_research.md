# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/upgrade/TestOzoneManagerPrepareState.java

## Purpose
`TestOzoneManagerPrepareState` validates OM prepare-state lifecycle and its marker-file persistence. Prepare mode blocks normal OM write requests during upgrade preparation and must survive restart only when the marker file is valid for the applied transaction index.

## Important APIs, Types, and Functions
- `OzoneManagerPrepareState.enablePrepareGate`, `finishPrepare`, `cancelPrepare`, `restorePrepareFromFile`, `requestAllowed`, and `getState` are tested.
- `PrepareStatus` values include `NOT_PREPARED`, `PREPARE_GATE_ENABLED`, and `PREPARE_COMPLETED`.
- `getPrepareMarkerFile` exposes the marker file containing the prepare transaction index.
- `Type.Prepare` and `Type.CancelPrepare` are the only request types allowed while the gate is up.

## Control Flow
Tests cover starting prepare, finishing as follower and leader, repeated finish, cancel after start/finish/cancel, request gating, restore with correct index, restore with marker index behind OM transaction index, garbage marker content, empty marker, missing marker, gate-only in-memory state, and repeated restores. Assertion helpers centralize status, index, marker presence, and request allowance checks.

## State and Persistence Behavior
The marker file is durable state. `finishPrepare(TEST_INDEX)` writes the index, and restore reads and validates it. `cancelPrepare` removes the marker and drops the gate. Invalid marker content or stale marker index raises `OMException` with `PREPARE_FAILED`, while preserving in-memory gate state for gate-only restore failure.

## Dependencies and Integration Points
The test uses `OzoneConfiguration` with `OZONE_METADATA_DIRS`, OM protocol `Type`, prepare status protos, and file I/O. It protects upgrade prepare behavior that coordinates OM request admission with Ratis-applied transaction indexes.

## Risks and Edge Cases
Covered risks include accepting stale marker files, mishandling corrupt or empty files, dropping gate state on failed restore, and allowing disallowed request types during prepare. The helper `assertPrepareFailedException` only rethrows non-prepare failures, so callers must rely on follow-up state assertions to ensure failure occurred.

## Test Signals
This file is the main signal for prepare-state durability and gate semantics. It confirms that once prepare begins, only prepare/cancel requests pass until cancellation.
