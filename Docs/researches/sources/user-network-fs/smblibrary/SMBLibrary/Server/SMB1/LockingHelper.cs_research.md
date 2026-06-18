# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB1/LockingHelper.cs

## Purpose

Handles SMB1 `LOCKING_ANDX` byte-range lock and unlock requests.

## Important APIs, Types, And Functions

`GetLockingAndXResponse` validates FID, rejects `CHANGE_LOCKTYPE`, processes unlock ranges, processes lock ranges, and rolls back prior locks if a later lock fails.

## Control Flow

The method returns no response when both lock and unlock counts are zero. Unlocks are applied first. Locks use exclusive mode unless the request has `SHARED_LOCK`; on failure, all locks acquired earlier in the same request are unlocked to preserve atomicity.

## State And Persistence Behavior

Persistent lock state lives in the file store. Session open-file state is only read.

## Dependencies And Integration Points

Uses SMB1 lock command types, `SMB1Session`, `OpenFileObject`, and `INTFileStore.LockFile`/`UnlockFile`.

## Risks And Edge Cases

Rollback ignores unlock status. `CANCEL_LOCK` is mentioned in comments but no separate cancel behavior is implemented. Session lookup is assumed valid.

## Test Signals

Test invalid FID, zero-count no-response, unsupported change-locktype, shared/exclusive locks, unlocks, failure rollback, and overlapping lock conflict statuses.

Source-read signal: reviewed the complete local source file for this item.
