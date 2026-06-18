# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_backup.java

## Purpose
`sqlite3_backup` is the Java wrapper for C `sqlite3_backup*` handles used by SQLite online backup APIs.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<sqlite3_backup>` and implements `AutoCloseable`. `close()` calls `CApi.sqlite3_backup_finish(this)`.

## Control Flow
`CApi.sqlite3_backup_init()` creates an instance. Client code steps it through `sqlite3_backup_step()`, inspects page counts, and finishes explicitly or via try-with-resources.

## State and Persistence Behavior
It carries a native pointer without independent ownership. Finishing should invalidate the pointer. The Java object can still exist after native finalization.

## Dependencies and Integration Points
It integrates with backup APIs in `CApi` and the `sqlite3` database handle wrappers for source/destination DBs.

## Risks
Failure to finish leaks backup resources and may keep locks. Double finishing should be handled by the C API wrapper but still signals misuse if result codes are ignored.

## Test Signals
`Tester1.testBackup()` initializes source/destination databases, steps one page at a time until `SQLITE_DONE`, checks page count, verifies `sqlite3_backup_finish()` returns zero and pointer becomes zero, then confirms copied data sums to six.
