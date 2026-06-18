# sources/user-network-fs/gcsfuse/internal/fs/inode/file_test.go

## Purpose

`file_test.go` is the primary regression suite for `FileInode`. It runs the same suite over non-zonal, zonal, and Pirlo rapid bucket modes and validates file identity, attributes, reads, staged writes, streaming-write eligibility, sync/flush persistence, local file promotion, truncate semantics, mtime behavior, clobber handling, content encoding, reader updates, unlink state, and file-handle accounting.

## Important APIs, Types, And Helpers

`FileTest` owns a fake bucket, simulated clock, initial object contents, backing `MinObject`, locked `FileInode`, and target `gcs.BucketType`. `createInodeWithLocalParam`, `createInodeWithEmptyObject`, and `createBufferedWriteHandler` set up the main test variants. `validateMrdInstanceMinObject` and `validateMrdWrapperMinObject` assert rapid-bucket reader wrappers receive copied, up-to-date min objects after inode state changes. `getWriteConfig` and `getWriteConfigWithEnabledRapidAppends` produce streaming write configs.

The suite covers `SourceGeneration`, `SourceGenerationIsAuthoritative`, `SyncPendingBufferedWrites`, `Attributes`, `Read`, `Write`, `Truncate`, `Destroy`, `Sync`, `Flush`, `SetMtime`, `CreateEmptyTempFile`, `InitBufferedWriteHandlerIfEligible`, `Unlink`, `UpdateSize`, `RegisterFileHandle`, and BWH support decisions.

## Control Flow And State Behavior

The staged read/write tests verify that reads fault content into a temp file, writes and truncates mutate only local content until sync/flush, and sync/flush creates a new GCS generation with `gcsfuse_mtime` metadata and updated reader wrappers. Local file tests create an inode with no backing object, stage empty or written content locally, and verify sync/flush promotes it to non-local with persisted object metadata. Truncate-up and truncate-down tests confirm size, zero-fill behavior, and mtime propagation.

Mtime tests split three paths: metadata update without faulting content, metadata update after clean content is faulted in, and local temp-file mtime update when content is dirty or the inode is local. Precondition and not-found errors from remote metadata updates are treated as unlinked/clobbered no-ops. Unlinked files ignore `SetMtime`. Attribute tests verify `gcsfuse_mtime` outranks `goog-reserved-file-mtime`.

Streaming tests inside this file validate eligibility for new/empty files and rapid appends to unfinalized objects, rejection for nonempty finalized objects, BWH size reflection in attributes/source generation, reading after flush, invalid config errors, and truncate-down fallback that finalizes then switches paths. Rapid append coverage confirms appending to an unfinalized zonal object writes expected content.

## Dependencies And Integration Points

The suite depends on fake GCS storage, `storageutil`, `gcsx.SyncerBucket`, `contentcache`, `gcsfuse_errors`, `cfg`, `util.OpenMode`, noop metrics/tracing, semaphores, FUSE attrs, and simulated time. It verifies integration with rapid bucket MRD reader state, GCS generation/metageneration preconditions, metadata conventions, and buffered-write configuration.

## Risks And Test Signals

The strongest signals are around preserving source generation until sync, rejecting clobbered sync/flush/openReader paths, validating uploaded size, ensuring reader wrappers are updated after object replacement, and correctly distinguishing sync from flush for streaming writes. Remaining risks include real storage API differences from the fake bucket, interaction with persistent disk content cache beyond basic construction, and multi-handle concurrency beyond counter increments/decrements.
