# sources/user-network-fs/rclone/backend/cache/directory.go

## Purpose
`directory.go` defines the cached directory wrapper used by the cache backend to persist directory metadata and satisfy `fs.Directory`.

## Important APIs, Types, And Control Flow
`Directory` stores an optional wrapped `fs.Directory`, the owning `*Fs`, normalized name and absolute directory path, cached modtime, size, item count, type string, and cache timestamp. `NewDirectory` creates a timestamped shallow directory for a remote. `ShallowDirectory` derives `Dir` and `Name` from `path.Join(f.Root(), remote)`. `DirectoryFromOriginal` converts a source `fs.Directory` into a cached record using source modtime, size, items, and current cache timestamp. Methods implement `Fs`, `String`, `Remote`, internal `abs`, `ModTime`, `Size`, `Items`, and `ID`.

## State And Persistence
Instances are JSON-serializable except for `Directory` and `CacheFs`, which are excluded. `Persistent.AddDir` and `AddBatchDir` store them as the `"."` key inside nested Bolt buckets. `CacheTs` drives info-age invalidation.

## Dependencies And Integration Points
The type depends on `fs.Directory`, `context`, `path`, and the cache backend's `cleanPath`/`cleanRootFromPath` semantics. Directory records are created by listing, mkdir, expiration, notification, and temp-upload cleanup paths.

## Risks And Test Signals
Path normalization and root trimming are the main correctness risks, especially for root directories and nested cache roots. `ID` returns empty if the original directory is absent, so consumers cannot rely on IDs for cached-only directories. Test signals appear in internal listing, mkdir/rmdir, notification, and nested-directory regression tests.
