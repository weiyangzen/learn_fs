# sources/user-network-fs/rclone/backend/pcloud/pcloud_test.go

Purpose: connects the pCloud backend to rclone's integration test harness.

Important APIs/types/functions: `TestIntegration` calls `fstests.Run` with `RemoteName: "TestPcloud:"` and `NilObject: (*pcloud.Object)(nil)`.

Control flow: all filesystem behavior is delegated to the shared `fstests` suite. No pCloud-specific skips or setup are declared here.

State and persistence: tests operate against the configured `TestPcloud:` account and can create, update, move, and delete remote objects and folders. No local persistent state is managed by the test file.

Dependencies/integration: imports the backend externally as `pcloud_test`, which verifies public package integration. Depends on `github.com/rclone/rclone/fstest/fstests`.

Risks/test signals: success depends on live credentials and pCloud API availability. Since no special skips are configured, production code must absorb backend quirks. The signal is broad rclone filesystem conformance.
