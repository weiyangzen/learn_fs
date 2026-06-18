<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache.go -->
# sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache.go

## Purpose
This file implements the metadata `StatCache` interface on top of the shared LRU cache. It caches positive object entries, implicit directories, folder resources, and negative entries with expirations, while supporting bucket-name namespacing for dynamic mounts and prefix invalidation.

## Important APIs and types
`StatCache` exposes `Insert`, `InsertImplicitDir`, `AddNegativeEntry`, `Erase`, `LookUp`, `InsertFolder`, `LookUpFolder`, `AddNegativeEntryForFolder`, and `EraseEntriesWithGivenPrefix`. `NewStatCacheBucketView` wraps a shared `lru.Cache` with an optional bucket prefix. Internal `entry` stores either a `*gcs.MinObject`, `*gcs.Folder`, expiration, and an `implicitDir` flag.

## Control flow and state behavior
Object insertion avoids replacing a newer positive entry with older generation or metageneration data, but always replaces negative entries and equivalent-generation entries for freshness. Implicit directory insertion skips if an explicit object entry already exists, preventing inferred placeholders from overwriting real metadata. Negative entries store nil object/folder pointers. Lookup reads from LRU, expires stale entries by erasing them, returns nil metadata for negative hits, and synthesizes a minimal `MinObject` for implicit directory hits.

## State and persistence behavior
The cache is in-memory, expiration-driven, and LRU-bounded through `entry.Size`. Size estimation uses unsafe struct size, nested object/folder size helpers, a fixed positive-object overhead, and a heap-to-RSS conversion factor. Bucket views namespace keys by concatenating bucket name, bucket creation time from `FileInfoKey` analogs is not used here, and object path joining deliberately avoids `path.Join` to preserve trailing slash distinctions.

## Dependencies and integration points
The implementation depends on `lru.Cache`, GCS metadata types, logger, util size-estimation helpers, math/time, and prefix erasure from LRU. It is used by filesystem metadata paths that need to cache object existence, listings, folders, and managed-folder-like resources.

## Risks and edge cases
`AddNegativeEntryForFolder` stores an entry with `f:nil`, indistinguishable in shape from object negative entries except by key namespace chosen by caller. `InsertFolder` does not apply generation/metageneration replacement checks like object insert does. Prefix erasure delegates to raw string prefix matching and must be called with a prefix that respects bucket-view key construction and trailing slash semantics.

## Test signals
No tests are in this work item, but expected signals would include stale-generation rejection, negative-to-positive replacement, implicit directory non-overwrite, expiration erase-on-lookup, bucket namespace isolation, folder entry lookup, and prefix invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache.go -->
