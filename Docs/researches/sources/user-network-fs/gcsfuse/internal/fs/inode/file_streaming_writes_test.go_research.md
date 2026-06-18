# sources/user-network-fs/gcsfuse/internal/fs/inode/file_streaming_writes_test.go

## Purpose

This suite focuses on `FileInode` behavior when streaming writes are enabled through `bufferedwrites.BufferedWriteHandler`. It compares zonal/rapid buckets with non-zonal buckets, validates fallback from streaming to staged writes, and checks BWH lifecycle across write, sync, flush, truncate, unlink, and file-handle deregistration.

## Important APIs, Types, And Helpers

`FileStreamingWritesCommon` holds shared context, bucket, clock, backing object, and locked inode. `FileStreamingWritesTest` runs against a non-zonal fake bucket; `FileStreamingWritesZonalBucketTest` runs against a zonal fake bucket. `createInode` creates local or empty GCS-backed file inodes and installs a streaming write config. `createBufferedWriteHandler` calls `InitBufferedWriteHandlerIfEligible` and asserts BWH creation.

The suite directly exercises `IsUsingBWH`, `Write`, `Flush`, `Sync`, `SyncPendingBufferedWrites`, `Truncate`, `Attributes`, `SourceGeneration`, `SourceGenerationIsAuthoritative`, `Unlink`, and `DeRegisterFileHandle`. It defines `FakeBufferedWriteHandler` to force a generic BWH write error.

## Control Flow And State Behavior

Common tests verify BWH existence and reinitialization rules: flushing a zero-size object allows BWH to be created again, but flushing a nonzero object prevents streaming writes from being re-enabled for that object under the tested config. Negative truncation propagates an error.

Zonal tests assert source generation remains authoritative even while BWH exists, because zonal streaming writes can expose current object size through BWH and `SyncPendingBufferedWrites` may return a `MinObject`. Syncing pending writes in a zonal bucket promotes a local inode to non-local and updates `src.Size`. Non-zonal tests assert the opposite: pending BWH writes make source generation non-authoritative, `SyncPendingBufferedWrites` does not create a remote object, and `src.Size` remains unchanged until final flush.

Out-of-order write tests cover fallback. A sequential first write goes through BWH; an out-of-order second write finalizes current BWH data, clears BWH, creates staged temp content, and applies the second write through the temp-file path. Tests validate content holes, overwrites, mtime/size attributes, sync result, and clobber errors if the object is externally changed before fallback finalization.

## Dependencies And Integration Points

The suite uses fake GCS buckets, `gcsx.SyncerBucket`, `contentcache`, `bufferedwrites`, `gcsfuse_errors`, integration-test operations helpers, generated test strings, noop tracing/metrics, FUSE attrs, and semaphores. It is tightly integrated with `cfg.WriteConfig` and bucket type flags that decide rapid versus regional write behavior.

## Risks And Test Signals

Risks covered include BWH incorrectly surviving flush, staged fallback losing bytes or mtime, zonal sync failing to promote local files, non-zonal sync prematurely creating objects, unlink still uploading local data, clobbered flush overwriting remote state, and write-handle cleanup leaking BWH resources. The `FakeBufferedWriteHandler` test also verifies unexpected BWH errors are wrapped and returned without claiming GCS sync. Remaining risk is concurrency: these tests are single-threaded and do not stress global block semaphore contention except indirectly through configuration.
