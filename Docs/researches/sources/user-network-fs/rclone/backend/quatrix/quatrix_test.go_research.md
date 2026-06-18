# sources/user-network-fs/rclone/backend/quatrix/quatrix_test.go

## Purpose
Quatrix integration test: runs standard rclone fstests against TestQuatrix.

## Important APIs, Types, And Functions
Important surface: TestIntegration with RemoteName and NilObject.

## Control Flow
delegates to fstests

## State And Persistence
remote Quatrix account data.

## Dependencies And Integration Points
fstest/fstests.

## Risks And Test Signals
Risks and useful test signals: does not isolate dynamic chunking or hard-delete/project-folder behavior.
