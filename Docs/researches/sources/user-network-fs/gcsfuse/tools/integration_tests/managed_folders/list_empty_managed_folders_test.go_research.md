<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/list_empty_managed_folders_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/list_empty_managed_folders_test.go

## Purpose

This suite verifies that empty managed folders are visible when gcsfuse is mounted with `--enable-empty-managed-folders`. It checks managed folders, simulated folders, and files in one directory tree.

## Important APIs, Types, and Functions

`enableEmptyManagedFoldersTrue` is a Testify suite. Helper `createDirectoryStructureForEmptyManagedFoldersTest` creates two Storage Control managed folders, a simulated folder through the mount, and a file. `TestListDirectoryForEmptyManagedFolders` uses `filepath.WalkDir` and `os.ReadDir` to validate entries.

## Control Flow

Each test sets up `EmptyManagedFoldersTest`, creates two empty managed folder resources, creates an empty simulated folder and a file through the mounted filesystem, then walks the root test directory. At the root it expects four entries: the two empty managed folders as directories, simulated folder as directory, and file as non-directory. Inside each folder it expects zero entries.

## State and Persistence Behavior

The test creates managed-folder control-plane resources and mounted filesystem objects. Teardown deletes managed folders and cleans the GCS test directory. Empty managed folders have no object children but should persist as visible directory entries due to the mount flag.

## Dependencies and Integration Points

It depends on `testEnv.controlClient`, `testEnv.storageClient`, setup bucket/mount path translation, and shared client/operations helpers. It is selected by the managed-folder package default config run `TestEnableEmptyManagedFoldersTrue`.

## Risks and Test Signals

Listing order is assumed by index-based assertions. The test also assumes empty managed folder support is enabled and not hidden by bucket type behavior. Passing signal is root visibility of empty managed folders and empty listings inside them.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/list_empty_managed_folders_test.go -->
