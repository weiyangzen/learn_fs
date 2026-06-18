# sources/storage-engines/tikv/src/storage/txn/actions/prewrite.rs

## Purpose
Implements the MVCC prewrite action for one mutation. It validates locks and committed versions, handles optimistic and pessimistic transaction modes, writes prewrite locks and long values, calculates async/1PC `min_commit_ts`, returns old values when requested, and supports pipelined-DML generations plus shared pessimistic lock upgrade.

## Important APIs, types, and functions
- `prewrite` is the public wrapper; `prewrite_with_generation` adds a generation for pipelined DML/flush.
- `TransactionProperties` carries start timestamp, transaction kind, commit kind, primary key, TTL, txn size, min commit timestamp, old-value requirement, retry flag, assertion level, and transaction source.
- `CommitKind::{TwoPc, OnePc(max_commit_ts), Async(max_commit_ts)}` controls commit timestamp calculation and lock flags.
- `TransactionKind::{Optimistic(skip_constraint_check), Pessimistic(for_update_ts)}` controls conflict checking.
- `PrewriteMutation` normalizes `Mutation` and owns most validation: `check_lock`, `check_for_newer_version`, `check_assertion`, `write_lock`.
- `async_commit_timestamps` calculates and installs in-memory locks under the concurrency manager; `amend_pessimistic_lock` recovers when a pipelined pessimistic lock was not persisted.

## Control flow
`prewrite_with_generation` converts the mutation, updates the concurrency manager for insert/check-not-exists reads, applies failpoints, and loads lock CF. Existing exclusive locks go through `check_lock`; shared locks require the current transaction to be present and the mutation to be `SharedLock`. Missing locks under `DoPessimisticCheck` trigger pessimistic amend for normal mutations and `PessimisticLockNotFound` for shared lock prewrite.

Duplicate prewrites at generation zero return the existing min commit timestamp. Otherwise the action optionally checks newer versions, runs assertion checks, computes old value if requested, and exits early for `should_not_write` mutations. For writes, `write_lock` creates a lock with TTL, primary, for-update timestamp, transaction size, min commit timestamp, transaction source, optional `last_change`, and short or long value placement. Async commit and 1PC calculate a final min commit timestamp under the key latch and may fall back to 2PC on `CommitTsTooLarge`. Shared lock prewrite updates a sub-lock inside `SharedLocks` and rejects async commit, 1PC, and nonzero generation.

## State and persistence behavior
Prewrite stages mutations in `MvccTxn`: lock CF receives `Lock` or `SharedLocks`, default CF receives long values, and in-memory latch guards are stored in `txn.guards` for async/1PC conflict visibility. It also updates `ConcurrencyManager::max_ts` for insert/check-not-exists linearizability and stores in-memory locks for async/1PC. Old values are returned as `OldValue::{None, Value, ValueTimeStamp, Unspecified}` without necessarily writing state.

## Dependencies and integration points
The action uses `check_data_constraint`, `common::next_last_change_info`, MVCC metrics, `txn_types::{Mutation, Lock, SharedLocks, Write}`, `SnapshotReader`, `MvccTxn`, scheduler TLS feature gating for `LAST_CHANGE_TS`, and command prewrite/flush/acquire-pessimistic-lock flows. `actions/tests.rs` wraps it for many cross-action tests.

## Risks and edge cases
Correctness hinges on not skipping constraint checks in retry paths that can lose idempotence, respecting `expected_for_update_ts` for force-locked pessimistic locks, and handling rollback records without false conflicts. Assertion checks have performance-sensitive reload rules and strict/fast/off semantics. Async/1PC fallback must clear lock flags and secondaries. Shared lock prewrite is intentionally narrow; accepting wrong mutation types, generations, or commit modes would corrupt shared-lock state. Long value placement and old-value reads must respect GC fences and short-value encoding.

## Test signals
The large test module covers async commit and 1PC max/min commit timestamps, pessimistic variants, GC fence handling, resend/retry behavior for non-pessimistic keys, old value over rollback/lock/delete/random histories, assertion levels, deferred uniqueness checks, last-change calculation and inheritance, expected `for_update_ts`, 1PC in-memory lock visibility, and shared-lock prewrite merge/rejection cases.
