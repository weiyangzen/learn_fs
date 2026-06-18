# sources/sync-backup/syncthing/internal/db/sqlite/db_service.go

## Purpose
This file implements periodic SQLite maintenance and garbage collection for main and folder databases.

## Important APIs and Control Flow
`DB.Service` returns a `Service` with a maintenance interval, typed metadata namespace, and manual-start channel. `Serve` schedules the next run from `dbsvc/lastMaint`, accepts manual starts through `StartMaintenance`, runs `periodic`, reports manual completion, and stores the last maintenance time. `periodic` tidies the main DB under `updateLock`, then iterates folders. For each folder it compares current local sequence to `dbsvc/lastSuccessfulGCSeq`; unchanged folders skip garbage collection. Changed folders run old-deleted cleanup, unused name/version cleanup, blocklist/block cleanup, and tidy under the folder update lock.

## State and Persistence Behavior
Maintenance writes typed KV metadata, runs `ANALYZE`, `PRAGMA optimize`, incremental vacuum, journal size limits, and WAL truncate checkpoints. It deletes old deleted file rows based on `deleteRetention`, orphaned `file_names` and `file_versions`, and unreferenced `blocklists` and `blocks`.

## Dependencies and Integration Points
The service integrates with `db.Typed`, `forEachFolder`, `folderDB.GetDeviceSequence`, SQLite pragmas, and the folder schema's foreign-key relationships. `blobRange`, `randomBlobRanges`, `blobRanges`, and `intToBlob` partition blob keyspace for bounded GC work.

## Risks and Test Signals
Block GC temporarily disables foreign keys on one connection and manually deletes in randomized blob ranges with a five-minute per-table cap, so interruption can leave garbage for a later run but must not delete referenced rows. `db_service_test.go` checks range SQL generation; `db_test.go` validates blocklist GC after deleting a file.
