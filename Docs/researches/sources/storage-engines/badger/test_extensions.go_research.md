# sources/storage-engines/badger/test_extensions.go

## Purpose
This file adds lightweight test-only extension fields and helper methods to production Badger types without importing `testing`. It lets tests observe internal lifecycle events and capture discard statistics while keeping production behavior effectively no-op unless channels/maps are configured.

## Important APIs, Types, and Functions
- Constants `updateDiscardStatsMsg` and `endVLogInitMsg` define synchronization messages for tests.
- `testOnlyOptions` adds a `syncChan` to `Options`.
- `testOnlyDBExtensions` adds `syncChan` and `onCloseDiscardCapture` to `DB`.
- `(*DB).logToSyncChan` sends a message on the DB sync channel if present.
- `(*DB).captureDiscardStats` copies value-log discard stats into `onCloseDiscardCapture` during close if configured.

## Control Flow and State Behavior
The file relies on embedding or composition elsewhere in `Options` and `DB`. `logToSyncChan` silently does nothing when `syncChan` is nil; otherwise it sends synchronously, so tests can block until specific internal milestones happen. `captureDiscardStats` locks the value-log discard stats structure, iterates its contents, and copies ID/value pairs into a test-provided map.

## Dependencies and Integration Points
It integrates with value-log initialization, discard stats updates, and DB close paths that call these helper methods. It intentionally avoids importing `testing` so production package dependencies do not change.

## Risks and Edge Cases
Because this is compiled into production, a non-nil unbuffered `syncChan` can block production code if accidentally set outside tests. The comments note a possible future build-tag split. `captureDiscardStats` assumes `db.vlog` and its `discardStats` are valid when called. The map is caller-owned and not internally synchronized beyond the discardStats lock.

## Test Signals
There is no direct test file in this subset, but other Badger tests can use these hooks to wait for background events and inspect close-time discard accounting.
