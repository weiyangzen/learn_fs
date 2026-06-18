<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/managed_folders_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/managed_folders_test.go

## Purpose

This package setup file orchestrates managed-folder integration tests. It creates storage and control clients, temporary service-account credentials, default flag configurations for view/admin/empty-managed-folder suites, and runs tests across static, dynamic, and only-dir mounting modes.

## Important APIs, Types, and Functions

It defines `env` with context, clients, bucket type, config, mount function/directories, service account/key path, bucket/testDir, and testDirPath. `TestMain` uses setup/test-suite config, credentials helpers, static/dynamic/only-dir mounting utilities, and cleanup.

## Control Flow

Default configs include key-file-based view-permission flags, `--enable-empty-managed-folders`, and key-file/stat-cache-disabled admin-permission flags. `TestMain` initializes clients, creates credentials, substitutes `${KEY_FILE}` in flags, skips mounted-directory mode, sets up test bucket dir, then runs static tests. If successful, it runs dynamic mount with mountDir pointing to the bucket under the mount root. If still successful, it runs only-dir mount and cleans that prefix. Finally it cleans the main managed-folder test prefix and exits.

## State and Persistence Behavior

This file owns service-account credential file lifecycle, shared clients, mount mode globals, and bucket cleanup. Managed-folder resources and IAM bindings are mostly created/removed in helper and suite files.

## Dependencies and Integration Points

It integrates Cloud Storage data APIs, Storage Control managed-folder APIs, credential generation, key-file flag substitution, and all managed-folder suites.

## Risks and Test Signals

Temporary credentials must be removed and IAM changes cleaned even on failures. Multiple `m.Run()` phases mutate global mount state. Success is all selected suites passing in each mount mode and cleanup of GCS/control-plane resources.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/managed_folders_test.go -->
