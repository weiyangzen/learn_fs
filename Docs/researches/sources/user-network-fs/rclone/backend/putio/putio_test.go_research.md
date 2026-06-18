# sources/user-network-fs/rclone/backend/putio/putio_test.go

## Purpose
Put.io integration test: runs standard rclone fstests against TestPutio.

## Important APIs, Types, And Functions
Important surface: TestIntegration with RemoteName and NilObject.

## Control Flow
delegates to fstests

## State And Persistence
remote account test data only.

## Dependencies And Integration Points
fstest/fstests.

## Risks And Test Signals
Risks and useful test signals: does not deterministically test TUS retry or offset recovery.
