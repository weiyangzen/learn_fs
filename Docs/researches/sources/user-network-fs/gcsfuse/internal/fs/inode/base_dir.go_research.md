<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir.go

## Purpose

This file implements `baseDirInode`, a read-only root-like directory for multi-bucket mounts. Its children are bucket roots resolved lazily by name through a `gcsx.BucketManager`; listing all buckets is intentionally unsupported.

## Important APIs, Types, and Functions

`baseDirInode` stores inode ID, root name, attributes, lookup count, a bucket manager, a cache of initialized buckets by name, a metric handle, and a type-cache deprecation flag. `NewBaseDirInode` constructs it and initializes lookup count and lock. It implements the `DirInode` interface with locking, lookup count, attributes, child lookup, listing stubs, mutation stubs, cache hooks, rename/delete stubs, prefetch hooks, context hooks, and writer counters.

`LookUpChild` is the main supported operation: it checks the local bucket map, calls `bucketManager.SetUpBucket(ctx, name, true, metricHandle)` on miss, caches the resulting `SyncerBucket`, and returns a `Core` for the bucket root.

## Control Flow

Base-dir lookups take an exclusive lock via `LockForChildLookup` because the bucket cache may be mutated. Attribute calls return static directory attributes with `Nlink=1`. `ReadEntries` and `ReadEntryCores` return `syscall.ENOTSUP` because enumerating accessible buckets is expensive and unsupported. Mutating operations return `fuse.ENOSYS`.

## State and Persistence Behavior

The inode caches successfully opened buckets in memory for the mount lifetime. Lookup counts track kernel references. No directory listing cache, type cache, prefetch context, local file entries, or active-writer state is meaningful for the base directory. There is no persistence beyond the bucket manager's external behavior.

## Dependencies and Integration Points

The file integrates with `gcsx.BucketManager`, `gcsx.SyncerBucket`, `metrics.MetricHandle`, FUSE inode attributes and errors, GCS object/folder types, and the common `DirInode` interface. It is used for dynamic or multi-bucket root mounts where child names are bucket names.

## Risks and Edge Cases

Because listing is unsupported, callers must handle `ENOTSUP` for directory reads. Bucket setup failures propagate directly. The constructor ignores the supplied `name` for stored name and sets `NewRootName("")`, which is intended for the base root. Mutation stubs must remain consistently unsupported to avoid accidental bucket creation/deletion semantics.

## Test Signals

The paired tests verify ID/name, lookup count, attributes, successful and failed bucket lookup, bucket setup caching, unsupported `ReadEntryCores`, list-cache invalidation default, and type-cache deprecation flag reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir.go -->
