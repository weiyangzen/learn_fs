# sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.cc

## Purpose

`db_impl_follower.cc` implements follower-mode DB open and refresh. A follower opens a local DB path backed by an on-demand filesystem pointing at a leader/source path, replays the leader MANIFEST through `ReactiveVersionSet`, creates local links to needed leader files, and periodically tails the MANIFEST to keep read state current. It is a read-scaling mode that differs from ordinary read-only open because it keeps catching up while the leader continues to evolve.

## Important APIs, Types, And Functions

- `DBImplFollower::DBImplFollower` constructs a `DBImplSecondary` with an empty secondary path, stores the wrapped `Env`, source path, condition variable, and stop flag.
- `DBImplFollower::~DBImplFollower` delegates to `Close`.
- `DBImplFollower::Recover` replays the MANIFEST with `ReactiveVersionSet::Recover`, creates the default column-family handle, records internal stats, and starts a dedicated periodic catch-up thread.
- `DBImplFollower::TryCatchUpWithLeader` tails and applies new MANIFEST records with `ReactiveVersionSet::ReadAndApply`.
- `DBImplFollower::PeriodicRefresh` sleeps for `follower_refresh_catchup_period_ms`, retries catch-up according to `follower_catchup_retry_count` and `follower_catchup_retry_wait_ms`, and stops when requested.
- `DBImplFollower::Close` stops and joins the catch-up thread, releases captured pending output file numbers, and closes the base DBImpl.
- `DB::OpenAsFollower` overloads build options, validate/create the local follower path, wrap the filesystem with `NewOnDemandFileSystem`, create a logger if needed, install `ReactiveVersionSet`, recover, create handles, install superversions, and publish the DB pointer.

## Control Flow

`DB::OpenAsFollower(Options, ...)` normalizes the single-default-CF case into the multi-CF overload. The multi-CF overload checks or creates `dbname`, constructs a `CompositeEnvWrapper` whose filesystem can fetch files on demand from `src_path` into `dbname`, creates an info log if needed, constructs `DBImplFollower`, replaces its `versions_` with `ReactiveVersionSet`, initializes `ColumnFamilyMemTablesImpl`, records whether WAL dir equals DB path, then calls `Recover` under `mutex_`.

`Recover` requires the DB mutex. It calls `ReactiveVersionSet::Recover` with the manifest reader and reporter, handles a failed manifest-reader status by permitting the unchecked error, creates the default column-family handle on success, and starts `catch_up_thread_`.

`TryCatchUpWithLeader` runs later from the refresh thread. It locks `mutex_`, asks `ReactiveVersionSet::ReadAndApply` to apply new manifest entries, releases and recaptures a pending-output file number around `current_next_file_number`, logs last sequence and next file number, and for each changed CF logs summary information. For non-dropped changed CFs, if the current memtable earliest sequence is older than the new last sequence, it moves the old memtable to immutable state, constructs fragmented range tombstones, and installs a fresh memtable with earliest sequence equal to `LastSequence`. It removes obsolete immutable memtables and installs a new superversion for each changed CF. It also deletes files returned by `ReadAndApply`, then outside that lock uses normal `FindObsoleteFiles`/`PurgeObsoleteFiles` cleanup.

`PeriodicRefresh` uses its private `mu_`/`cv_` for sleeping and shutdown notification, not the DB mutex. On each period it attempts catch-up repeatedly until success, retry exhaustion, or stop. `Close` sets `stop_requested_`, signals the condition variable, joins the thread, releases the pending output iterator, and calls `DBImpl::Close`.

## State And Persistence Behavior

Follower mode persists local metadata and linked/fetched files in `dbname`, while source data is accessed through an on-demand filesystem rooted at `src_path`. The code captures a pending output number during catch-up to keep cleanup from deleting files at or above the reactive next-file boundary. It maintains normal column-family superversion state for readers, but it does not create user-write WALs. `OwnTablesAndLogs()` currently returns true with a TODO about read-scaling deletion semantics, meaning purge behavior is intentionally conservative but still owner-like in this implementation.

## Dependencies And Integration Points

The follower depends on `DBImplSecondary`, `ReactiveVersionSet`, `CompositeEnvWrapper`, `NewOnDemandFileSystem`, manifest reader/reporting state from the base implementation, `ColumnFamilyMemTablesImpl`, `ColumnFamilyHandleImpl`, memtable/superversion machinery, file deletion helpers from `db_impl_files.cc`, and DB open entry points. It integrates with thread-status/logging, perf sync points, and the regular column-family handle API after open.

## Risks And Edge Cases

- Catch-up mutates versions, memtables, and superversions while readers may be active; correct locking and superversion install/cleanup are critical.
- The private refresh condition variable and DB mutex are separate; shutdown must wake sleeping retry loops promptly.
- Manifest tailing can fail transiently; the current TODO notes missing robust retry/error notification beyond local retries.
- File deletion for read scaling is called out as incomplete. Incorrect ownership or pending-output tracking could remove files still needed by the follower.
- Dropped column families are skipped for logging but changed-CF iteration must avoid installing reader state for dropped CFs.
- Local/source DB identity misconfiguration is not fully prevented; comments call out a future local `IDENTITY` cross-check.

## Test Signals

High-value tests should open as follower, verify default and named CF handles, force manifest catch-up, exercise dropped CFs, validate superversion replacement while iterators/readers exist, inject `ReadAndApply` failures and retry waits, test clean shutdown while sleeping and while catching up, verify on-demand links survive leader compaction/deletion, and assert obsolete cleanup does not delete needed source-linked files. Existing sync points around `TryCatchUpWithLeader` support deterministic catch-up race tests.
