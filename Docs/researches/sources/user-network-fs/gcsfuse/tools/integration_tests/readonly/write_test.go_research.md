# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/write_test.go

## Purpose

This file verifies that write and append attempts fail on read-only mounts for existing and non-existing files.

## Important APIs, Types, and Functions

`checkIfFileFailedToOpenForWrite` calls `operations.WriteFile` and validates read-only error. Tests cover existing files at root, directory, and subdirectory. `checkIfNonExistentFileFailedToOpenForWrite` expects a not-found error for writes to missing paths. `checkIfFileFailedToOpenForAppend` calls `operations.WriteFileInAppendMode` and validates read-only error. `checkIfNonExistentFileFailedToOpenForAppend` expects not-found for missing append targets.

## Control Flow

Each test constructs a mounted path, attempts write or append, and validates either read-only or not-found error depending on whether the target exists.

## State and Persistence Behavior

Expected behavior is no content change and no file creation. Existing fixture files should remain unchanged, and missing paths should remain absent.

## Dependencies and Integration Points

It depends on `operations.WriteFile`, `operations.WriteFileInAppendMode`, read-only and not-found validators, setup paths, and fixture constants. It is central to the read-only enforcement suite.

## Risks and Edge Cases

For non-existent write/append attempts, the expected error is not-found rather than read-only; this encodes current path resolution semantics. The tests do not re-read existing file content after failed writes, relying on errors as the main signal.

## Test Signals

Passing means existing writes/appends are rejected as read-only and missing writes/appends are rejected as not-found. Unexpected success indicates a serious mutation bug.
