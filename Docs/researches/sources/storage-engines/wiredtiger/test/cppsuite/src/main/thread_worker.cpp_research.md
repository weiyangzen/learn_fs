# sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.cpp

## Purpose
Implements the per-thread execution context used by workload operations. It wraps configuration, session/cursor state, timestamps, operation tracking, transaction state, throttling, collection partitioning, and generic CRUD helpers.

## Important APIs, Types, And Functions
`type_string` formats `thread_type`. Constructors initialize config-derived fields, the session, optional barrier, tracker cursor, sleep duration, and operation-per-transaction bounds. CRUD helpers are `insert`, `update`, `remove`, and `truncate`. Transaction helpers include `begin`, `try_begin`, `commit`, `rollback`, `try_rollback`, `can_commit`, `active`, `set_commit_timestamp`, and op-count accessors.

## Control Flow
Generic mutations obtain a timestamp, set it on the active transaction when timestamping is enabled, invoke `crud` helpers or WiredTiger truncate, write an operation tracker row, and either increment operation count or mark rollback required on `WT_ROLLBACK`. `begin` randomizes the target operation count for this transaction. `can_commit` requires an active transaction, no rollback requirement, and enough operations. Collection assignment evenly divides database collections by worker id and distributes remainders to low ids.

## State And Persistence Behavior
The worker owns its `scoped_session`, optional operation tracker cursor, optional statistics cursor, transaction wrapper, sleep interval, operation counters, and running flag. Inserts/updates/removes are persisted through WiredTiger cursors and mirrored to operation tracking tables. `truncate` can operate over whole collections or cursor-bounded ranges. The worker itself does not own the `database`, timestamp manager, or tracker.

## Dependencies And Integration Points
Depends on `constants`, `logger`, `random_generator`, `crud`, `transaction`, `scoped_session`, `scoped_cursor`, `operation_tracker`, `timestamp_manager`, and `barrier`. It is consumed by all default and custom operation loops.

## Risks And Test Signals
`op_tracker` is asserted non-null for CRUD helpers, so tests must initialize tracking even if validation is disabled. `set_commit_timestamp` intentionally accepts `EINVAL` as a rollback signal due to timestamp races with stable timestamp movement. `sync` assumes `_barrier` is non-null. The generic `update` records `tracking_operation::INSERT`, making validation model updates overwrite prior value state.
