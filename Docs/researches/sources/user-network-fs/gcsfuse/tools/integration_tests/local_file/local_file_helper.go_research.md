<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/local_file_helper.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/local_file_helper.go

## Purpose

This helper file centralizes shared state and local-file helper assertions for the local file integration package. It expresses the core contract that writes to a still-open local file are not visible in GCS until the file is closed.

## Important APIs, Types, and Functions

It defines constants `onlyDirMounted` and `testDirLocalFileTest`, package globals `testDirName`, `testDirPath`, `storageClient`, and `ctx`, plus helpers `WritingToLocalFileShouldNotWriteToGCS` and `NewFileShouldGetSyncedToGCSAtClose`.

## Control Flow

`WritingToLocalFileShouldNotWriteToGCS` writes `client.FileContents` to an open file handle without closing and immediately validates the corresponding GCS object is not found. `NewFileShouldGetSyncedToGCSAtClose` creates a local file, derives the directory name, calls the no-GCS-before-close helper, then closes and validates GCS content.

## State and Persistence Behavior

The helpers make unsynced local file-handle state explicit: write buffers are durable locally but not persisted to GCS until close. Package globals are assigned by `setup_test.go` and individual tests.

## Dependencies and Integration Points

It depends on Cloud Storage client types, shared client helpers, operations write helpers, and the local-file test suite. Nearly every local file test imports or relies on these package globals.

## Risks and Test Signals

The helpers assume object non-existence is the correct pre-close signal and that `client.GetDirName` maps mounted paths to the expected GCS test directory. Failures here usually indicate core local-file writeback contract regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/local_file_helper.go -->
