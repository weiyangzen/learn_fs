# sources/sync-backup/kopia/internal/impossible/impossible_test.go

Purpose: verifies `PanicOnError` no-ops for nil and panics with the original error message for non-nil errors.

Important APIs/types/functions: `impossible.PanicOnError`, `errors.New`, and `require.PanicsWithError`.

Control flow: the test calls `PanicOnError(nil)`, then creates a sentinel error and asserts that invoking the helper panics with that error text.

State/persistence behavior: no persistent state. The test is pure control-flow validation.

Dependencies/integration: package `impossible_test` uses the exported helper only, with `testify/require`.

Risks/test signals: narrow by design; it does not test panic recovery behavior beyond matching the error string.
