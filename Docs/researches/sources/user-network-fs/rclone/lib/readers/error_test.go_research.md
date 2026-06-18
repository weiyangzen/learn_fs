# sources/user-network-fs/rclone/lib/readers/error_test.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error_test.go -->
## sources/user-network-fs/rclone/lib/readers/error_test.go

Purpose: unit-tests `ErrorReader`.

Important APIs and control flow: `TestErrorReader` creates a sentinel `errors.New("boom")`, reads into a buffer, and asserts the same error and zero bytes are returned.

State, dependencies, and integration: dependencies are `errors`, `testing`, and testify. The test is a direct package-level check.

Risks and test signals: it covers the intended non-nil-error path only. It does not cover nil error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/readers/error_test.go -->
