
# sources/user-network-fs/rclone/backend/hidrive/hidrive_test.go

## Purpose
This file hooks the HiDrive backend into rclone's generic integration test suite and provides test-only setters for upload chunking parameters.

## Important APIs, Types, And Control Flow
`TestIntegration` runs `fstests.Run` against `TestHiDrive:` with HiDrive's object type and `ChunkedUploadConfig` spanning one byte through `MaximumUploadBytes`. `SetUploadChunkSize` and `SetUploadCutoff` mutate `f.opt` and return the previous value so the generic tests can force chunked upload scenarios.

## State And Persistence
The test mutates backend upload options in memory during tests. Remote persistence is handled by the generic integration suite against the configured HiDrive remote.

## Dependencies And Integration Points
It integrates with `fstests.SetUploadChunkSizer` and `fstests.SetUploadCutoffer`, allowing generic test cases to exercise chunk boundaries.

## Risks And Test Signals
The test suite depends on a real `TestHiDrive:` remote and valid OAuth. It is a broad signal for standard rclone behavior and chunked uploads, but does not directly unit-test REST error mapping, token renewer nil behavior, recursive mkdir rollback absence, or sparse chunk failure semantics.
