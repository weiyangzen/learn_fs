# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/Sqlite.java

## Purpose
`Sqlite.java` is the high-level Java `wrapper1` database API over `org.sqlite.jni.capi.CApi`. It turns raw JNI SQLite handles into safer Java objects with result-code constants, argument checks, exceptions, `AutoCloseable` resource ownership, Java callback adapters, and nested wrappers for statements, backups, blobs, tracing, hooks, collations, status, and auto-extensions.

## Important APIs, types, and functions
- `Sqlite` wraps one `sqlite3 db` handle and exposes `open()`, `close()`, version/compile-option helpers, status helpers, transaction/introspection helpers, busy/authorizer/hook setup, UDF creation, backup, blob, collation, tracing, and library configuration.
- `Stmt` wraps `sqlite3_stmt` and provides `step()`, `reset()`, SQL text inspection, explain/normalized SQL, parameter binding, column accessors, Java object binding, and finalization.
- `Status`, `TableColumnMetadata`, `Backup`, and `Blob` are typed wrappers around common SQLite output-pointer and handle APIs.
- Callback interfaces include `PrepareMulti`, `ScalarFunction`/`AggregateFunction`/`WindowFunction` registration overloads, `TraceCallback`, `AutoExtension`, `Collation`, `CollationNeeded`, `BusyHandler`, `CommitHook`, `RollbackHook`, `UpdateHook`, `ProgressHandler`, `Authorizer`, `ConfigLog`, and `ConfigSqlLog`.
- Static constants mirror `CApi` SQLite result codes, open flags, status/db-status ops, limits, prepare flags, trace flags, db/lib config options, encodings, data types, and authorizer codes.

## Control flow
`open()` calls `sqlite3_open_v2`, converts failures into `SqliteException`, registers the native handle in `nativeToWrapper`, and runs Java-level auto-extensions before returning. `thisDb()` and nested `thisStmt()`/`thisBlob()` guard against use-after-close. `checkRc()` and `checkRcStatic()` centralize result-code-to-exception mapping, with `SQLITE_NOMEM` promoted to `OutOfMemoryError`.

Statement preparation has two paths: `prepare()` returns exactly one non-null statement and treats empty SQL as an `IllegalArgumentException`; `prepareMulti()` loops through a UTF-8 buffer using the tail offset and passes each parsed statement to a visitor. `Stmt.step()` maps `SQLITE_ROW` to `true`, `SQLITE_DONE` to `false`, and optionally exposes raw busy/locked codes through `step(false)`.

Callback setup builds capi adapter objects and registers them through `sqlite3_create_function`, hook, trace, collation, busy, progress, authorizer, and config APIs. Native callback handles are mapped back to Java wrappers through synchronized maps so trace and collation-needed callbacks can receive wrapper objects rather than only raw handles.

## State and persistence behavior
The class owns native lifetime for database, statement, backup, and blob handles; `close()`/`finalizeStmt()`/`finish()`/`Blob.close()` clear Java references after closing native resources. Static mutable state includes `nativeToWrapper` for database handles, `Stmt.nativeToWrapper` for statement handles, and a `LinkedHashSet` of `AutoExtension` callbacks. Database persistence itself remains SQLite-managed; this wrapper only controls handle lifetime, runtime configuration, callbacks, and native-to-Java associations.

## Dependencies and integration points
The file depends on `org.sqlite.jni.capi` handle classes, `OutputPointer`, and numerous `CApi.sqlite3_*` JNI methods. It integrates with sibling wrapper interfaces/classes such as `ScalarFunction`, `AggregateFunction`, `WindowFunction`, `SqlFunction`, and `SqliteException`. The API is intended to be used with Java try-with-resources and SQLite JNI build options such as `ENABLE_NORMALIZE` and `ENABLE_SQLLOG`.

## Risks and edge cases
- The static wrapper maps are synchronized but not weak; leaked unclosed handles can retain wrappers.
- `Stmt.finalizeStmt()` initializes `rc` to zero and ignores the return from `sqlite3_finalize`, despite comments describing a returned result code.
- `libConfigSqlLog()` checks `hasNormalizeSql` while reporting `SQLITE_ENABLE_SQLLOG`; this appears inconsistent with the nearby `hasSqlLog` variable.
- Callback exceptions have mixed behavior: some propagate as SQLite errors, while collations/config logs suppress exceptions by SQLite API necessity.
- `prepareMulti()` uses the instance field `db` rather than `thisDb()` inside the loop, so a concurrently closed connection could produce lower-level misuse behavior.
- Auto-extension callbacks can recursively call `Sqlite.open()`, which the comments identify as a stack-overflow risk.

## Test signals
`Tester2.java` exercises this class heavily: open/close, db config, prepare/bind/column APIs, scalar/aggregate/window UDFs, keywords, explain, trace, status, auto-extensions, backup, collation-needed, busy handlers, commit/rollback/update hooks, progress, authorizer, blob I/O, prepareMulti, SQL/config logging, multithreaded execution, and thread cache cleanup.
