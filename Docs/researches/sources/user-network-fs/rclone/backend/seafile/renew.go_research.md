# sources/user-network-fs/rclone/backend/seafile/renew.go

## Purpose
This file implements a small background renewal helper used by the Seafile backend to refresh expiring tokens, such as decryption tokens. It repeatedly invokes a caller-provided renewal callback on a ticker until shut down.

## Important APIs, Types, And Functions
`Renew` holds a `time.Ticker`, the `run func() error` callback, a `done` channel, and a `sync.Once` for idempotent shutdown. `NewRenew` constructs the ticker and starts `renewOnExpiry` in a goroutine. `renewOnExpiry` selects on ticker ticks or shutdown and logs callback errors. `Shutdown` stops the ticker and closes the done channel once.

## Control Flow
Creation immediately starts the goroutine. On each tick, `run` is called synchronously. If it returns an error, the error is logged but the loop continues. When `Shutdown` closes `done`, the goroutine returns. `Shutdown` can be called multiple times safely because channel close and ticker stop are protected by `sync.Once`.

## State And Persistence Behavior
State is in-memory only: a ticker, goroutine, done channel, and callback. Remote token state is changed only through the supplied callback, not by this helper directly. Shutdown prevents future renewals but does not wait for an already-running callback to finish.

## Dependencies And Integration Points
The file depends on `sync`, `time`, and rclone `fs` logging. It is intended to be owned by Seafile backend lifecycle code that knows when renewal is needed and when to shut it down.

## Risks And Edge Cases
If `run` blocks for longer than the ticker interval, renewals serialize and ticks may be dropped by the ticker. There is no context cancellation for the callback and no panic recovery. `Shutdown` does not wait for goroutine exit, so callers needing strict lifecycle ordering would need an additional acknowledgement mechanism. Errors are logged but not surfaced to the owner.

## Test Signals
`renew_test.go` verifies idempotent shutdown and that renewal fires at least once under a short interval. It does not test error logging, long-running callbacks, or shutdown during callback execution.
