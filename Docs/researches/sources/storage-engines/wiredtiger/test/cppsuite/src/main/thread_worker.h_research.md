# sources/storage-engines/wiredtiger/test/cppsuite/src/main/thread_worker.h

## Purpose
Declares `thread_worker`, the state container passed to every workload function, and `thread_type`, the operation categories supported by the framework.

## Important APIs, Types, And Functions
`enum class thread_type` covers background compact, checkpoint, custom, insert, read, remove, and update. `thread_worker` exposes CRUD wrappers, transaction wrappers, timing and barrier utilities, collection partition helpers, and public immutable config fields such as `collection_count`, `free_space_target_mb`, `key_count`, `key_size`, `value_size`, `thread_count`, `type`, and `id`.

## Control Flow
The class acts as the operation-loop context. Callers use `running()` to control loops, `sleep()` for throttling, `begin`/`commit`/`rollback` for transaction control, and `finish()` to request shutdown.

## State And Persistence Behavior
Owns a `scoped_session`, operation tracker cursor, statistics cursor, transaction object, op counters, target operation count, optional barrier pointer, and `_running` flag. Holds references or pointers to shared `database`, `timestamp_manager`, and `operation_tracker`.

## Dependencies And Integration Points
Includes `database`, `operation_tracker`, `timestamp_manager`, `configuration`, `scoped_cursor`, `scoped_session`, `transaction`, and `barrier`. This is the common integration object for `database_operation`, workload manager, and test overrides.

## Risks And Test Signals
The class has many public fields to simplify tests, so invariants are convention-based. A moved `scoped_session` is expected to be valid before cursor use. Long-running operations must check `running()` frequently or test shutdown will block on joins.
