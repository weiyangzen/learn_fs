# sources/sync-backup/restic/cmd/restic/integration_test.go

## Purpose

This file contains integration-style tests for restic command behavior around repository locking, backend list semantics, backend reader capabilities, and transient repository config access failures. The tests are written in package `main`, so they exercise the command-layer helpers and options directly rather than only testing exported internal packages.

## Important APIs, Types, and Functions

- `TestCheckRestoreNoLock` builds a readonly repository fixture, sets `env.gopts.NoLock = true`, then runs check, snapshot listing, and restore. It validates that read-oriented commands still work when locking is deliberately disabled and the repository storage cannot be written.
- `listOnceBackend` embeds `backend.Backend` and tracks file types listed through `List`. It rejects a second listing of any non-lock `restic.FileType`. With `strictOrder`, it also rejects listing snapshots after indexes, catching workflows that would break on eventually consistent backends.
- `newListOnceBackend` and `newOrderedListOnceBackend` are small wrappers used as backend test hooks.
- `TestListOnce` installs `newOrderedListOnceBackend`, creates a prunable repository, runs prune, check with read-data and unused checks, and rebuild-index with and without reading all packs. The test asserts these commands do not rely on repeated listing and preserve the expected index/snapshot listing order.
- `writeToOnly` implements `io.Reader` and `io.WriterTo`, but its `Read` method fails. It catches code paths that accidentally drop the `WriterTo` optimization/capability.
- `onlyLoadWithWriteToBackend` wraps `Load` so every load callback receives a `writeToOnly` reader.
- `TestBackendLoadWriteTo` installs that wrapper as `BackendInnerTestHook`, disables cache during a backup to force backend reads later, then re-enables cache and lists snapshots. Success means layered backend/load code preserves `WriteTo`.
- `failConfigOnceBackend` embeds `backend.Backend` and fails exactly once for config `Load` or `Stat`, depending on which method is used first.
- `TestBackendRetryConfig` installs `failConfigOnceBackend`, initializes test data, then runs another backup. It asserts config loading retries both during init/open and later command execution.
- External helpers used heavily here include `withTestEnvironment`, `testSetupBackupData`, `testRunBackup`, `testRunCheck`, `testRunRestore`, `testListSnapshots`, `testRunPrune`, `runCheck`, `runRebuildIndex`, `openWithReadLock`, and `FindFilteredSnapshots`.

## Control Flow

Each test creates a temporary restic test environment, injects optional backend wrappers through `global.Options` hooks, runs command-level helpers, and fails via `internal/test` assertions. Backend wrappers intercept `List`, `Load`, or `Stat` at the backend boundary. The `ListOnce` tests force prune/check/rebuild-index/find flows through a backend that can tolerate only one list pass per type. `TestFindListOnce` backs up three snapshots, combines explicit full ID, short ID, and `"latest"` selectors, and confirms the resulting ID set equals the known three snapshots without requiring another backend listing.

## State and Persistence Behavior

The tests create real repository fixtures under temporary directories and mutate repository contents through backup/prune/check/rebuild/restore commands. `TestCheckRestoreNoLock` changes filesystem permissions under `env.repo` to remove write bits and then verifies no-lock read operations avoid lock writes. The backend wrappers maintain in-memory state (`listedFileType`, `failedOnce`) only for a single test run. The tests also exercise cache behavior by toggling `env.gopts.NoCache`.

## Dependencies and Integration Points

The file depends on restic internals: `internal/backend`, `internal/data`, `internal/errors`, `internal/global`, `internal/restic`, `internal/test`, and `internal/ui/progress`. Its main integration point is `global.Options` backend hook support, which allows tests to wrap configured backends without changing production command code. It also directly exercises command package functions such as `runCheck`, `runRebuildIndex`, `openWithReadLock`, and snapshot filtering.

## Risks and Edge Cases

- The list-once wrappers intentionally exempt lock files; commands may list locks multiple times during locking/unlocking without failing these tests.
- `strictOrder` specifically guards against listing snapshots after indexes, a subtle risk for eventually consistent object stores.
- `writeToOnly.Read` panics through an error rather than returning EOF, making capability loss obvious.
- `failConfigOnceBackend` fails either `Load` or `Stat`, depending on access path. Tests therefore cover retry behavior without depending on one exact config access method.
- Permission changes in `TestCheckRestoreNoLock` rely on the test fixture and host filesystem honoring chmod semantics.

## Test Signals

This file is itself a test signal for backend abstractions and command integration. Passing tests indicate read operations can run with `--no-lock`, backup/check/rebuild/find avoid unsafe repeated listings, backend `Load` preserves `io.WriterTo`, and transient config access errors are retried.
