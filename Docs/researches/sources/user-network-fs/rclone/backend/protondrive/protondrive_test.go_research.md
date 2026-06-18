# sources/user-network-fs/rclone/backend/protondrive/protondrive_test.go

## Purpose
Proton Drive integration test: runs the standard rclone fstests suite against TestProtonDrive.

## Important APIs, Types, And Functions
Important surface: TestIntegration with RemoteName and NilObject.

## Control Flow
delegates backend-contract operations to fstests

## State And Persistence
remote test data and rclone config credentials.

## Dependencies And Integration Points
fstest/fstests and protondrive backend.

## Risks And Test Signals
Risks and useful test signals: credential and account-state dependent; cache/draft/rate behavior may affect runs.
