# sources/storage-engines/rocksdb/db/db_impl/db_impl_follower.h

## Purpose

`db_impl_follower.h` declares `DBImplFollower`, the follower-mode DB implementation used by `DB::OpenAsFollower`. It specializes `DBImplSecondary` for a reactive, manifest-tailing read-scaling instance that uses a local DB path plus a source/leader path.

## Important APIs, Types, And Functions

- `class DBImplFollower : public DBImplSecondary` inherits secondary/read-only behavior and overrides recovery and close.
- The constructor takes sanitized `DBOptions`, an owned `Env`, `dbname`, and `src_path`.
- `~DBImplFollower()` closes the instance.
- `Status Close() override` stops background catch-up before base close.
- `OwnTablesAndLogs() const override` currently returns true, with a TODO explaining file deletion semantics for read scaling still need refinement.
- `Recover(...) override` has the same signature shape as `DBImpl::Recover` but ignores write/retry parameters that do not apply to follower recovery.
- Private helpers `TryCatchUpWithLeader` and `PeriodicRefresh` implement background manifest tailing.
- Private state includes `env_guard_`, `catch_up_thread_`, `stop_requested_`, `src_path_`, a private mutex/condition variable pair, and `pending_outputs_inserted_elem_`.

## Control Flow

The header makes `DB` a friend so open factories can construct and initialize `DBImplFollower` directly. Normal construction stores the environment wrapper and source path. Recovery is protected and called by open. Once recovered, the implementation starts `PeriodicRefresh`, which calls `TryCatchUpWithLeader` until `Close` sets `stop_requested_` and joins the thread.

## State And Persistence Behavior

`env_guard_` owns the composite/on-demand environment for the follower lifetime. `src_path_` identifies the leader/source DB path. `pending_outputs_inserted_elem_` pins a file-number boundary during reactive apply so obsolete-file cleanup treats freshly observed or soon-to-be-linked files as protected. The private `mu_`/`cv_` are lifecycle controls for the refresh thread and are separate from DBImpl's main mutex.

## Dependencies And Integration Points

The declaration depends on `db_impl.h`, `db_impl_secondary.h`, `logging`, and `port` threading primitives. Its protected overrides plug into the DBImpl open/recovery lifecycle, while private helpers integrate with `ReactiveVersionSet` in the `.cc` file.

## Risks And Edge Cases

- Returning true from `OwnTablesAndLogs` is explicitly marked provisional and affects purge ownership.
- The class owns a background thread; destructors and `Close` must be idempotent enough to handle open failures and explicit close.
- The recovery signature ignores several base parameters, so future DBImpl recovery contract changes must be reflected here.
- `pending_outputs_inserted_elem_` is a unique pointer to a list iterator; release/reset ordering matters for cleanup safety.

## Test Signals

Compile-time coverage should ensure all DBImpl recovery/close overrides still match the base class. Runtime tests should cover construction through `DB::OpenAsFollower`, repeated `Close`, destructor close after partial initialization, thread wakeup, and purge behavior while `pending_outputs_inserted_elem_` is set.
