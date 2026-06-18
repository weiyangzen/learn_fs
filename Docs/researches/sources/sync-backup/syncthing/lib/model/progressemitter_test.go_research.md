# sources/sync-backup/syncthing/lib/model/progressemitter_test.go

## Purpose

`progressemitter_test.go` verifies `ProgressEmitter` behavior for local download progress events and remote BEP `DownloadProgress` messages. It focuses on event timing, state diffing, temporary-index eligibility, append/forget message correctness, subscription cleanup, and no-op behavior when state has not materially changed.

## Important APIs, Helpers, and Test Cases

- `timeout` is the short polling duration for event expectations.
- `caller` annotates test failures with the source call site.
- `expectEvent` polls an event subscription and asserts a `DownloadProgress` event with the expected top-level folder count.
- `expectTimeout` asserts that no event arrives within the short timeout.
- `TestProgressEmitter` exercises local event emission as a puller is registered, updated by copy/pull operations, and deregistered.
- `TestSendDownloadProgressMessages` is a detailed protocol-message state machine test for `computeProgressUpdates`.
- `sendMsgs` calls `computeProgressUpdates` under the emitter lock and sends the resulting messages to fake connections, matching production's split between computation and sends.

## Control Flow

`TestProgressEmitter` creates an event logger, config wrapper, and emitter with a positive interval, then manually sets `p.interval = 0` to make timer ticks immediate after registration. It first expects no event, registers a `sharedPullerState`, and then mutates that state through methods such as `copyDone`, `copiedFromOrigin`, `pullStarted`, and `pullDone`. Each mutation should produce exactly one local event, followed by a timeout when no further change occurs. Deregistration should emit an empty progress event.

`TestSendDownloadProgressMessages` creates a fake connection subscribed to two folders and directly manipulates `p.registry` with crafted `sharedPullerState` objects. It uses an `expect` helper to locate messages for a folder and verify update type, file version, and block indexes. The test repeatedly calls `sendMsgs` after changing availability, update timestamps, versions, creation timestamps, registry membership, and subscriptions.

## State and Persistence Behavior

The tests operate entirely in memory. They inspect fake connection `downloadProgressMessages` and the emitter's `sentDownloadStates` map. They verify that sent state remembers prior append messages, produces only diffs for newly available blocks, sends forgets when pullers disappear or versions change, and deletes device state after temporary-index unsubscribe.

No file or database persistence is involved.

## Dependencies and Integration Points

The test uses config wrappers, event logger service, fake protocol connections from the model test harness, `protocol.Vector`, `protocol.FileInfo`, and `protocol.FileDownloadProgressUpdateType*` constants. It depends on `sharedPullerState` methods from the puller implementation to update progress timestamps in the same way production pullers do.

## Risks and Edge Cases Captured

- No duplicate local events should be emitted when progress did not change.
- Temporary-index messages require more blocks than `TempIndexMinBlocks`; smaller files, directories, symlinks, and pullers in unsubscribed folders are ignored.
- Availability changes without an updated timestamp do not produce messages, matching the timestamp-driven design.
- Version changes require a forget for the old version and append for the new version.
- Puller recreation with the same file version still forces forget plus append because creation time changed.
- Deleted/disappeared pullers produce forget messages only once.
- Folder subscription cleanup currently does not send forget messages for unshared folders, and the test documents this behavior with commented expectations.

## Test Signals

These tests are strong coverage for `ProgressEmitter.computeProgressUpdates` and local event emission. They deliberately avoid depending on deterministic map iteration by locating updates dynamically. The main residual risk is that the tests call `computeProgressUpdates` directly for protocol messages rather than running the full `Serve` timer path, though `TestProgressEmitter` does cover the timer/event loop for local events.
