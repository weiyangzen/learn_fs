# sources/user-network-fs/rclone/lib/errcount/errcount_test.go

Source read signal: reviewed complete local file (27 lines, sha256 b7c4d25df3c9a63e).

Purpose: Verifies the observable behavior of `ErrCount`.

Important APIs/types/functions: `TestErrCount` uses `New`, `Add`, and `Err` with two sentinel errors.

Control flow: It checks initial nil status, adds one error and validates message/wrapping, then adds a second error and validates count text plus wrapping of the latest error.

State and persistence behavior: No persistent state; all state is inside one `ErrCount`.

Dependencies and integration points: Uses Go `errors`, `testing`, and `testify/assert`.

Risks and test signals: Covers the main API but not concurrent `Add`/`Err` calls; thread-safety relies on the mutex implementation.
