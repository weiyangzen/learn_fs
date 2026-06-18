# sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/operations_test.go

## Purpose

This suite verifies basic directory and file operations on a requester-pays bucket mounted with a billing project and key file.

## Important APIs, Types, and Functions

`operationTests` is a `testify/suite` suite. `SetupSuite` creates the test directory under the mount, and `TearDownSuite` removes it. `TestDirOperations` creates, stats, renames, stats, and removes a directory. `TestFileOperations` creates a file with content, stats, renames, stats, and removes it.

## Control Flow

The directory test first asserts non-existence, creates a directory, verifies it is a directory, renames it, verifies old path absence and new path presence, removes it, and verifies absence. The file test follows the same lifecycle for a file created with random content.

## State and Persistence Behavior

The suite creates temporary objects under `RequesterPaysBucketTests` in the requester-pays bucket and removes them in test and suite flow. All operations should be billed to the configured billing project.

## Dependencies and Integration Points

It depends on standard `os`/`io/fs`, `filepath`, operations file creation helper, setup random string generation and permissions, and `testify` suite/assertions. It is mounted and configured by `setup_test.go`.

## Risks and Edge Cases

The suite validates functional operations but does not directly inspect billing attribution; missing billing project usually manifests as permission/billing errors. Random names avoid collisions. Cleanup uses `os.RemoveAll` through the requester-pays mount, so cleanup can fail if billing or credentials regress.

## Test Signals

Passing means create/stat/rename/delete work for files and directories on requester-pays buckets with the configured billing project and credentials. Failures often reveal missing `--billing-project`, bad key file, requester-pays enablement, or operation regressions.
