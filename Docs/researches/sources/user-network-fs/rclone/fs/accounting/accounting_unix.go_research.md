<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_unix.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting_unix.go

## Purpose

`accounting_unix.go` implements SIGUSR2-driven bandwidth-limit toggling for Unix-like builds.

## Important APIs, Types, and Functions

`(*tokenBucket).startSignalHandler` registers `syscall.SIGUSR2`, starts a goroutine, and on each signal swaps current and previous token buckets while toggling `toggledOff`.

## Control Flow

On signal receipt, the handler locks the token bucket, ignores the signal if no current bandwidth schedule is configured, flips the toggle state, swaps `curr` and `prev`, and logs whether limits are enabled or disabled.

## State and Persistence Behavior

State is process memory: signal subscription, goroutine lifetime, `toggledOff`, and token bucket sets. No settings are persisted.

## Dependencies and Integration Points

It depends on Go signal handling and Unix build tags. It integrates with scheduled bandwidth updates in `token_bucket.go`, which may update `prev` while toggled off.

## Risks and Test Signals

Risks include unbounded goroutine lifetime, signal handler duplication if start is called repeatedly, lock contention, and confusing schedule changes while toggled off. Tests are mostly integration/manual: start with bwlimit, send SIGUSR2, and observe rc/logged limiter state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_unix.go -->
