# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AuthorizerCallback.java

## Purpose
Java callback interface for `sqlite3_set_authorizer`.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call(int opId, String s1, String s2, String s3, String s4)`, with all string arguments nullable.

## Control Flow
SQLite invokes the callback while compiling SQL statements. Return values follow SQLite authorizer semantics such as `SQLITE_OK`, `SQLITE_DENY`, and `SQLITE_IGNORE`.

## State And Persistence Behavior
The interface stores no state. Implementations may keep policy state and are retained by the native callback registration on a database handle.

## Dependencies And Integration Points
Depends on `CallbackProxy` and nullability annotations. Installed via `CApi.sqlite3_set_authorizer`.

## Risks And Edge Cases
Thrown exceptions are converted to database-level errors and suppressed. Policy code runs during prepare/compile and must avoid reentrant or slow operations.

## Test Signals
Prepare statements that trigger read, write, pragma, attach, function, and transaction authorizer opcodes and verify return-code handling.
