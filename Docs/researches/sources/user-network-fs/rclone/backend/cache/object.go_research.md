# sources/user-network-fs/rclone/backend/cache/object.go

## Purpose
`object.go` defines the cache backend's `fs.Object` wrapper. It persists object metadata, lazily refreshes stale entries, routes reads through cache handles, and keeps temp-upload objects distinct from source objects.

## Important APIs, Types, And Control Flow
`Object` stores the wrapped object, parent FS, cache FS, normalized name/path, cached modtime/size/storable/type/timestamp, cached hash map, and refresh mutex. `NewObject` creates a placeholder and switches to `objectPendingUpload` when the persistent pending queue contains the absolute path. `ObjectFromOriginal` wraps a source object and populates metadata via `updateData`. `refresh` checks info-age and notification flags, while `refreshFromSource` reloads from either temp FS or wrapped FS. `Open` refreshes, creates a `Handle`, applies seek/range options, and returns a limited reader. `Update`, `Remove`, `SetModTime`, and `Hash` update source state and cache state.

## State And Persistence
Objects serialize to Bolt as JSON records under their parent directory bucket. `persist` writes metadata through `Persistent.AddObject`; `RemoveObject` clears object metadata and chunks. Hashes are cached lazily in `CacheHashes`. Temp-upload state is driven by `Persistent.SearchPendingUpload`.

## Dependencies And Integration Points
The type integrates `fs.Object`, `hash.Type`, `readers.NewLimitedReadCloser`, background upload pause/play controls, persistent cache expiration, upstream change notifications, and temp FS routing.

## Risks And Test Signals
Risks include stale object metadata when wrapped changes are not notified, concurrent refresh/update behavior, operations on started temp uploads, hash cache invalidation, and correct path cleaning under crypt wrappers. Tests exercise object not found, wrapped object discovery, direct wrapped mutations, double updates, temp-file operations, uploading-file blockers, and cache-write chunk invalidation.
