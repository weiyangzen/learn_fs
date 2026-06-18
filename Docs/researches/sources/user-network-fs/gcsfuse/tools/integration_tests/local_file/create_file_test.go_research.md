<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/create_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/create_file_test.go

## Purpose

This file tests creation and close-time synchronization of local files on a gcsfuse mount. It focuses on files that exist locally before they are uploaded to GCS and conflict behavior when the same object appears remotely.

## Important APIs, Types, and Functions

Tests are methods on `LocalFileTestSuite`. They use helper `NewFileShouldGetSyncedToGCSAtClose`, `CreateLocalFileInTestDir`, `WritingToLocalFileShouldNotWriteToGCS`, `CloseFileAndValidateContentFromGCS`, `CreateObjectInGCSTestDir`, and `operations.ValidateESTALEError`.

## Control Flow

The first two tests create new local files in the test directory and inside an explicit directory, write content without closing, verify no GCS object exists, then close and verify object contents. `TestCreateNewFileWhenSameFileExistsOnGCS` opens a local file, creates a same-name GCS object before close, writes local content, and expects close to fail with ESTALE while preserving the GCS content. `TestEmptyFileCreation` validates empty close creates an empty GCS object.

## State and Persistence Behavior

Unsynced local file handles are the main state. Data is not persisted to GCS until close, and concurrent remote creation introduces generation conflict semantics. `testDirPath` is reset per test through `setup.SetupTestDirectory`.

## Dependencies and Integration Points

This file depends on `local_file_helper.go` and shared client/operations/setup utilities. It runs under the local-file package's static, only-dir, and dynamic mounting modes and write-buffer flag variants.

## Risks and Test Signals

The conflict test assumes close detects stale remote state and does not overwrite. Passing signals are absent GCS objects before close, exact content after close, and ESTALE with preserved remote content on conflict.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/create_file_test.go -->
