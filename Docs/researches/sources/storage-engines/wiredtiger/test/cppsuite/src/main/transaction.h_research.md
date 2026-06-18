# sources/storage-engines/wiredtiger/test/cppsuite/src/main/transaction.h

## Purpose
Declares the transaction wrapper used by worker operations to track active and rollback-required state around WiredTiger transactions.

## Important APIs, Types, And Functions
Public methods are `active`, `begin`, `commit`, `rollback`, `set_needs_rollback`, and `needs_rollback`. Private fields are `_in_txn` and `_needs_rollback`.

## Control Flow
The header provides the state-machine interface. Workers begin a transaction, mutate via CRUD helpers, set rollback-needed on recoverable conflicts, and then either commit or rollback based on the wrapper state.

## State And Persistence Behavior
The wrapper does not own sessions or cursors; it receives `scoped_session &` per call. It only stores transaction state flags, while the actual persisted state lives in WiredTiger.

## Dependencies And Integration Points
Includes `scoped_session.h` and `wiredtiger.h`. Integrated by `thread_worker` and indirectly by all workload operation implementations.

## Risks And Test Signals
The interface relies on correct sequencing by callers. It does not expose a reset other than successful rollback or commit, so callers should not abandon an active transaction without resolving it.
