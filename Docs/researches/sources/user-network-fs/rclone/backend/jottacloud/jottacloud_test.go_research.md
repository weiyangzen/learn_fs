
# sources/user-network-fs/rclone/backend/jottacloud/jottacloud_test.go

## Purpose
Registers the Jottacloud backend with rclone's standard integration test harness.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestJottacloud:"` and a nil object sentinel of type `*jottacloud.Object`. The generic suite exercises object creation, listing, updates, removals, directory operations, feature declarations, hashes, and optional backend hooks.

## State And Persistence
State is entirely test-remote data created and cleaned up by `fstests.Run`; no local persistent files are produced beyond normal test artifacts.

## Dependencies And Integration Points
Depends on the external Jottacloud test remote being configured in rclone's test environment. Imports the backend package to expose the concrete object type to the generic suite.

## Risks And Test Signals
The test is a broad integration signal but not hermetic. Failures can reflect account quota, network/API changes, config drift, or backend regressions.
