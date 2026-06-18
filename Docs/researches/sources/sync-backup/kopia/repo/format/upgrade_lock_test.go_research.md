# sources/sync-backup/kopia/repo/format/upgrade_lock_test.go

## Purpose
Integration-tests repository format upgrade lock behavior with real repository environments, storage backups, rollback, commit, and active write sessions.

## Important APIs, Types, And Functions
Tests include `TestFormatUpgradeSetLock`, `TestFormatUpgradeAlreadyUpgraded`, `TestFormatUpgradeCommit`, `TestFormatUpgradeRollback`, `TestFormatUpgradeMultipleLocksRollback`, `TestFormatUpgradeFailureToBackupFormatBlobOnLock`, and `TestFormatUpgradeDuringOngoingWriteSessions`. Helper `writeObject` writes object data through repository writers.

## Control Flow
Tests create repositories at specific format versions, set locks with valid/invalid owners, update advance notice, commit or roll back, reopen repositories to observe persisted state, and inspect backup blob lists. Failure tests wrap storage with before-operation hooks to force backup, restore, delete, or get errors. Active-session tests open multiple writers, set an upgrade lock from another client, verify writes flush before cache refresh notices the lock, advance time beyond format cache duration, and assert later flushes fail with repository-unavailable errors.

## State And Persistence
Uses real repository initialization over map/versioned/reconnectable storage. Persistent artifacts include format blobs, backup blobs, legacy poison blobs, object contents, and session-related state.

## Dependencies And Integration Points
Depends on `repotesting`, `repo`, `content`, `object`, `blobtesting`, `beforeop`, format manager APIs, and repository writer interfaces. This is the main integration signal for upgrade locks across format, content, and object layers.

## Risks And Edge Cases
Multiple-lock rollback demonstrates stale-cache clients can create multiple backups and rollback must pick the oldest. Failure injection shows rollback can be retried after transient failures. Active writer behavior depends on format cache duration and lock monitoring; writes already in flight may complete until clients refresh lock state.

## Test Signals
Coverage is broad and high-value for upgrade safety. It does not validate that legacy clients actually fail on the poison blob within this test file, but it verifies poison write is attempted during commit.
