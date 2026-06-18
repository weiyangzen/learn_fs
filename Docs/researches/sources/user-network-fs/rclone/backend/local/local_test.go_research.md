
# sources/user-network-fs/rclone/backend/local/local_test.go

## Purpose
Runs rclone's generic integration test suite against the local backend.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with the empty local remote name, nil object sentinel `*local.Object`, and `QuickTestOK: true`.

## State And Persistence
Creates temporary local files and directories under the fstest root and cleans them up through the test harness.

## Dependencies And Integration Points
Uses the standard `fstests` suite to exercise local backend interface behavior across many common operations.

## Risks And Test Signals
Provides broad interface regression coverage. Platform-specific behavior is partly covered here and partly in internal tests and build-tagged helper tests.
