# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_test.go

Purpose: broad unit and integration-style tests for filesystem blob storage.

Important APIs/types/functions: tests include `TestFileStorage`, `TestFileStorageLongPath`, `TestFileStorageValidate`, `TestFileStorageTouch`, `TestFileStorageConcurrency`, `TestFilesystemStorageDirectoryShards`, retry/error handling tests for get/metadata/put/delete/list/touch/new, temp-file creation tests, `verifyBlobTimestampOrder`, `newMockOS`, and `verifyEmptyDir`.

Control flow: shared `blobtesting` suites exercise normal storage operations against temp directories. Other tests use mock OS implementations to inject read/stat/write/sync/close/rename/remove/list errors, verify retry limits, assert path validation, inspect directory sharding behavior, test touch threshold semantics, and confirm temp files are removed on failures.

State and persistence behavior: tests create real temp-directory blob trees and mock OS state. They verify atomic-temp-file behavior, mtime persistence, shard layout, cleanup after errors, and concurrent access behavior.

Dependencies/integration points: covers `fsImpl`, `fsStorage`, sharded storage, retry policy, `osInterface`, and generic blob testing. Risks/test gaps include platform-specific behavior split into other files, no crash/power-loss simulation around rename, and limited real filesystem error coverage. This is the main regression suite for local storage correctness.
