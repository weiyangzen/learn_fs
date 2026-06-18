<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/view_permissions_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/view_permissions_test.go

## Purpose

This suite validates managed-folder behavior when the effective permission is view-only. It ensures listing succeeds while create, delete, copy, and move operations fail with read-only filesystem errors.

## Important APIs, Types, and Functions

`managedFoldersViewPermission` embeds Testify suite and stores flags. Test methods use `listNonEmptyManagedFolders`, `os.Create`, `os.Remove`, `os.RemoveAll`, `moveAndCheckErrForViewPermission`, `copyDirAndCheckErrForViewPermission`, and `copyObjectAndCheckErrForViewPermission`. The suite function applies and revokes IAM roles using `creds_tests`.

## Control Flow

`TestManagedFolders_FolderViewPermission` grants objectViewer on the bucket, creates the non-empty managed-folder structure, runs the suite with nil managed-folder permissions, grants objectViewer on each managed folder, waits 60 seconds, then runs the suite again. Tests list non-empty managed folders and attempt object creation, object deletion, non-empty managed-folder deletion, moving/copying folders, moving/copying objects within a managed folder, and moving/copying objects out of managed folders; all writes are expected to fail read-only.

## State and Persistence Behavior

State includes bucket and managed-folder IAM bindings, managed-folder resources, GCS files, and mounted namespace attempts. View permission should permit reads/lists but not persist namespace mutations.

## Dependencies and Integration Points

It depends on helpers in `test_helper.go`, credential utilities, and package setup for key-file mounting. It exercises authorization through the service account key passed to gcsfuse.

## Risks and Test Signals

Fixed IAM propagation sleep can be flaky. If gcsfuse maps authorization failures to different errors, read-only checks may fail. Passing signals are successful listing and consistent read-only errors for all mutating operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/view_permissions_test.go -->
