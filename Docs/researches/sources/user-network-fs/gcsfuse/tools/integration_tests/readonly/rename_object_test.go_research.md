# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/rename_object_test.go

## Purpose

This file verifies that file and directory rename operations fail on a read-only mount and that source objects remain intact while destination paths are not created.

## Important APIs, Types, and Functions

`checkIfRenameFileFailed` calls `operations.RenameFile`, validates read-only failure, stats the old path, and ensures the new path does not exist. `checkIfRenameDirFailed` does the same for directories. Tests cover root file, nested file, subdirectory file, top-level directory, and subdirectory renames, with extra child-listing checks for directory cases.

## Control Flow

Each test constructs old and new paths under the fixture tree, invokes the helper, and for directory tests reads the original directory to ensure children remain present and correct.

## State and Persistence Behavior

Expected state is no mutation: original files/directories remain, destination names are absent, and child entries are unchanged. Directory tests explicitly verify source subtree preservation after failed rename.

## Dependencies and Integration Points

It depends on operations rename helpers, read-only error validation, `os.Stat`, `os.ReadDir`, setup paths, and fixture constants. It is part of the read-only package matrix.

## Risks and Edge Cases

Directory listing checks assume sorted order and exact fixture counts. Error validation is strong for rename helpers. If rename partially mutates before failing, the explicit old/new stat and listing assertions should catch it.

## Test Signals

Passing signal is read-only errors on all rename attempts plus preserved old paths and absent new paths. Failures indicate read-only enforcement gaps or partial-rename rollback problems.
