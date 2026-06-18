# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/failure_during_file_sync_test.go

## Purpose

This suite validates behavior when credentials allow reading/listing but not object creation. It ensures failed file syncs do not leave phantom entries in directory listings.

## Important APIs, Types, and Functions

`readOnlyCredsTest` stores the mounted test directory path. `assertFailedFileNotInListing` reads the directory and requires it to be empty. `assertFileSyncFailsWithPermissionError` closes a file handle and requires a permission-denied error. `TestEmptyCreateFileFails_FailedFileNotInListing` and `TestNonEmptyCreateFileFails_FailedFileNotInListing` cover empty and non-empty create/sync failures. `TestReadOnlyTest` runs the suite.

## Control Flow

Each test opens a file with create/truncate flags. In zonal bucket runs, open itself is expected to fail with permission denied. In other runs, open can return a local file handle, and the permission failure is expected on close/sync; the non-empty test writes content before close. Both tests then list the directory and require no entries.

## State and Persistence Behavior

The test directory exists before credentials are reduced. Failed files may exist transiently in local write staging, but must not persist in GCS or listings after failure. The suite reads the mounted directory to verify no ghost state.

## Dependencies and Integration Points

It depends on the `readonly_creds` harness, `operations.WriteWithoutClose`, setup flags, and credential-mode execution using objectViewer permissions. It uses `testify` assertions for zonal-specific behavior.

## Risks and Edge Cases

Behavior differs between zonal and non-zonal buckets, so assertions branch on `setup.IsZonalBucketRun`. Permission errors are checked by substring. If local staging cleanup is asynchronous, immediate listing could be timing-sensitive, though the current tests do not retry.

## Test Signals

Passing means create/sync fails with permission denied and the failed file is absent from listings for both empty and non-empty writes. Failures indicate credential enforcement, staging cleanup, or listing consistency bugs.
