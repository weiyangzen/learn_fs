<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_test.go -->
# sources/user-network-fs/rclone/fs/fserrors/error_test.go

## Purpose
Unit tests for fserrors wrappers, cause walking, retry decisions, retry-after, and context handling.

## Important APIs, Types, And Control Flow
Defines custom wrapper and temporary error types to test `Cause`, `RetryError`, `FatalError`, `NoRetryError`, `NoLowLevelRetryError`, `FsError`, `Count`, `IsCounted`, `ShouldRetry`, `RetryAfterErrorTime`, `IsRetryAfterError`, and `ContextError`. Tables include EOFs, temporary errors, closed network string, no-low-level-retry override, and context cancellation/deadline.

## State And Persistence
Local errors only, except countable wrappers mutate their counted flag.

## Dependencies And Integration Points
Uses rclone error walking and standard context/errors behavior.

## Risks And Test Signals
Strong classifier coverage. It does not exhaust every string phrase in `retriableErrorStrings` or every platform retriable errno.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error_test.go -->
