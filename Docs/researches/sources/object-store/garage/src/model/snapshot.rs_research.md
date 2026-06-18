# sources/object-store/garage/src/model/snapshot.rs

## Purpose
This file implements manual and automatic metadata DB snapshots. It creates snapshot directories/files through the DB engine, keeps only the newest snapshots, and exposes a background worker for periodic snapshots.

## Important APIs, types, and functions
`async_snapshot_metadata` runs blocking snapshot work on a Tokio blocking thread. `snapshot_metadata` acquires a global `SNAPSHOT_MUTEX`, chooses the configured/default snapshot directory, calls `garage.db.snapshot`, and invokes `cleanup_snapshots`. `AutoSnapshotWorker` schedules periodic snapshots with randomized interval. `KEEP_SNAPSHOTS` is 2.

## Control flow
Manual snapshots fail fast if another snapshot is running. Snapshot names are current UTC RFC3339 timestamps. Cleanup reads entries, filters short names, sorts by filename, and deletes all but the two newest. Auto worker first schedules half an interval after startup, then after each successful snapshot schedules `interval * (1.0..1.2)`.

## State and persistence behavior
Snapshots are filesystem artifacts under `metadata_snapshots_dir` or `<metadata_dir>/snapshots`. No metadata table rows are changed. The auto worker keeps scheduling state only in memory.

## Dependencies and integration points
It depends on Garage DB snapshot support, filesystem APIs, background worker traits, rand, chrono, and Garage config. `Garage::spawn_workers` starts it when configured.

## Risks and edge cases
`cleanup_snapshots` constructs deletion paths with `snapshots_dir.join(to_delete.path())`; because `DirEntry::path()` is already a path, this deserves review for path correctness. Cleanup handles only files directly inside snapshot directories before removing the directory, so nested directories could fail. Auto snapshots stop on snapshot errors and reschedule only after success because `work` returns the error.

## Test signals
No local tests. Useful tests should cover lock contention, default/configured directories, retention ordering, directory cleanup, auto scheduling, and the `join(to_delete.path())` path behavior.
