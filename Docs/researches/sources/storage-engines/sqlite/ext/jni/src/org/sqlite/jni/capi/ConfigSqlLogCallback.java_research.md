# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ConfigSqlLogCallback.java

## Purpose
Callback interface for optional SQLite SQL logging support through `SQLITE_CONFIG_SQLLOG`.

## Important APIs, Types, And Functions
Declares `void call(sqlite3 db, String msg, int msgType)`.

## Control Flow
If the native library is built with `SQLITE_ENABLE_SQLLOG`, SQLite invokes this callback for SQL log events after global installation.

## State And Persistence Behavior
No interface state. The callback is global process-level SQLite config state and receives database handle wrappers for events.

## Dependencies And Integration Points
Installed through `CApi.sqlite3_config(ConfigSqlLogCallback)`. If SQL log support is absent, the wrapper returns `SQLITE_MISUSE`.

## Risks And Edge Cases
Feature availability depends on native build flags. Like other global config, it is not thread-safe relative to concurrent SQLite use.

## Test Signals
Build-flag-sensitive tests: expect callback delivery when enabled and `SQLITE_MISUSE` when disabled.
