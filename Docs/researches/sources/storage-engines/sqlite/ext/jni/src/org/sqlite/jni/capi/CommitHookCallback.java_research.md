# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CommitHookCallback.java

## Purpose
Java callback interface for SQLite commit hooks.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call()`. Return semantics follow `sqlite3_commit_hook`.

## Control Flow
SQLite calls the hook during transaction commit. A non-zero return requests commit rollback.

## State And Persistence Behavior
No interface state. Registered callback state is associated with a database handle until changed.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_commit_hook`, which returns the previous hook object.

## Risks And Edge Cases
Exceptions are translated to database-level errors. Commit hooks run inside transaction processing and should avoid unsafe reentrancy.

## Test Signals
Transactions with zero/non-zero hook returns, previous-hook return checks, rollback behavior, and exception translation.
