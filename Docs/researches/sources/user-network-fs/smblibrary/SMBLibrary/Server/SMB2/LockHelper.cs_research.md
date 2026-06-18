<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/LockHelper.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/LockHelper.cs

## Purpose
SMB2 byte-range lock and unlock handling. It validates SMB2 lock-array rules, applies locks or unlocks through the backing store, and rolls back previously acquired locks if a later lock in the request fails.

## APIs, Types, and Functions
`LockHelper.GetLockResponse()` is the entry point. It uses `LockRequest.Locks`, `LockElement` flags, `IFileStore.LockFile()`, `UnlockFile()`, and `LockResponse`.

## Control Flow, State, and Persistence
The helper resolves the open file, rejects empty lock arrays, determines whether the array is an unlock series from the first element, validates mixed lock/unlock and shared/exclusive flags, then processes elements in order. Multi-lock requests require `FailImmediately`. On a lock failure, earlier ranges from the same request are unlocked. State lives in the backing store's lock table.

## Dependencies and Integration
Called by SMB2 dispatch after tree lookup and session validation. It depends on `INTFileStore` lock semantics and session open-file tracking.

## Risks and Test Signals
Risks include no overflow checks when casting unsigned offsets/lengths to signed longs, rollback unlock failures being ignored, and limited async lock-wait support. Test invalid flag mixes, multi-lock rollback, unlock failures, boundary offsets, shared versus exclusive behavior, and invalid file IDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/Server/SMB2/LockHelper.cs -->
