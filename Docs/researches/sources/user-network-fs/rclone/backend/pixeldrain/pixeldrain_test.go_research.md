# sources/user-network-fs/rclone/backend/pixeldrain/pixeldrain_test.go

Purpose: connects the PixelDrain backend to rclone's integration test harness.

Important APIs/types/functions: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestPixeldrain:"`, `NilObject: (*pixeldrain.Object)(nil)`, and `SkipInvalidUTF8: true`.

Control flow: shared rclone filesystem tests drive all operations. The only backend-specific control is skipping invalid UTF-8 cases.

State and persistence: tests operate against a real configured PixelDrain filesystem and can create, update, share, move, and delete nodes. No local persistent state is managed.

Dependencies/integration: imports `pixeldrain` externally and `fstests`, validating public package integration.

Risks/test signals: reliability depends on API key validity, service availability, and root folder permissions. Invalid UTF-8 behavior is documented as unsupported by the skip. The signal is integration-level rclone conformance.
