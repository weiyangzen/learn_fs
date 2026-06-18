# sources/sync-backup/kopia/repo/blob/gdrive/gdrive_storage_test.go

Purpose: live integration tests for Google Drive storage behavior and invalid setup.

Important APIs/types/functions: `TestCleanupOldData`, `TestGDriveStorage`, `TestGdriveStorageInvalid`, `gunzip`, `mustGetOptionsOrSkip`, `createTestFolderOrSkip`, and `deleteTestFolder`.

Control flow: helpers read credentials from environment, create or locate a Drive folder, construct `gdrive.Options`, run shared blob storage tests, clean old data, and validate invalid configuration failures.

State and persistence behavior: tests create real Google Drive files/folders and delete them during cleanup. File IDs and Drive metadata are external persistent state.

Dependencies/integration points: exercises Drive service creation, file upload/download/list/delete, file ID cache, and generic blob behavior. Risks include skipped coverage without credentials, Drive eventual consistency, quota/rate limits, and leftover files after failures. Because the provider is warned as not actively tested, these integration tests are especially important but environment-dependent.
