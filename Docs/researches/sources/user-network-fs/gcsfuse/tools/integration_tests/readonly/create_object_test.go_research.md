# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/create_object_test.go

## Purpose

This file verifies that creating files or directories through a read-only GCSFuse mount fails with a read-only filesystem error.

## Important APIs, Types, and Functions

`checkIfFileCreationFailed` calls `os.OpenFile` with `os.O_CREATE` and validates failure with `operations.CheckErrorForReadOnlyFileSystem`. `TestCreateFile` and `TestCreateFileInDirectory` cover root-level and nested file creation. `checkIfDirCreationFailed` calls `os.Mkdir` and validates read-only failure. `TestCreateDir` and `TestCreateSubDirectoryInDirectory` cover directory creation.

## Control Flow

Tests build paths under the mounted fixture tree, attempt creation, fail if creation succeeds, and validate the returned error. The file helper defers `file.Close()` even when `file` may be nil if creation failed, which depends on Go allowing method calls on nil interface values only if not reached through a nil concrete pointer; in practice this defer can panic if not guarded.

## State and Persistence Behavior

The expected behavior is no new objects or directories in GCS. All state comes from the read-only fixture seeded before tests.

## Dependencies and Integration Points

It uses standard `os`/`io/fs`, `operations.CheckErrorForReadOnlyFileSystem`, setup permissions, and package constants. It runs under the read-only harness's multiple mount and credential configurations.

## Risks and Edge Cases

The unconditional `defer file.Close()` in `checkIfFileCreationFailed` is risky when `os.OpenFile` returns a nil file with an error. The tests validate error type for create operations, which is stronger than copy tests. Directory mode uses `fs.ModeDir` rather than permission bits, but failure is expected before mode matters.

## Test Signals

Passing signal is read-only error on file and directory creation attempts. Any successful create is a mutation bug; any wrong error may indicate path resolution or permission behavior drift.
