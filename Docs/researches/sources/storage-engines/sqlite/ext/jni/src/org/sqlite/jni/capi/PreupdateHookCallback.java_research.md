# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/PreupdateHookCallback.java

## Purpose
Java callback interface for SQLite preupdate hook notifications.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `void call(sqlite3 db, int op, String dbName, String dbTable, long iKey1, long iKey2)`.

## Control Flow
When preupdate support is enabled and a hook is installed, SQLite calls this before row changes. Callers can use related `CApi.sqlite3_preupdate_*` methods during callback scope.

## State And Persistence Behavior
No interface state. Callback registration lives on the database handle. Values returned by preupdate old/new APIs are valid only during the hook callback.

## Dependencies And Integration Points
Installed via `CApi.sqlite3_preupdate_hook`. Integrates with `sqlite3_preupdate_count`, `depth`, `blobwrite`, `old`, and `new`.

## Risks And Edge Cases
Feature may be absent unless built with `SQLITE_ENABLE_PREUPDATE_HOOK`. Exceptions are translated to db errors and suppressed. Holding `sqlite3_value` references after callback scope is unsafe.

## Test Signals
Insert/update/delete cases, old/new value extraction during callback, disabled-build `SQLITE_MISUSE` behavior, and exception translation.
