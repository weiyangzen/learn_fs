# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/delete_object_test.go

## Purpose

This file verifies that deleting files, directories, subdirectories, or the mount root through a read-only mount fails.

## Important APIs, Types, and Functions

`checkIfObjDeletionFailed` calls `os.RemoveAll` and requires a non-nil error validated by `operations.CheckErrorForReadOnlyFileSystem`. Tests cover deleting the main fixture directory, root file, subdirectory, nested file, and all objects via the mount root.

## Control Flow

Each test builds the target path from `setup.MntDir()` and fixture constants, calls the helper, and fails if deletion succeeds.

## State and Persistence Behavior

The expected behavior is preservation of all seeded fixture objects and directories. No new state is created. Because `os.RemoveAll` can return nil for non-existent paths, fixture correctness is important for meaningful coverage.

## Dependencies and Integration Points

It depends on standard `os`, setup constants, and read-only error validation from operations. It is part of the broader read-only package matrix.

## Risks and Edge Cases

`os.RemoveAll` semantics differ from simple `Remove`; if paths are absent, success may be ambiguous. The tests rely on fixture paths existing. Recursive delete of the mount root is a high-impact operation, so a regression could wipe test data if read-only enforcement fails.

## Test Signals

Passing means delete attempts are rejected with read-only filesystem errors. Fixture-preservation checks in other tests add indirect confidence that failed deletes did not remove source data.
