# sources/user-network-fs/rclone/backend/cache/storage_persistent.go

## Purpose
`storage_persistent.go` implements the cache backend's durable metadata and chunk store using BoltDB plus filesystem chunk files.

## Important APIs, Types, And Control Flow
`GetPersistent` returns a singleton `Persistent` per DB path. `connect` creates the chunk data directory, opens Bolt, optionally purges, and creates root, root timestamp, data timestamp, and pending-upload buckets. Directory/object methods store directory metadata under nested buckets and object metadata as JSON key values. Chunk methods write chunk files under `dataPath/objectAbs/offset` and timestamp them in `DataTsBucket`. Cleanup computes total chunk size and deletes oldest timestamped chunks until under limit. Stats walks buckets and timestamp indexes. Pending upload methods add, search, claim, roll back, remove, update, list by dir, purge for tests, and reconcile queue records from temp FS contents.

## State And Persistence
Persistent state is split between Bolt buckets (`root`, `rootTs`, `dataTs`, `pending`) and chunk files on disk. The root bucket stores a directory tree: directories are nested buckets with `"."` metadata and objects are JSON values. Pending uploads store destination path, added time, and started flag. Chunk timestamps are big-endian nanosecond keys mapping to path/offset/size.

## Dependencies And Integration Points
It integrates bbolt transactions, `walk.ListR`, cache `Object`/`Directory`, temp upload background workers, cache stats/RC commands, cleanup loops, and tests via methods in `utils_test.go`.

## Risks And Test Signals
Risks include singleton lifetime with closed DB reuse, recursive `iterateBuckets` opening nested read transactions, timestamp key collisions for chunks written in the same nanosecond, stale chunk files when DB records are inconsistent, pending-upload queue races, and path/root normalization. Tests cover temp queue states, chunk timestamp lookup, cleanup by size, notification-created parent buckets, cache purge, and reconciliation behavior.
