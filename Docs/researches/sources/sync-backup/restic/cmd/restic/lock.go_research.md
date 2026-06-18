# sources/sync-backup/restic/cmd/restic/lock.go

## Purpose

This file centralizes command-layer repository opening with optional locking. It provides small helpers for read, append, and exclusive command modes and delegates actual repository opening and lock acquisition to internal global/repository packages.

## Important APIs, Types, and Functions

- `internalOpenWithLocked(ctx, gopts, dryRun, exclusive, printer)` opens the repository via `global.OpenRepository`. If `dryRun` is false, it acquires a repository lock with `repository.LockRepo`; if `dryRun` is true, it marks the repository as dry-run with `repo.SetDryRun()` and skips locking.
- `openWithReadLock(ctx, gopts, noLock, printer)` calls `internalOpenWithLocked` with `exclusive=false` and maps its `noLock` argument to `dryRun`.
- `openWithAppendLock(ctx, gopts, dryRun, printer)` opens a non-exclusive lock unless dry-run is requested.
- `openWithExclusiveLock(ctx, gopts, dryRun, printer)` opens an exclusive lock unless dry-run is requested.

All helpers return the possibly updated context, the opened `*repository.Repository`, an `unlock` callback, and an error.

## Control Flow

The common helper first opens the repository. It initializes `unlock` to a no-op so callers can defer it safely only after checking errors. For non-dry-run operations it calls `repository.LockRepo(ctx, repo, exclusive, gopts.RetryLock, statusCallback, printer.E)`. The status callback prints retry/lock messages through `printer.P` unless JSON output is enabled. On success, the lock's `Unlock` method becomes the returned cleanup function. For dry-run/no-lock operations it marks the repository dry-run and returns without lock acquisition.

## State and Persistence Behavior

The main persistent side effect is creation/removal of repository lock files through `repository.LockRepo` and the returned `Unlock` function. Dry-run/no-lock mode avoids lock file writes and changes in-memory repository state via `SetDryRun`. The helper does not itself persist data beyond lock behavior.

## Dependencies and Integration Points

The file depends on `internal/global` for repository construction, `internal/repository` for locking, and `internal/ui/progress` for output. It is used by many command implementations that need consistent lock policy. It also interacts with `global.Options.RetryLock`, `global.Options.JSON`, and the terminal printer interface.

## Risks and Edge Cases

- `openWithReadLock` currently treats `noLock` as `dryRun`; the TODO notes that stronger read-only enforcement is still pending until locking moves deeper into the repository layer.
- If `repository.LockRepo` fails after opening a repository, the returned repo is discarded and no unlock function is returned. Callers must handle the error path.
- JSON mode suppresses human lock retry messages to avoid corrupting structured output.
- The dry-run path avoids locks, so commands using it must ensure they do not persist unintended repository changes.

## Test Signals

`integration_test.go` covers no-lock behavior with a readonly repository. Broader command tests that run append/exclusive operations indirectly cover successful locking and unlock cleanup.
