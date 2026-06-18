# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/copy_object_test.go

## Purpose

This file verifies that copying files or directories into a read-only GCSFuse mount fails.

## Important APIs, Types, and Functions

`checkIfFileCopyFailed` attempts to copy a source file into the read-only subdirectory destination and expects an error. `TestCopyFile` and `TestCopyFileFromBucketDirectory` exercise file copies from root-level and directory-level files. `checkIfDirCopyFailed` expects `operations.CopyDir` to fail. `TestCopyDirectory` and `TestCopySubDirectory` exercise directory-copy attempts.

## Control Flow

Each test constructs source and destination paths under `setup.MntDir()` and the seeded `TestDirForReadOnlyTest` tree. It invokes the copy helper and reports an error if the copy unexpectedly succeeds.

## State and Persistence Behavior

The tests rely on read-only fixture data created by `readonly_test.go`. They should not create destination files or directories; success would indicate an unintended mutation of the mounted bucket.

## Dependencies and Integration Points

The file depends on `operations.CopyFile`, `operations.CopyDir`, `setup.MntDir`, `setup.GenerateRandomString`, and constants from the package harness. It runs under `--o=ro`, restrictive file/dir mode, persistent mount, and viewer-credential variants configured by the harness.

## Risks and Edge Cases

The helper only checks that an error occurred; it does not validate that the error is specifically read-only for copy operations. Destination names include randomness for files, reducing collisions, while directory destination paths are fixed by fixture layout.

## Test Signals

Passing tests mean copy operations return errors and therefore do not mutate the read-only mount. Unexpected success is a direct read-only enforcement regression.
