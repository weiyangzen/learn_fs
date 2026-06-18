<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error.go -->
# sources/user-network-fs/rclone/fs/fserrors/error.go

## Purpose
Provides rclone's error classification wrappers and retry decision helpers.

## Important APIs, Types, And Control Flow
Defines interfaces and wrappers for high-level retry, fatal, no-retry, no-low-level-retry, retry-after, and countable errors. Constructors wrap nil with default messages where needed and implement `Unwrap` for `errors` compatibility. Detection helpers walk error chains with `lib/errors.Walk`. `Cause` records the root cause and flags `Timeout`/`Temporary`. `ShouldRetry` rejects no-low-level-retry, accepts timeout/temporary causes, known retriable errors, and selected network error string fragments. `ShouldRetryHTTP` checks configured status codes. `ContextError` promotes context cancellation/deadline errors into a pending error pointer.

## State And Persistence
Global retriable error/string slices are initialized here and extended by platform files. Countable wrappers carry mutable counted state.

## Dependencies And Integration Points
Used by low-level HTTP, backend, and operations retry loops. Integrates standard errors, HTTP responses, context cancellation, and rclone's cause walker.

## Risks And Test Signals
String matching is fragile but needed for unexported stdlib errors. Wrapper detection order matters when multiple classifications exist. Tests cover causes, retry decisions, retry-after, context errors, syscall wrapping, and countable behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/fserrors/error.go -->
