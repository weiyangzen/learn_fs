# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/LockElement.cs

## Purpose

Represents one SMB2 byte-range lock element and provides helpers for lock-list marshalling.

## Important APIs, Types, And Functions

Fields are `Offset`, `Length`, `Flags`, and `Reserved`. Boolean properties toggle each `LockFlags` bit. `ReadLockList` and `WriteLockList` process repeated 24-byte elements.

## Control Flow

Parsing reads 64-bit offset/length then 32-bit flags/reserved. The boolean setters mutate the flag mask in place. List helpers step by `StructureLength`.

## State And Persistence Behavior

Lock elements are request/response payload data; persistent lock state is managed by `INTFileStore.LockFile` and `UnlockFile` in command handlers.

## Dependencies And Integration Points

Uses `Utilities` byte helpers and `LockFlags`; integrates with SMB2 lock request handling.

## Risks And Edge Cases

`WriteBytes` writes `Flags` and `Reserved` with `WriteUInt64` at offsets 16 and 20 even though both fields are 32-bit. That can overwrite beyond the 24-byte structure and corrupt adjacent elements. The struct also does not validate exclusive/shared/unlock combinations.

## Test Signals

Round-trip a single lock and a two-lock list with sentinels after the buffer to catch overwrite. Add validation tests for shared, exclusive, unlock, and fail-immediately combinations.

Source-read signal: reviewed the complete local source file for this item.
