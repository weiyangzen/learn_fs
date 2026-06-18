# sources/user-network-fs/rclone/backend/union/errors_test.go

Purpose: unit tests for the union `Errors` aggregate type.

Important APIs: `TestErrorsMap`, `TestErrorsFilterNil`, `TestErrorsErr`, `TestErrorsError`, and `TestErrorsUnwrap` using sentinel `err1`, `err2`, `err3`.

Control flow/state: constructs literal error slices and compares transformed values, nil handling, exact string output, and `errors.Is` behavior.

Dependencies/integration: standard `errors`, `testing`, and testify `assert`.

Risks/test signals: exact formatting tests catch user-visible message regressions; unwrapping tests protect compatibility with Go multi-error matching.
