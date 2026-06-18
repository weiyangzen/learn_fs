# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_stmt.java

## Purpose
`sqlite3_stmt` is the Java wrapper for C `sqlite3_stmt*` prepared statement handles.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<sqlite3_stmt>` and implements `AutoCloseable`. `close()` calls `CApi.sqlite3_finalize(this)`.

## Control Flow
Prepare APIs create instances. Client code binds values, steps rows, reads columns, resets as needed, and finalizes or uses try-with-resources.

## State and Persistence Behavior
The wrapper carries a native pointer that should become zero after finalization. It does not own resources outside the native statement lifecycle.

## Dependencies and Integration Points
It integrates with `CApi.sqlite3_prepare*`, bind APIs, column APIs, `sqlite3_step`, `sqlite3_reset`, `sqlite3_finalize`, `sqlite3_db_handle`, and trace callbacks.

## Risks
Unfinalized statements can hold locks and memory. Temporary column `sqlite3_value` wrappers are only valid while the statement row is active.

## Test Signals
`Tester1.testPrepare123()`, bind/fetch tests, SQL expansion tests, explain/status tests, and try-with-resources uses validate pointer invalidation, DB-handle lookup after finalize, readonly/busy status, tail parsing, and finalization behavior.
