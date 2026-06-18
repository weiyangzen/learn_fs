# sources/storage-engines/tikv/src/storage/txn/commands/prewrite.rs

## Purpose
`prewrite.rs` implements the storage scheduler commands for optimistic and pessimistic transaction prewrite. This is the first phase of TiKV's 2PC protocol, with extensions for async commit, 1PC, pessimistic-lock checking, assertion checking, retry idempotence, and CDC old-value collection. The file centralizes both public commands behind a generic `Prewriter<K>` so most MVCC write-loop behavior is shared while transaction-kind specific differences are isolated.

## Important APIs, types, and functions
The command macro defines `Prewrite` and `PrewritePessimistic`, both returning `PrewriteResult`. `Prewrite` carries `Vec<Mutation>`, primary key, `start_ts`, TTL, transaction size, min/max commit timestamps, optional async-commit secondaries, `try_one_pc`, and assertion level. `PrewritePessimistic` carries `(Mutation, PrewriteRequestPessimisticAction)` plus `for_update_ts` and `for_update_ts_constraints`.

`Prewriter<K>` is the main executor. `PrewriteKind` abstracts `txn_kind()` and optimistic-only `can_skip_constraint_check()`. `MutationLock` abstracts plain optimistic mutations and `PessimisticMutation`, which adds pessimistic action and optional expected `for_update_ts`. Public helper functions include `one_pc_commit()` and crate-visible `fallback_1pc_locks()`.

## Control flow
`process_write` first handles a pessimistic retry special case by checking `txn_status_cache` for a known commit and forcing retry semantics. It then lets the transaction kind skip or enforce constraints, checks that the snapshot's max timestamp is synced for async commit or 1PC, creates an `MvccTxn` and `SnapshotReader`, and calls `prewrite()`.

`prewrite()` computes `CommitKind` as 1PC, async commit, or normal 2PC. It builds `TransactionProperties` and iterates all mutations. For the async primary key it passes the full secondary set; for other async keys it passes an empty set. Each mutation delegates to `actions::prewrite::prewrite`. Successful async or 1PC results update the final min commit timestamp and old-value map. A zero min-commit timestamp forces fallback to 2PC, clears async/1PC flags, moves pending 1PC locks into normal lock CF writes, and releases memory guards. Write conflict, missing pessimistic lock, key-locked, and commit-ts-too-large paths call `check_committed_record_on_err` to preserve idempotence for retried prewrites that already committed.

`write_result()` emits either a write batch with locks and optional 1PC commit writes, or a lock-error-only response with no writes. Async commit and successful 1PC may switch the response policy to `OnCommitted` when `async_apply_prewrite` is enabled.

## State and persistence behavior
The command writes MVCC locks, write records for 1PC, old-value metadata in `TxnExtra`, known committed transaction status for cache promotion, lock guards, and released-lock notifications. It persists normal lock CF records for 2PC/async commit, and for 1PC converts collected locks directly into write CF records at `final_min_commit_ts` before unlocking pessimistic locks. It also sets disk-full options from context and supports old-value collection when `ExtraOp::ReadOldValue` is requested.

## Dependencies and integration points
This file depends on `txn_types` mutations, locks, timestamps, writes, and old values; `MvccTxn` and `SnapshotReader`; `actions::prewrite`; `check_committed_record_on_err`; lock manager guards; scheduler `WriteCommand`; and metrics. It integrates with async commit/1PC timestamp safety through `SnapshotExt::is_max_ts_synced`, with conflict retry through `txn_status_cache`, with CDC through `TxnExtra`, and with commit/rollback commands through the locks it leaves or releases.

## Risks
The main correctness risks are atomicity during 1PC, retry idempotence after partial network failures, async/1PC fallback without leaving stale memory locks, commit timestamp bounds, and pessimistic `for_update_ts` validation. The optimistic bulk skip path sorts mutations and may skip constraint checks only when no write data exists in the target range; mistakes there can violate uniqueness or conflict semantics. Assertion errors are deliberately delayed behind more concrete errors, which is important for index-key conflict behavior.

## Test signals
The embedded tests are extensive. They cover skip-constraint checks and tombstones, optimistic and pessimistic 1PC, async commit fallback, max-ts sync rejection, response policy selection, `CheckNotExists`, committed and rolled-back retry idempotence, newer-lock encounters, commit-ts-too-large retry recovery, last-change timestamp calculation, pessimistic `for_update_ts` constraints, and shared-lock prewrite restrictions. These tests are strong regression signals for transaction protocol edge cases.
