<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/rename_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/rename_test.go

## Purpose

This file tests rename behavior for local unsynced files and directories containing local files. It distinguishes supported file rename from unsupported directory rename while unsynced files are present, and verifies directory rename succeeds after sync.

## Important APIs, Types, and Functions

`verifyRenameOperationNotSupported` checks for `operation not supported`. Tests use `os.Rename`, local creation/write helpers, GCS validators, and `operations.Copy/Move`-adjacent constants such as `NewDirName`.

## Control Flow

`TestRenameOfLocalFile` creates and writes an unsynced local file, renames it, and expects the new GCS object to contain the data and the old name to disappear. `TestRenameOfDirectoryWithLocalFileFails` creates a directory with one GCS file and one unsynced local file, attempts directory rename, expects unsupported, writes more, then closes and validates the local file under its original directory. `TestRenameOfLocalFileSucceedsAfterSync` syncs first then renames the file. `TestRenameOfDirectoryWithLocalFileSucceedsAfterSync` reuses the failing setup, then renames after sync and validates both objects under the new directory.

## State and Persistence Behavior

Local file rename can force persistence under the new name. Directory rename is blocked while local unsynced children exist, then becomes a remote object move after children are synced.

## Dependencies and Integration Points

It depends on local-file package state and shared client/operations helpers. It exercises rename-dir-limit configurations from package setup.

## Risks and Test Signals

The expected unsupported error string is platform/path dependent. Passing signals are correct object movement, no overwrite of old names, and protection against renaming directories with unsynced children.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/rename_test.go -->
