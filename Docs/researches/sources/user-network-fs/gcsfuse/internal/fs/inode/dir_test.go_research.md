# sources/user-network-fs/gcsfuse/internal/fs/inode/dir_test.go

## Purpose

This Go test suite exercises the non-HNS `DirInode` behavior in `gcsfuse/internal/fs/inode`. It validates how directory inodes resolve children from GCS object names, combine explicit directory marker objects with implicit-directory prefixes, expose FUSE dirents and `Core` records, mutate bucket contents, manage local unsynced child files, update type-cache state, and control list-cache invalidation. It is a high-signal regression suite for the directory layer that maps flat GCS object namespace semantics onto filesystem directory operations.

## Important APIs, Types, And Helpers

`DirTest` holds a context, `gcsx.SyncerBucket`, simulated clock, locked `DirInode`, and `metadata.TypeCache`. `resetInode` and `resetInodeWithTypeCacheConfigs` recreate a `NewDirInode` with configurable implicit dirs, nonexistent-type caching, managed-folder listing, cache size, and TTL. Helper methods `readAllEntries`, `readAllEntryCores`, `setSymlinkTarget`, `createLocalFileInode`, and `validateCore` drive repeated behaviors. The suite also defines `DirentSlice` for deterministic sorting of FUSE directory entries.

The tests cover public `DirInode` APIs including `ID`, `Name`, `Attributes`, `LookUpChild`, `ReadDescendants`, `ReadEntries`, `ReadEntryCores`, `CreateChildFile`, `CloneToChildFile`, `CreateChildSymlink`, `CreateChildDir`, `DeleteChildFile`, `DeleteChildDir`, `DeleteObjects`, `CreateLocalChildFileCore`, `LocalFileEntries`, `InsertFileIntoTypeCache`, `EraseFromTypeCache`, `ShouldInvalidateKernelListCache`, `InvalidateKernelListCache`, `Context`, and `Destroy`. They also reach into `dirInode.readObjectsUnlocked` and `dirInode.prefetcher` for behavior that is otherwise hard to observe.

## Control Flow And State Behavior

The central lookup flow tests priority among explicit directory marker objects (`name/`), regular files (`name`), symlink metadata on regular objects, conflict marker names, and implicit directories created by descendants. Explicit directory objects shadow regular files for normal lookup, while conflict-marker suffix lookup resolves the regular file side of a file/dir conflict. When `implicitDirs` is enabled, descendant objects can synthesize a directory `Core` without a backing `MinObject`; when disabled, those synthetic dirs are hidden.

Listing tests create a mix of explicit dirs, nonempty dirs, files, implicit dirs, symlinks, and unsupported paths. `ReadEntries` returns FUSE `Dirent` records and updates `prevDirListingTimeStamp`; `ReadEntryCores` returns typed `Core` records plus unsupported path prefixes. `readObjectsUnlocked` is tested with and without implicit dirs and with a start offset to ensure pagination/filtering logic remains stable while the inode lock is released.

Mutation tests verify creation with generation preconditions, cloning, symlink metadata including standard symlink content, deletion with generation/metageneration preconditions, recursive deletion of object subtrees, and local child file overlays. State persistence is mostly remote object state in the fake bucket, plus local in-memory inode state: lookup counts, type cache entries, local-file maps, list-cache timestamps, and lifecycle context cancellation.

## Dependencies And Integration Points

The suite uses `fake.NewFakeBucket`, `storageutil`, `gcsx.NewSyncerBucket`, `contentcache`, FUSE `fuseops`/`fuseutil`, `metadata.TypeCache`, `cfg.Config`, `semaphore.Weighted`, noop tracing/metrics, and `timeutil.SimulatedClock`. It implicitly tests integration between the inode layer and the storage layer's object create/update/delete/list semantics, including GCS generation preconditions and metadata-based symlink detection.

## Risks And Test Signals

Key risks covered are stale type-cache entries hiding a newly preferred object type until TTL expiry, incorrect precedence between file and directory objects, unsupported paths leaking into visible entries, local unsynced files appearing in the wrong parent, deletion incorrectly evicting or retaining cache state, and list-cache invalidation TTL regressions. Type-cache deprecation tests exercise a newer path that queries cached object data using `FetchOnlyFromCache` and falls back on cache misses. The tests do not execute real GCS behavior, so production risks remain around API pagination, managed folder support in real buckets, and concurrency under lock handoff.
