# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/RangeLock.h

## Purpose
`RangeLock.h` declares serializable metadata for range locks, currently focused on an exclusive read lock type that rejects commits to locked ranges. It models owners, individual locks, and persisted lock sets per range.

## Important APIs, Types, And Functions
- `RangeLockType` currently has `Invalid` and `ExclusiveReadLock`.
- `RangeLockOwner` stores owner unique ID, description, log ID, and creation time; construction validates non-empty owner and description.
- `RangeLockState` stores lock type, owner ID, range, and reserved physical lock ID; it validates, stringifies, serializes, and derives a unique string from owner/type/range.
- `RangeLockStateSet` stores a map of unique lock string to state, validates all locks, inserts/removes locks, tests lock type presence, and serializes the set.

## Control Flow And State
Owner construction assigns a random log ID and `now()` timestamp. `RangeLockStateSet::insertIfNotExist()` rejects adding a different exclusive read lock if any lock already exists, enforcing one exclusive lock owner/type/range combination at a time. Removal erases by derived unique string.

## Persistence And External State
The structs have `FileIdentifier` values and `serialize()` methods, making them suitable for network or system-key persistence. The comments call out `RangeLockStateSet` as persisted state on a range.

## Dependencies And Integration Points
The header depends on Flow errors/random IDs/time, FDB key ranges, and fdbrpc serialization. It integrates with range lock management code and transaction commit validation that checks locked ranges.

## Risks And Edge Cases
`RangeLockState::getLockUniqueString()` uses textual range formatting and has a TODO to use `lockId`; formatting changes could affect identity if persisted keys are derived from it elsewhere. `RangeLockStateSet::insertIfNotExist()` only special-cases exclusive read locks, so future lock types need explicit compatibility rules. Owner equality ignores description/log/time and compares only unique ID.

## Test Signals
Tests should cover invalid owner/state rejection, serialization round trips, exclusive lock insertion conflicts, idempotent insertion of the same lock, removal by state, `isLockedFor`, equality independent of map iteration, string output, and compatibility when new lock types are added.
