# sources/user-network-fs/rclone/backend/iclouddrive/iclouddrive_test.go

## Purpose
Defines the iCloud Drive integration test entrypoint for rclone's generic filesystem test suite.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestICloudDrive:"` and `NilObject: (*iclouddrive.Object)(nil)`.

## Control Flow
The test is gated by the same non-Plan9/non-Solaris build tag as the backend. When credentials/config for `TestICloudDrive:` exist, `fstests.Run` exercises the backend through rclone's common object, directory, upload, download, move, purge, and feature tests.

## State and Persistence
No local state is persisted by the test file itself. It relies on rclone test remote configuration and any remote iCloud state created and cleaned up by `fstests`.

## Dependencies and Integration Points
Imports the backend package and `github.com/rclone/rclone/fstest/fstests`. It is the main automated integration signal that the backend conforms to the rclone interface contract.

## Risks and Edge Cases
The test requires real iCloud credentials and network access, so it may not run in normal unit-test lanes. It does not isolate individual retry, normalization, or unknown-result behavior; failures will often appear as broad integration failures.

## Test Signals
Presence of this test means interface regressions can be caught by rclone's shared suite when the remote is configured. There are no pure unit tests for `iclouddrive.go` in this file.
