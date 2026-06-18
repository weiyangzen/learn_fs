# sources/user-network-fs/rclone/backend/qingstor/qingstor_test.go

## Purpose
QingStor integration test: runs standard fstests and exposes chunk-size/cutoff setters.

## Important APIs, Types, And Functions
Important surface: TestIntegration, SetUploadChunkSize, SetUploadCutoff.

## Control Flow
fstests can force chunked upload behavior

## State And Persistence
remote QingStor test data.

## Dependencies And Integration Points
fstest/fstests and fs.

## Risks And Test Signals
Risks and useful test signals: live-service dependent; endpoint and uploader unit coverage absent.
