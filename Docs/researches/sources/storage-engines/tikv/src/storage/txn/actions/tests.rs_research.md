# sources/storage-engines/tikv/src/storage/txn/actions/tests.rs

## Purpose
Defines reusable test helpers for the transaction action layer. These helpers perform prewrite, flush, pessimistic prewrite, delete, lock, shared lock, and rollback operations against a test engine and assert success or failure.

## Important APIs, types, and functions
- `must_prewrite_put_impl`, `must_prewrite_put_impl_with_should_not_exist`, and `must_prewrite_insert_impl` are the central successful prewrite wrappers.
- `flush_put_impl`, `flush_put_impl_with_assertion`, and `must_flush_put` exercise command-layer `Flush` with generations.
- `must_pessimistic_prewrite_*`, `must_prewrite_put_async_commit`, and `must_pessimistic_prewrite_put_async_commit` cover pessimistic and async paths.
- `must_prewrite_put_err_impl*`, `must_prewrite_insert_err_impl`, and related wrappers return expected `mvcc::Error`.
- `must_prewrite_delete`, `must_prewrite_lock`, `must_shared_prewrite_lock`, and `must_rollback` stage common MVCC histories.

## Control flow
Most helpers build a `Context`, take an engine snapshot, create a `ConcurrencyManager`, `MvccTxn`, and `SnapshotReader`, construct `TransactionProperties`, call `prewrite` or `txn::cleanup`, then write `txn.into_modifies()` to the engine. Error helpers stop before writing and return the unwrapped error. Flush helpers construct a command and run `process_write` with a `WriteContext` that includes `MockLockManager`, statistics, and a test `TxnStatusCache`.

## State and persistence behavior
Successful helpers persist staged lock/write/default CF mutations through the engine's `write` method or `mvcc::tests::write`. Error helpers are read/validation paths and do not persist `MvccTxn` modifications. Helpers can set region id and transaction source in `Context`, set async commit secondaries, TTLs, min/max commit timestamps, assertions, retry flags, and expected for-update timestamps.

## Dependencies and integration points
This file sits under `actions` but integrates command and action layers: `prewrite`, `Flush`, `WriteContext`, `MockLockManager`, `TxnStatusCache`, `MvccTxn`, `SnapshotReader`, and test MVCC write utilities. Other action tests import these helpers to assemble repeatable histories.

## Risks and edge cases
Because these are assertion helpers, parameter defaults encode assumptions used by many tests. A subtle change in defaults for `pessimistic_action`, `for_update_ts`, assertion level, region id, transaction source, or async secondaries can change broad test semantics. Helpers that write immediately are unsuitable for tests needing to inspect staged but unapplied modifications.

## Test signals
This file is itself test infrastructure. Its signal comes from downstream modules: commit, prewrite, gc, flashback, cleanup, and command tests rely on these helpers to create committed versions, locks, rollbacks, shared-lock upgrades, async commit locks, and failure cases.
