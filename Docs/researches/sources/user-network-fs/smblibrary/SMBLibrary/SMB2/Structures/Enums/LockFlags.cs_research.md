# sources/user-network-fs/smblibrary/SMBLibrary/SMB2/Structures/Enums/LockFlags.cs

## Purpose

Defines SMB2 lock element flag bits for shared locks, exclusive locks, unlock requests, and fail-immediately behavior.

## Important APIs, Types, And Functions

`LockFlags : uint` is a `[Flags]` enum with protocol constants `0x1`, `0x2`, `0x4`, and `0x8`.

## Control Flow

No control flow; `LockElement` reads, writes, and toggles these bits.

## State And Persistence Behavior

No local persistence. Values are passed to server file-lock handling.

## Dependencies And Integration Points

Consumed by `LockElement` and SMB2 lock request processing.

## Risks And Edge Cases

The enum permits invalid combinations such as shared plus exclusive plus unlock; validation must happen in lock command handling.

## Test Signals

Test bitwise combinations and command-layer rejection of mutually exclusive flag mixes.

Source-read signal: reviewed the complete local source file for this item.
