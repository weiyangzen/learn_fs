# sources/user-network-fs/gcsfuse/internal/fs/inode/file_mock_bucket_test.go

## Purpose

This suite tests `FileInode` against a testify mock bucket so it can assert exact storage calls and request choices that the fake bucket cannot expose. It focuses on clobber detection, forced metadata fetches, upload size validation, attribute refresh for remote appends, and streaming write initialization differences between zonal/rapid and regional buckets.

## Important APIs, Types, And Helpers

`FileMockBucketTest` owns a mock `storagemock.TestifyMockBucket`, simulated clock, optional backing `MinObject`, and locked `FileInode`. `createLockedInode` builds either a local file or an empty GCS-backed file using `gcsx.NewSyncerBucket`; for local files it creates an empty temp file immediately. `createGCSBackedFileInode` creates a locked non-local inode around a supplied min object for attributes-focused tests.

The test targets `Flush`, `Sync`, `Attributes`, and `InitBufferedWriteHandlerIfEligible`. It also reaches source generation state and uses `gcsfuse_errors.FileClobberedError` to classify failures.

## Control Flow And State Behavior

Local-file flush is expected to create an object without a preceding `StatObject`, because no remote source exists. Synced empty-file flush is expected to stat GCS first, including extended attributes, before creating/replacing the object. Upload size validation is checked by mocking `CreateObject` to return a size smaller than the temp-file size; `Flush` must fail and report the expected and actual sizes.

Clobber tests dirty an inode, then mock `StatObject` to return either the same generation/metageneration with larger size or a different generation. The first path models remote append at same generation and should become `FileClobberedError` with the remote-append message during sync. The second path validates classic generation/metageneration mismatch clobbering.

Attribute tests check the non-sync path where `Attributes(..., true)` sees remote size growth at the same generation. In that case the inode updates `src.Size` and `attrs.Size` rather than reporting `Nlink` zero. A no-change attribute test confirms a newer timestamp with same size/generation does not overwrite cached source attributes.

## Dependencies And Integration Points

The suite depends on `storagemock.TestifyMockBucket`, `mock.AnythingOfType` request matching, `storageutil`, `gcsx.SyncerBucket`, `contentcache`, `cfg.WriteConfig`, semaphores, noop tracing/metrics, and FUSE attrs. It complements fake-bucket tests by verifying storage call contracts and `FetchLatestGcsObject`/BWH initialization decisions.

## Risks And Test Signals

Important risks covered are accidental remote stat on local file flush, missing remote stat on synced-file overwrite, accepting partial uploads, treating remote append size growth as a normal sync, and fetching stale metadata for rapid append paths. The zonal append test asserts no `StatObject` for rapid appends, while zonal overwrite and regional writes must fetch metadata. Remaining risk is that mock expectations may not capture full request fields unless matched strictly.
