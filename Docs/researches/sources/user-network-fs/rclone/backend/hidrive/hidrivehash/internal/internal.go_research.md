
# sources/user-network-fs/rclone/backend/hidrive/hidrivehash/internal/internal.go

## Purpose
This internal file defines the `LevelHash` interface used by tests and internal package consumers to expose level-specific hash operations without exporting the concrete `level` type.

## Important APIs, Types, And Control Flow
`LevelHash` embeds `encoding.BinaryMarshaler`, `encoding.BinaryUnmarshaler`, and `hash.Hash`, and adds `Add(sum []byte)` plus `IsFull() bool`. There is no executable control flow.

## State And Persistence
The interface defines behavior only. Implementations may have binary-marshaled state, but this file stores nothing.

## Dependencies And Integration Points
`hidrivehash.level` asserts conformance to this interface, and `hidrivehash_test.go` uses it to test `Add` and `IsFull` directly while keeping the concrete type unexported.

## Risks And Test Signals
Because this is an internal interface, its compatibility risk is small and limited to the `hidrivehash` package tree. Compile-time conformance and tests that type-assert `NewLevel()` to `internal.LevelHash` are the main signal.
