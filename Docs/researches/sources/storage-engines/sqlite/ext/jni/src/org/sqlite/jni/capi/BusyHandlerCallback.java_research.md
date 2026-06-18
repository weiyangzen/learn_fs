# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/BusyHandlerCallback.java

## Purpose
Callback interface for SQLite busy-handler decisions.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call(int n)`, where `n` is SQLite's busy invocation count.

## Control Flow
SQLite invokes the callback when a database lock cannot be acquired. Return non-zero to retry and zero to stop waiting.

## State And Persistence Behavior
No intrinsic state. Stateful implementations are retained by the database connection registration and may count attempts or consult application cancellation state.

## Dependencies And Integration Points
Installed through `CApi.sqlite3_busy_handler`; related to `sqlite3_busy_timeout`.

## Risks And Edge Cases
Callback must be fast and should not reenter the same connection in unsafe ways. Exceptions follow `CallbackProxy` no-throw semantics and may be suppressed.

## Test Signals
Two-connection lock contention tests, retry count assertions, clearing the handler with null, and timeout interaction checks.
