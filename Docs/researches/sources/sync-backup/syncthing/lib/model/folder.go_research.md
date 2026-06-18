# sources/sync-backup/syncthing/lib/model/folder.go

## Purpose
Implements the shared folder service: lifecycle, scanning, pull scheduling, health checks, watcher management, error tracking, local database updates, and forced rescans. Specialized folder modes embed this base.

## Important APIs, Types, and Functions
Core types are `folder`, `syncRequest`, `puller`, `scanBatch`, and `cFiler`. Public-like service methods include `Serve`, `Scan`, `ScheduleScan`, `DelayScan`, `SchedulePull`, `ScheduleForceRescan`, `Errors`, `WatchError`, `Override`, `Revert`, `BringToFront`, and `Jobs`. Key internals include `pull`, `scanSubdirs`, `scanSubdirsChangedAndNew`, `scanSubdirsDeletedAndIgnored`, `findRename`, watcher routines, `updateLocals`, and `unifySubs`.

## Control Flow
`Serve` sets startup state, reconciles block index, optionally starts the watcher, then runs a select loop over context cancellation, pull scheduling, pull retry backoff, initial scan completion, forced rescans, scan timers, synchronous requests, watcher events, watcher restarts, and version cleanup. `scanSubdirs` reloads ignores, takes the IO limiter, normalizes subdirs, scans changed/new files, flushes updates, then walks database prefixes to mark deleted or newly ignored items. `pull` waits for initial scan, checks need count and health, reloads ignores, takes IO when needed, delegates to the mode-specific puller, and schedules exponential retry on failure.

## State and Persistence Behavior
The folder holds timers, channels, state tracker, local/pull error slices, forced-rescan map, watcher state, stats reference, and mutable ignore matcher. Persistent state is in Syncthing DB through `db.Update`, `DropFilesNamed`, block index population/drop, folder stats, and local index events. Filesystem state is read through scanners and watchers; version cleanup may mutate versioned files via the configured versioner.

## Dependencies and Integration Points
Integrates with `config.FolderConfiguration`, `db.DB`, `fs.Filesystem`, `ignore.Matcher`, `scanner`, `events`, `stats`, `locations`, `watchaggregator`, `versioner`, and semaphores. It is the base for send-receive, send-only, receive-only, and receive-encrypted modes.

## Risks
This file has high concurrency complexity: timers must be stopped/drained correctly, buffered scheduling channels coalesce events, and watcher goroutines interact with scans. Global path health, ignore reloads, and DB updates can fail mid-scan. `updateLocals` ignores return values in some callers, and global mutable folder state requires sequencing through `doInSync`.

## Test Signals
Direct tests are not in this file, but many model tests exercise scanning, receive-only behavior, fake connections, and pull scheduling. Additional focused tests would help for `unifySubs`, watcher restart errors, forced rescan, and deleted/ignored database reconciliation.
