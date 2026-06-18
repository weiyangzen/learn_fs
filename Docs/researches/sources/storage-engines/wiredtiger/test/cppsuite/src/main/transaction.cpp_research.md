# sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.cpp

## Purpose
Implements a small transaction state machine over `WT_SESSION` transaction APIs for use by `thread_worker`.

## Important APIs, Types, And Functions
`active`, `begin`, `commit`, `rollback`, `set_needs_rollback`, and `needs_rollback` manage `_in_txn` and `_needs_rollback`.

## Control Flow
`begin` asserts no active transaction, calls `begin_transaction`, and clears rollback state. `commit` asserts the transaction is active and not marked for rollback, calls `commit_transaction`, accepts `0`, `EINVAL`, or `WT_ROLLBACK`, logs nonzero failures, clears `_in_txn`, and returns success status. `rollback` asserts active, calls `rollback_transaction`, clears rollback state, and marks inactive.

## State And Persistence Behavior
State is in-memory only, but it gates all persisted WiredTiger writes done by `thread_worker`. WiredTiger may internally roll back a transaction when commit returns `WT_ROLLBACK`; this wrapper treats the transaction as inactive afterward.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `scoped_session`, and `test_util`. Used exclusively by `thread_worker` as its transaction member.

## Risks And Test Signals
`EINVAL` during commit is tolerated because timestamp races can make a commit timestamp older than the stable timestamp. Callers must not call `commit` after `set_needs_rollback`; `thread_worker::can_commit` enforces that. Unexpected begin/rollback failures abort via `testutil_check`.
