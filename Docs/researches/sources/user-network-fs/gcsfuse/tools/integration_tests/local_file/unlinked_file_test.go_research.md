<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/unlinked_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/unlinked_file_test.go

## Purpose

This file validates behavior for unlinked local files: stat/listing exclusion, writes and sync after unlink, and reusing the same file name after deletion before or after sync.

## Important APIs, Types, and Functions

Tests use `CreateLocalFileInTestDir`, `operations.RemoveFile`, `ValidateNoFileOrDirError`, `operations.WriteWithoutClose`, `operations.SyncFile`, `CloseFileAndValidateContentFromGCS`, and GCS not-found/content validators.

## Control Flow

The first tests remove open local files and verify stat fails, listings omit unlinked entries, writes to the open handle still succeed, sync does not upload, and close does not create GCS objects. `TestFileWithSameNameCanBeCreatedWhenDeletedBeforeSync` removes and closes an unsynced file, validates no upload, then creates a same-name file and persists new content. `TestFileWithSameNameCanBeCreatedAfterDelete` syncs a file, deletes it from mount/GCS, then recreates the same name and persists new content.

## State and Persistence Behavior

Unlink separates open file handle state from directory namespace state. Once unlinked, sync/close must not persist old content. Name reuse must allocate clean new local state without stale GCS or inode conflicts.

## Dependencies and Integration Points

It depends on local file package globals and shared operation/client helpers. It covers POSIX unlink semantics critical for temp-file workflows.

## Risks and Test Signals

The test intentionally ignores one close error after deleting before sync because flush currently returns error if unlinked. Passing signals are no GCS upload for unlinked handles and correct content for recreated names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/unlinked_file_test.go -->
