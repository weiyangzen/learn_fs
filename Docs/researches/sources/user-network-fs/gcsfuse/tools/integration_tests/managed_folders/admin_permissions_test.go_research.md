<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/admin_permissions_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/admin_permissions_test.go

## Purpose

This suite tests managed-folder operations when effective permissions include admin rights at the managed-folder level or bucket level. It covers create, delete, copy, move, and listing behavior across several bucket/managed-folder permission combinations.

## Important APIs, Types, and Functions

`managedFoldersAdminPermission` tracks `bucketPermission`, `managedFoldersPermission`, and flags. Setup mounts, creates the non-empty managed-folder structure, optionally grants managed-folder IAM roles, and waits for propagation. Tests use `os.Create`, `os.Remove`, `os.RemoveAll`, `operations.CopyFile`, `operations.CopyDir`, `operations.Move`, `operations.StatFile`, and `listNonEmptyManagedFolders`.

## Control Flow

For each flag set, `TestManagedFolders_FolderAdminPermission` first grants bucket admin permission, then iterates permission cases: bucket admin with nil/view/admin managed-folder roles and bucket view with managed-folder admin. It adjusts bucket IAM when needed, sets bucket/testDir path for the mount mode, and runs the suite. Test methods validate object creation/deletion, managed-folder deletion hiding empty folders, copy/move of objects and directories, and listing. Directory copy/move is expected to fail read-only when bucket permission is view despite managed-folder admin.

## State and Persistence Behavior

State includes IAM bindings on buckets and managed folders, managed folder resources created through the Storage Control API, copied test objects, and mounted namespace mutations. Cleanup revokes bindings and removes resources, with special handling when bucket view permission prevents broad cleanup.

## Dependencies and Integration Points

It depends on `test_helper.go`, credentials helpers, Cloud Storage/Storage Control clients, and package mount setup. It only runs static mount via `setup.RunTestsOnlyForStaticMount`.

## Risks and Test Signals

IAM propagation is handled by a fixed 60-second sleep and can still be flaky. Permission union semantics are central. Passing signals are successful admin operations where allowed and read-only failures where bucket-level view blocks broader directory operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/admin_permissions_test.go -->
