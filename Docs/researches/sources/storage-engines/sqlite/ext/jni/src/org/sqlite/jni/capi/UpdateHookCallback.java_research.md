# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/UpdateHookCallback.java

## Purpose
`UpdateHookCallback` represents the Java callback for `sqlite3_update_hook()`.

## Important APIs, Types, and Functions
The single method `void call(int opId, String dbName, String tableName, long rowId)` reports insert, update, or delete operations with database/table names and affected rowid. It extends `CallbackProxy`.

## Control Flow
Registration through `CApi.sqlite3_update_hook()` installs a callback and returns the previously installed hook. SQLite invokes `call()` after eligible row changes.

## State and Persistence Behavior
The interface has no internal state. Implementations may close over counters or expected operation codes. Installed hook identity is retained by the JNI proxy until replaced, cleared, or the database closes.

## Dependencies and Integration Points
It depends on `CallbackProxy` and integrates with C API constants such as `SQLITE_INSERT`, `SQLITE_UPDATE`, and `SQLITE_DELETE`.

## Risks
Exceptions from callbacks are translated into database-level errors. Hook callbacks run in SQLite execution context, so implementations should be lightweight and avoid reentrant misuse.

## Test Signals
`Tester1.testUpdateHook()` validates old-hook return semantics, insert/update/delete operation IDs, clearing the hook, replacing with another hook, and continued database operation after hook changes.
