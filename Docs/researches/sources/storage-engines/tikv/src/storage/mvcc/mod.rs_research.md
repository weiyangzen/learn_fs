# sources/storage-engines/tikv/src/storage/mvcc/mod.rs

## Purpose

This is the MVCC module root. It declares MVCC submodules, re-exports the primary transaction/reader/checker APIs, defines the storage-layer MVCC error type and error-code mapping, provides default-value-missing critical handling, and contains test helpers used across transaction and reader tests.

## Important APIs, Types, and Functions

- Submodules: `consistency_check`, `metrics`, `mvcc_read_tracker`, `reader`, and `txn`.
- Public re-exports include MVCC keys/locks/writes from `txn_types`, consistency-check and MVCC-info scanners, reader APIs, transaction APIs such as `MvccTxn`, and selected histograms.
- `ErrorInner` is the central MVCC error taxonomy. It covers engine/IO/codec errors, lock conflicts, committed/rollback states, missing locks, write conflicts, deadlocks, assertions, commit timestamp validity, pessimistic lock failure reasons, flashback-era generation errors, shared-lock shrink-mode violations, and miscellaneous boxed errors.
- `Error` boxes `ErrorInner`, provides transparent error behavior, and supports `maybe_clone` for cloneable variants.
- `From` implementations convert storage KV errors, IO, codec, PD, and `txn_types` errors into MVCC errors.
- `ErrorCodeExt for Error` maps each MVCC error variant to the stable storage error code used by clients and telemetry.
- `default_not_found_error` increments the critical error metric, optionally sets a panic mark and panics depending on config, or logs a backtrace and returns `DefaultNotFound`.
- `PessimisticLockNotFoundReason` classifies why a pessimistic lock was not found.
- `tests` contains helper assertions and write/read routines such as `must_get`, `must_locked`, `must_written`, `must_get_commit_ts`, and shared-lock loading helpers.

## Control Flow

Normal MVCC code returns `Result<T> = std::result::Result<T, Error>`. Errors from lower layers are converted into `ErrorInner`, optionally cloned for retry or propagation, then mapped to a public error code when needed. The `default_not_found_error` path is intentionally special: default CF absence after a write record points to it is treated as data corruption or unexpected data loss, so it records `CRITICAL_ERROR` and either panics under strict config or returns a structured `DefaultNotFound`.

The test helper flow builds snapshots, constructs `SnapshotReader` or `MvccReader`, checks lock conflicts where needed, then asserts reads/writes/locks against encoded MVCC state.

## State and Persistence Behavior

The module root does not persist MVCC data directly. Its state effects are diagnostic: critical-error metrics, panic marks, logs with backtraces, and helper test writes through the storage engine. Persistent state is handled by transaction modules and readers re-exported here.

## Dependencies and Integration Points

This file is the integration boundary between `txn_types`, `kvproto`, `engine_traits`, error-code infrastructure, TiKV utility logging/panic behavior, storage KV abstractions, MVCC reader/txn modules, and raftstore consistency checking. Client-facing behavior depends on the exact `ErrorCodeExt` mapping, so changing variants or mappings affects RPC error contracts.

## Risks and Edge Cases

- `ErrorInner::maybe_clone` intentionally returns `None` for IO and opaque `Other` errors; callers must tolerate non-cloneable errors.
- The blanket `impl<T: Into<ErrorInner>> From<T> for Error` uses specialization-style `default fn`, so compiler/toolchain compatibility matters.
- `GenerationOutOfOrder`'s format string appears to use `{1:?}` for both key and lock text, which may make logs misleading.
- `default_not_found_error` can panic depending on runtime config; paths that call it are high-severity consistency assumptions, not ordinary missing-key cases.
- Test helpers assume shared locks are unsupported in several legacy single-lock assertion paths and use `unimplemented!` if encountered.

## Test Signals

Local content is mostly reusable test support rather than direct tests. It is exercised by MVCC transaction and reader suites that validate locking, commits, rollbacks, overlapped rollbacks, old value retrieval, shared locks, and error cases.
