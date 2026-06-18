# sources/user-network-fs/rclone/backend/filescom/filescom_test.go

Purpose: This is the generic integration-test entry point for the Files.com backend.

Important APIs and types: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestFilesCom:"` and `NilObject: (*filescom.Object)(nil)`.

Control flow: The shared rclone test suite constructs the configured remote and runs standard filesystem tests.

State and persistence behavior: It mutates the configured Files.com remote and any server-side sessions/actions created by backend operations.

Dependencies and integration points: It depends on `fstests`, the Files.com backend package, the Files.com SDK, and configured test credentials.

Risks: Provider migrations, session auth, and bundle links are not unit-tested locally. The generic suite is the only signal for SDK integration.

Test signals: Passing `fstests.Run` is the primary compatibility signal.
