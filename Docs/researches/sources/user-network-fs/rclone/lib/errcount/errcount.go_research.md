# sources/user-network-fs/rclone/lib/errcount/errcount.go

Source read signal: reviewed complete local file (58 lines, sha256 70ff2e49351470d7).

Purpose: Provides a thread-safe accumulator that reports the number of errors and the last error without flooding users with every failure.

Important APIs/types/functions: Type `ErrCount` holds a mutex, last error, and count. `New`, `Add`, and `Err` are the public API.

Control flow: `Add` ignores nil, then increments count and stores the latest error under lock. `Err` returns nil for no errors, wraps the only error for count one, or formats a summary with count plus last error for multiple failures.

State and persistence behavior: State is in-memory per `ErrCount` instance. Wrapped errors preserve `errors.Is` visibility for the last error.

Dependencies and integration points: Uses `sync` and `fmt`. It is suitable for batch operations that need a final summarized error.

Risks and test signals: Only the last non-nil error is retained, so earlier error identity is intentionally lost. Tests cover nil, single-error wrapping, multi-error count text, and `errors.Is` on the last error.
