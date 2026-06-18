<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/remove_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/remove_dir_test.go

## Purpose

This file tests removing directories that contain unsynced local files, alone or mixed with already synced GCS files. It verifies unlinked open files do not upload after their parent directory is removed.

## Important APIs, Types, and Functions

Tests use `operations.CreateDirectory`, `CreateLocalFileInTestDir`, `CloseFileAndValidateContentFromGCS`, `operations.RemoveDir`, `operations.ValidateNoFileOrDirError`, `operations.WriteWithoutClose`, and GCS object-not-found validators.

## Control Flow

`TestRmDirOfDirectoryContainingGCSAndLocalFiles` creates an explicit directory with one synced file and one open local file, removes the directory, verifies the path disappears, writes to the unlinked open handle, closes it successfully, and checks neither local nor synced objects remain in GCS. `TestRmDirOfDirectoryContainingOnlyLocalFiles` removes a directory with two open local files and validates closing both handles does not create GCS objects.

## State and Persistence Behavior

Directory removal unlinks open local files from namespace state. Their handles can still be written/closed, but close must not persist deleted entries. Synced entries and directory markers are deleted from GCS.

## Dependencies and Integration Points

It relies on local file helpers and shared operations for POSIX remove and validation. It covers behavior important for applications that delete trees while files are still open.

## Risks and Test Signals

The tests assume `operations.RemoveDir` handles non-empty directory semantics for this mounted filesystem. Passing signals are namespace removal, safe writes to unlinked handles, no post-close GCS creation, and deletion of synced contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/remove_dir_test.go -->
