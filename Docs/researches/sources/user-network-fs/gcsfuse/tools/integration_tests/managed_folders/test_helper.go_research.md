<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/test_helper.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/test_helper.go

## Purpose

This helper file provides common managed-folder IAM, directory creation, cleanup, listing, and read-only error assertion utilities used by the managed-folder suites.

## Important APIs, Types, and Functions

It defines managed-folder constants, `FileInNonEmptyManagedFoldersTest`, `IAMPolicy`, and helpers `providePermissionToManagedFolder`, `revokePermissionToManagedFolder`, `createDirectoryStructureForNonEmptyManagedFolders`, `cleanup`, `listNonEmptyManagedFolders`, `copyDirAndCheckErrForViewPermission`, `copyObjectAndCheckErrForViewPermission`, `moveAndCheckErrForViewPermission`, and `createFileForTest`.

## Control Flow

IAM grant writes a temporary JSON policy and runs `gcloud storage managed-folders set-iam-policy`; revoke uses `gcloud storage managed-folders remove-iam-policy-binding` and tolerates missing binding/folder errors. Directory creation deletes any prior test prefix, creates a temp source file, creates two managed folders with Storage Control, copies one file into each, creates a simulated folder with a copied file, and copies one root file. Listing walks the mounted tree and validates the root has two managed folders, one simulated folder, and one file, with each child folder containing one file.

## State and Persistence Behavior

Helpers create IAM policy files, managed-folder resources, GCS objects, and mounted namespace state. Cleanup revokes IAM bindings, deletes managed folders, and removes GCS prefixes.

## Dependencies and Integration Points

It depends on `gcloud`, Cloud Storage and Storage Control clients, setup path translation, and shared operations. View-permission helpers normalize expected read-only filesystem errors for copy/move operations.

## Risks and Test Signals

The listing helper has index-based assumptions and a few error messages reference `objs[3]` even in child contexts, which could obscure diagnostics. IAM relies on external gcloud behavior. Passing signals are correct managed-folder visibility and read-only failures where expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/test_helper.go -->
