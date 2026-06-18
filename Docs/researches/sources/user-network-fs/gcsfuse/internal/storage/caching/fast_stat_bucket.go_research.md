## sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket.go

### Purpose
`fast_stat_bucket.go` implements a caching `gcs.Bucket` wrapper for stat and folder metadata. It caches positive object/folder entries, negative misses, implicit directories, and listing-derived metadata while invalidating entries after mutations.

### Important APIs, Types, And Functions
`CacheMissError` marks cache-only lookup misses. `NewFastStatBucket` constructs `fastStatBucket`. Key helpers include `insertMultiple`, `insertListing`, `insertMultipleMinObjects`, `eraseEntriesWithGivenPrefix`, `insertHierarchicalListing`, `insert`, `insertMinObject`, `insertFolder`, negative-entry helpers, `invalidate`, `lookUp`, and `lookUpFolder`. Bucket methods wrap object, folder, list, stat, read, write, update, delete, move, and multi-range operations.

### Control Flow
Stat first panics on invalid requests for extended attrs without GCS fetch, then bypasses cache when forced, otherwise returns positive cache entries, converts negative entries to `NotFoundError`, optionally returns `CacheMissError`, or fetches from GCS and inserts results. Listings populate cache differently for hierarchical buckets, deprecated type-cache mode, and normal mode. Mutating operations invalidate affected names after wrapped calls, and insert new objects/folders on success. Deletes add negative entries on success and invalidate on precondition/not-found errors. Folder operations have parallel folder cache/negative-entry behavior. Context cancellation is checked after acquiring the mutex before inserting listing results to avoid stale cache updates.

### State, Persistence, And Dependencies
State is protected by `mu` and stored in `metadata.StatCache` with primary and negative TTLs based on an injected clock. Persistent remote state remains in the wrapped bucket. Dependencies include metadata cache, storageutil conversions, logger, `gcs` types, `timeutil.Clock`, context, and string suffix checks for directory markers.

### Integration Points
This wrapper sits between filesystem metadata lookups and the underlying bucket, reducing GCS stat calls. It integrates with HNS folder APIs, implicit directory behavior, appendable writer precondition cache invalidation, and force-fetch/fetch-only cache request flags.

### Risks
Cache coherency is the main risk. Incorrect invalidation after failed writes, stale listings after context cancellation, or wrong negative-entry TTLs can surface stale file/folder existence. `StatObject` panics for one invalid flag combination, so callers must respect request invariants. For hierarchical listings, zero-byte objects ending in `/` are excluded as folders while collapsed runs become folder entries; malformed prefixes only log errors.

### Test Signals
This shard does not include fast-stat tests, but the code has explicit paths that should be tested: positive/negative object and folder cache hits, fetch-only cache misses, force-fetch with extended attrs, listing insertion in HNS and implicit-dir modes, mutation invalidation, appendable takeover precondition invalidation, context-canceled listing suppression, and rename prefix erasure.
