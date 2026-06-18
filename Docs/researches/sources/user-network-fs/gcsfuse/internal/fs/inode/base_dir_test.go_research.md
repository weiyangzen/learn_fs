<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir_test.go

## Purpose

This ogletest suite validates `baseDirInode`, the multi-bucket base directory inode.

## Important APIs, Types, and Functions

`BaseDirTest` owns a context, simulated clock, fake bucket manager, and locked `DirInode`. `fakeBucketManager` maps bucket names to `gcsx.SyncerBucket` instances and counts setup calls. `resetInode` constructs `NewBaseDirInode` with fixed attributes and locks it for tests.

Tests cover `ID`, `Name`, lookup counts, attributes with both clobber-check values, missing bucket lookup, successful lookup of bucket roots, cached bucket setup, kernel list-cache invalidation behavior, unsupported `ReadEntryCores`, and `IsTypeCacheDeprecated` true/false construction.

## Control Flow

Setup creates fake buckets `bucketA` and `bucketB`, constructs the base inode, and locks it. Lookup tests call `LookUpChild` and inspect returned `Core` fields. Cache tests check that repeated bucket lookups do not call `SetUpBucket` again for successful names.

## State and Persistence Behavior

The fake bucket manager's `setupTimes` counter and the base inode's internal bucket map are the observed mutable state. Tests unlock the inode in teardown. No durable files are written.

## Dependencies and Integration Points

The suite uses fake GCS buckets, `gcsx.NewSyncerBucket`, FUSE inode attributes, metadata type classification, no-op metrics, and ogletest assertions. It validates the base directory's implementation of the common `DirInode` contract.

## Risks and Edge Cases

The suite does not exercise every unsupported mutation stub, but it verifies listing unsupported behavior through `ReadEntryCores`. Cached lookup tests assume failed lookups are not cached and successful lookups are cached.

## Test Signals

Signals include expected root local/GCS names, bucket root type as `metadata.ImplicitDirType`, setup-call counts, `syscall.ENOTSUP` on listing, and boolean type-cache deprecation reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir_test.go -->
