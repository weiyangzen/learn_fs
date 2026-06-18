# sources/sync-backup/kopia/snapshot/snapshotfs/source_snapshots.go

Purpose: virtual directory that lists all snapshots for one source as timestamp-named child directories.

Important APIs/types/functions: `sourceSnapshots`, its `fs.Directory` methods, and `Iterate`.

Control flow: `Iterate` calls `snapshot.ListSnapshots` for the configured source, formats each start time as `YYYYMMDD-HHMMSS`, appends the incomplete reason in parentheses when present, builds a synthetic directory `DirEntry` with the snapshot root object ID, and returns repository entries.

State and persistence: read-only synthetic entries backed by actual root objects. Directory summary is copied from `m.RootEntry.DirSummary` when present.

Dependencies and integration points: leaf level under `AllSourcesEntry` for browsing historical snapshots and feeding restore/mount traversal.

Risks and test signals: snapshots with identical second-level start times and same incomplete reason would map to duplicate child names. Tests validate typical naming through the all-sources integration suite.
