# sources/user-network-fs/rclone/backend/filelu/filelu_test.go

Purpose: This is the generic integration-test entry point for the FileLu backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFileLu:"`, nil object, and `SkipInvalidUTF8: true`.

Control flow: The shared rclone test harness runs standard filesystem behavior tests against the configured remote.

State and persistence behavior: It mutates the configured FileLu remote and has no additional local state.

Dependencies and integration points: It depends on `fstests` and valid FileLu credentials under `TestFileLu:`.

Risks: Skipping invalid UTF-8 means the encoding-heavy path in `filelu.go` has reduced generic test coverage. FileLu-specific multipart, range, and hash edge cases have no local unit tests.

Test signals: Passing `fstests.Run` is the primary signal.
