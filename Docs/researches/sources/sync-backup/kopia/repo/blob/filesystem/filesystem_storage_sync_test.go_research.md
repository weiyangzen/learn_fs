# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_storage_sync_test.go

Purpose: tests that filesystem writes sync data before close and surface sync errors.

Important APIs/types/functions: `verifySyncBeforeCloseFile`, `mockOSForSyncTest`, `TestPutBlob_SyncBeforeClose`, and `TestPutBlob_FailsOnSyncError`.

Control flow: the custom write file tracks whether `Sync` happens before `Close` and can inject sync failures. The mock OS returns that file from `CreateNewFile`. Tests call `PutBlobInPath` and assert successful ordering or expected error behavior.

State and persistence behavior: state is held in mock file flags rather than real durable writes. The tested persistence invariant is important: data is flushed before a temp file is closed and renamed.

Dependencies/integration points: targets `fsImpl.createTempFileWithData` and write error cleanup paths. Risks/test gaps include no real fsync durability guarantee across filesystems and no directory fsync check after rename. The test strongly pins the current temp-file write/sync/close order.
