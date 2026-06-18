# sources/storage-engines/tikv/src/storage/txn/mod.rs

## Purpose
`mod.rs` is the public facade for TiKV's transactional storage module. It wires together transaction actions, command types, latches, scheduler, store abstractions, and transaction status cache support. It also defines the shared transaction `Result` and `Error` types and the `ProcessResult` enum that moves command outcomes between command processors, the scheduler, callbacks, and resumed command flows.

## Important APIs, types, and functions
The module exports submodules `commands`, `flow_controller`, `sched_pool`, `scheduler`, and `txn_status_cache`, while keeping `actions`, `latch`, `store`, `task`, and `tracker` private. Public re-exports expose the action entry points used by command handlers: pessimistic lock acquisition, cleanup, commit, flashback-to-version phases, GC, prewrite, transaction property types, `Command`, `TxnScheduler`, `Latches`, `Lock`, and store/scanner helper types.

`ProcessResult` is the central result carrier. It covers unit success, multi-result batches, prewrite details, MVCC introspection, lock lists, transaction status, chained `NextCommand`, error failures, pessimistic lock key results, secondary-lock status, and raw compare-and-swap responses. `ProcessResult::maybe_clone` intentionally clones only the successful pessimistic-lock response shape currently needed by scheduler side paths. `ProcessResult::get_key_lock_info` recognizes the nested storage/txn/MVCC `KeyIsLocked` error inside `PessimisticLockRes`, allowing scheduler logic to detect shared-lock update cases.

`ErrorInner` normalizes lower-level failures from the KV engine, codec, protobuf, MVCC, IO, concurrency-manager max-ts updates, and scheduler-specific validation cases. `Error::from_mvcc`, `Error::maybe_clone`, and the blanket `From<T: Into<ErrorInner>>` implementation make command code concise. `ErrorCodeExt` maps each variant to TiKV storage error codes used by diagnostics and client-facing response conversion.

## Control flow
Most execution flow enters through re-exported `Command` and `TxnScheduler`. Command handlers return `ProcessResult` and `Result<T>` values defined here. Errors propagate upward as `Error`, then are wrapped by storage-level errors in scheduler callbacks. The `NextCommand` result supports multi-phase operations by allowing read or write completion handlers to schedule a new command with the same callback.

The test-only `tests` module re-exports helper functions from action test modules, which gives downstream storage tests a stable namespace for common assertions such as must-prewrite, must-commit, must-cleanup, lock checks, and GC success.

## State and persistence behavior
This file does not maintain persistent state or write to storage directly. Its state role is representational: it defines process-result variants and error variants that describe persistent effects performed elsewhere. Variants such as `MaxTimestampNotSynced`, `RawKvMaxTimestampNotSynced`, `FlashbackNotPrepared`, and `InvalidReqRange` capture correctness gates around timestamp freshness, flashback region state, and physical snapshot bounds.

## Dependencies and integration points
The module integrates `kvproto::kvrpcpb::LockInfo`, transaction key/value/timestamp types from `txn_types`, TiKV storage error and MVCC error types, protobuf and codec errors, and `error_code` mappings. Its re-exports are consumed throughout storage command implementations and tests, so variant shape and public exports are part of a broad internal API surface.

## Risks and edge cases
The nested pattern in `get_key_lock_info` is brittle because it depends on the exact layering of storage, transaction, and MVCC errors. `maybe_clone` deliberately returns `None` for protobuf, IO, and boxed dynamic errors because they are not safely cloneable; callers must be prepared for non-cloneable errors. The blanket `From` implementation is convenient but can obscure which lower-level error conversion path was selected. Adding a new `ErrorInner` variant requires updating `maybe_clone` and `error_code` mappings or error reporting will lose fidelity.

## Test signals
There are no direct tests for `ProcessResult` or `ErrorCodeExt` in this file. Coverage comes from action tests re-exported under `txn::tests` and from scheduler/store tests that construct or inspect `ProcessResult` and transaction errors. Useful additional checks would assert `get_key_lock_info` on `KeyIsLocked`, `maybe_clone` behavior for cloneable and non-cloneable variants, and exact error-code mapping for newer variants such as raw max-ts freshness and invalid max-ts update.
