# sources/sync-backup/syncthing/lib/model/folder_recvonly_test.go

## Purpose
Regression and behavior tests for receive-only folder local-change tracking and revert semantics.

## Important APIs, Types, and Functions
Tests include `TestRecvOnlyRevertDeletes`, `TestRecvOnlyRevertNeeds`, `TestRecvOnlyUndoChanges`, `TestRecvOnlyDeletedRemoteDrop`, `TestRecvOnlyRemoteUndoChanges`, `TestRecvOnlyRevertOwnID`, and `TestRecvOnlyLocalChangeDoesNotCauseConflict`. Helpers are `setupKnownFiles` and `setupROFolder`.

## Control Flow
Each test constructs a receive-only model, fake remote connection, and fake filesystem content. They send remote indexes, scan local state, mutate files or remote state, call `m.Revert` or direct pull, then assert global, local, need, and receive-only sizes or file existence. The own-ID test subscribes to local index updates and waits for a non-deleted equivalent file after revert.

## State and Persistence Behavior
Tests use the model database and fake filesystem to exercise real local index updates, scan results, deletion on disk, and event emission. Remote state is simulated via fake connection index updates.

## Dependencies and Integration Points
Uses the model test harness, config wrappers, `addFakeConn`, scanner blocks, events, and filesystem helpers. It validates receive-only integration across scanner, DB global/local views, puller, and revert API.

## Risks
The tests are integration-heavy and can be timing-sensitive where they wait on events. They focus on receive-only, not receive-encrypted. Assertions are mostly size-based, so some metadata details may be unverified.

## Test Signals
Strong coverage for user-visible receive-only invariants: local changes are detected but not needed, revert makes old global data needed again, equivalent remote changes clear receive-only state, and repeated local edits do not produce conflict pulls.
