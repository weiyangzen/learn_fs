<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors.go -->
# sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors.go

## Purpose

This package defines filesystem-specific error types. The current file contains `FileClobberedError`, used to report that an object backing a file was modified or deleted externally while gcsfuse was accessing it.

## Important APIs, Types, and Functions

`FileClobberedError` has `Err error` for the underlying cause and `ObjectName string` for the affected GCS object. `Error()` formats a user-facing concurrent modification message including the object name and wrapped error. `Unwrap()` returns `Err`, enabling `errors.Is` and `errors.As` through Go's standard error chaining.

## Control Flow

The type is passive. Callers construct it around lower-level storage or consistency errors. When logged or returned, `Error()` is called by Go error formatting; when matched, `Unwrap()` exposes the original cause.

## State and Persistence Behavior

The error stores only in-memory fields for one failure. It has no global state, no synchronization, and no persistence.

## Dependencies and Integration Points

The only direct dependency is `fmt`. The integration point is any fs/inode/handle path that detects a clobbered object generation or missing source object and wants both a gcsfuse-specific diagnostic and normal wrapped-error behavior.

## Risks and Edge Cases

`Error()` prints `<nil>` when `Err` is nil, which is intentional per tests but can look odd to users. The type uses a pointer receiver, so nil pointer use would panic. Any change to the message string can affect tests and user-facing diagnostics.

## Test Signals

The paired test validates the exact message for nil and non-nil underlying errors and verifies `errors.Is` works when a cause is present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors.go -->
