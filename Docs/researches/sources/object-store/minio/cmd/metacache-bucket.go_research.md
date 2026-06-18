# sources/object-store/minio/cmd/metacache-bucket.go

## Purpose

`metacache-bucket.go` manages all metacache listings for a single bucket. It creates, indexes, updates, cleans, clones, and deletes cache descriptors, and coordinates deletion of on-disk cache data under `.minio.sys`.

## Important APIs, Control Flow, And State

`bucketMetacache` stores the bucket name, `caches` by cache ID, `cachesRoot` by listing root, a mutex, and an `updated` flag. `newBucketMetacache` optionally deletes existing bucket cache data through an object layer implementing `deleteAllStorager`, then initializes maps. `findCache` validates bucket identity, returns an existing cache while updating `lastHandout`, returns a non-created `scanStateNone` cache when `Create` is false, or creates a new metacache from `listPathOptions`, indexes it by ID and root, and marks the bucket updated.

`cleanup` works on a cloned cache map, removing entries that are not worth keeping, have mismatched ID/bucket, or exceed `metacacheMaxEntries` with old `lastHandout` times beyond client wait. `updateCacheEntry` merges a metacache update into an existing entry. `cloneCaches` shallow-copies both indexes. `deleteAll` deletes all on-disk cache data and resets maps. `deleteCache` removes one cache from both indexes under lock, then calls `metacache.delete` outside the lock.

State is in memory plus persisted metacache objects deleted through the object layer. Dependencies include object-layer lookup, logger/console debug, map copy, sorting, and metacache lifecycle methods defined elsewhere.

## Risks And Test Signals

Risks include stale `cachesRoot` entries, cleanup deleting caches still needed by clients, shallow clone sharing metacache values with embedded mutable fields, object-layer absence, and lock ordering around deletes. `metacache-bucket_test.go` benchmarks `findCache` under many IDs and roots but does not assert cleanup/delete correctness.
