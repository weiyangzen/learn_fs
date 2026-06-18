# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/RollbackHookCallback.java

## Purpose
Java callback interface for SQLite rollback hooks.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `void call()`.

## Control Flow
SQLite invokes the hook when a transaction rolls back.

## State And Persistence Behavior
No interface state. Registration is database-handle state until replaced or cleared.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_rollback_hook`, which returns the previous hook object.

## Risks And Edge Cases
Exceptions are translated to database-level errors. Callback code runs during rollback handling and should avoid unsafe connection reentry.

## Test Signals
Explicit rollback and failed commit scenarios, previous-hook return checks, clearing hook, and exception translation.
