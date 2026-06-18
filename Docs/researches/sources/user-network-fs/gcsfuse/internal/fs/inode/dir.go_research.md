<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/dir.go

## Purpose

This file defines the `DirInode` interface and implements `dirInode`, the primary GCS bucket-backed directory inode. It owns directory lookup, listing, type-cache interaction, implicit directory synthesis, HNS folder handling, child creation/deletion/rename, recursive deletion, local-file listing, kernel list-cache invalidation, and metadata-prefetch lifecycle hooks.

## Important APIs, Types, and Functions

`DirInode` extends `Inode` with child lookup, file/folder rename, descendant reads, paginated entry reads, creation/deletion of files, dirs, symlinks, recursive delete, type-cache updates, lookup locking, list-cache invalidation, prefetch cancellation, lifecycle context, unlink flags, and active writer counters. `dirInode` stores the bucket, clocks, optional `MetadataPrefetcher`, recursive context/cancel function, config flags, name, attributes, lock, lookup count, optional type cache, previous listing timestamp, HNS/symlink/unsupported-path flags, unlinked state, metadata TTL, and active-writer count.

Key helpers include `findExplicitInode`, `findExplicitFolder`, `findDirInode`, `lookUpConflicting`, `fetchCoreEntity`, `listObjectsAndBuildCores`, `readObjectsUnlocked`, `deletePrefixRecursively`, and `isBucketHierarchical`.

## Control Flow

`NewDirInode` validates directory names, builds a context derived from the parent directory context, creates the optional metadata prefetcher, and initializes legacy type cache unless deprecated. `LookUpChild` handles conflict suffixes, then optionally tries stat-cache-only lookup when type-cache deprecation is enabled, otherwise reads legacy type-cache hints. Unknown lookups trigger metadata prefetch and concurrently stat/list file and directory candidates with `errgroup`; directories win over files. Results update legacy type cache when enabled.

Listing flows through `ReadEntryCores` -> `readObjects` -> `listObjectsAndBuildCores`, which issues delimiter-based `ListObjects`, converts min objects and collapsed prefixes into `Core` records, handles unsupported paths, HNS folder cores, implicit directories, continuation tokens, and type-cache insertion. Mutation flows create objects/folders/symlinks, delete files/dirs, recursively delete prefixes, move objects, or rename folders while cancelling current prefetch and tracking active writers when stale prefetch could be harmful.

## State and Persistence Behavior

Persistent storage changes happen through the GCS bucket: object creation, copy, delete, move, folder create/delete/rename, and recursive delete. In-memory state includes lookup counts, type cache, previous listing timestamp, lifecycle cancellation context, unlinked flag, and active-writer count. Metadata prefetch can update cache asynchronously unless cancelled or blocked by active writers. HNS deleted folder inodes can be marked unlinked.

## Dependencies and Integration Points

The file is central to fs integration: it uses `cfg`, metadata cache types, `gcsx.SyncerBucket`, `locker`, logger, caching errors, storage GCS APIs, storage utilities, FUSE attributes/dirents, clocks, errgroups, and semaphores. `DirHandle` consumes `ReadEntries` and `ReadEntryCores`; higher-level filesystem operations consume creation/deletion/rename methods.

## Risks and Edge Cases

The largest risks are stale metadata from caches or prefetch, races with writers, HNS-vs-flat directory representation differences, conflict suffix lookup correctness, unsupported path filtering, and recursive delete closure/concurrency behavior. Directory entries must prefer directories over files for conflicts. Type-cache deprecation splits behavior between legacy type cache and stat-cache-only lookup. `readObjectsUnlocked` must avoid cache updates after context cancellation.

## Test Signals

Coverage is distributed across many files: implicit directory tests cover lookup/list conflict semantics and rmdir behavior; HNS tests cover folder listing/deletion/cache consistency; dir prefetcher tests cover async cache population and cancellation; dir handle tests cover listing conversion; base/core tests cover shared interfaces and `Core` classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir.go -->
