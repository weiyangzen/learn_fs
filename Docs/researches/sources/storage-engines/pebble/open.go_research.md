# sources/storage-engines/pebble/open.go

Purpose: This file implements Pebble DB opening and related read-only inspection helpers. It orchestrates option validation, recovery, directory locking, format-version handling, version-set initialization, WAL replay, object provider integration, cleanup scheduling, file cache setup, and background scheduling.

Important APIs and types: `FileCacheSize`, `Open`, `resolvedDirs`, `prepareOpenAndLockDirs`, `GetVersion`, `readOptionsFile`, `DBDesc`, `Peek`, `ErrDBDoesNotExist`, `ErrDBAlreadyExists`, `ErrDBNotPristine`, `checkConsistency`, and `walEventListenerAdaptor` are defined here. `Open` is the main public constructor.

Control flow: `Open` clones/validates options, recovers state, handles missing format-version markers and shared-storage minimum format, removes obsolete recovery files, creates cache and DB structures, initializes version sets for new or recovered DBs, initializes WAL manager/failover options, opens delete pacer and file cache, replays WALs, writes a new OPTIONS file, scans/deletes obsolete files, registers compaction scheduler, creates a new WAL, updates read state, ratchets format version if needed, schedules table stats/flush/compaction, closes recovery locks, and installs finalizer checks. Error defers clean up partially opened resources.

State and persistence: It writes OPTIONS files atomically through temp+rename+directory sync, may create/ratchet format markers, opens WALs, updates version state, and triggers obsolete cleanup. `prepareOpenAndLockDirs` creates/opens/locks data, WAL, failover, and recovery directories. `Peek` and `GetVersion` inspect existing files without fully opening the DB.

Dependencies and integration: It ties together `recoverState`, `manifest`, `wal`, `objstorage.Provider`, caches, delete pacer, compaction scheduler, and options. `checkConsistency` uses the object provider to compare local table sizes against MANIFEST state while skipping remote objects.

Risks and test signals: Risks include resource leaks on mid-open failure, format compatibility with shared objects, WAL failover identifier mismatch, lock handling, stale obsolete files, and remote objects skipped by synchronous consistency checks. Broad DB tests cover this path; subset cleanup tests validate open-triggered obsolete scanning.
