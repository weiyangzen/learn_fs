# sources/user-network-fs/rclone/lib/readers/noclose_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose_test.go -->
## sources/user-network-fs/rclone/lib/readers/noclose_test.go

Purpose: validates that `NoCloser` removes close capability only when necessary.

Important APIs and control flow: the test asserts nil remains nil, a read-only reader is returned unchanged, a read-closer is wrapped, the wrapper no longer satisfies `io.Closer`, and reading through the wrapper returns the underlying read error.

State, dependencies, and integration: test fixtures implement small `readOnly` and `readClose` types. Dependencies are `errors`, `io`, `testing`, and testify.

Risks and test signals: confirms type-level behavior and delegation. It does not test interactions with `http.NewRequest`, which is the main integration motivation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/noclose_test.go -->
