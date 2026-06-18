# sources/user-network-fs/rclone/backend/oracleobjectstorage/waiter.go

Purpose: implements a generic state waiter used by the OCI backend to poll asynchronous operations such as object copy work requests.

Important APIs/types/functions: `StateRefreshFunc` returns a result, state string, and error. `StateChangeConf` configures delay, pending states, target states, timeout, minimum timeout, poll interval, not-found tolerance, and required continuous target occurrences. `WaitForStateContext` runs the wait loop. `NotFoundError`, `UnexpectedStateError`, and `TimeoutError` are structured failures with `Unwrap`.

Control flow: `WaitForStateContext` starts a goroutine, applies an initial delay, emits refresh results through a buffered channel, calls `Refresh`, classifies target/pending/unexpected states, applies exponential backoff bounded by `MinTimeout` and 10 seconds or `PollInterval`, and watches cancellation. The caller side returns on target success, context cancellation, or timeout. On timeout it cancels the refresh goroutine and gives it a 30-second grace period to report a final success.

State and persistence: all state is transient: last result, not-found retry count, target occurrence count, wait duration, channels, and timers. Nothing is persisted.

Dependencies/integration: depends on `context`, `time`, `slices`, `strings`, `fmt`, and `fs.Errorf`. The copy helper constructs this waiter around OCI work request lifecycle polling.

Risks/test signals: repeated `time.After` timers are simple but less efficient for very long polling. `UnexpectedStateError` formats a possibly nil last error. Grace-period behavior can exceed configured timeout. No direct unit tests exist; behavior is indirectly tested by OCI copy integration paths.
