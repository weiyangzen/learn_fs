
# sources/user-network-fs/rclone/backend/hdfs/hdfs_test.go

## Purpose
This is the HDFS integration-test entry point for rclone's generic backend test suite.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestHdfs:"` and `NilObject: (*hdfs.Object)(nil)`. The test suite then drives the backend through standard object, directory, upload, move, remove, and metadata behaviors when a matching test remote is configured.

## State And Persistence
The test persists data only in the configured test HDFS remote through `fstests`. It does not define local fixtures or mocks.

## Dependencies And Integration Points
It imports the backend package and `github.com/rclone/rclone/fstest/fstests`. It is gated by `!plan9`, matching the backend implementation.

## Risks And Test Signals
Because this file delegates entirely to `fstests`, failures depend on external HDFS availability and credentials. It is a broad behavioral signal, but it does not directly test Kerberos branches, HDFS overwrite semantics, `ErrReplicating` close retry, or path encoding edge cases unless the generic suite happens to hit them.
