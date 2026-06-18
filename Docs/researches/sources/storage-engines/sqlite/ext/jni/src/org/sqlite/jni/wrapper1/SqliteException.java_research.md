# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqliteException.java

## Purpose
`SqliteException.java` is the runtime exception type for `wrapper1`. It captures SQLite primary error code, extended error code, SQL error offset, and system errno so Java callers can inspect structured SQLite failure state instead of parsing messages.

## Important APIs, types, and functions
- `SqliteException(String msg)` records a caller-supplied message and leaves both result-code fields at `SQLITE_ERROR`.
- `SqliteException(int sqlite3ResultCode)` uses `sqlite3_errstr()` and sets both primary and extended codes to the supplied result code.
- Package-private `SqliteException(sqlite3 db)` snapshots `sqlite3_errmsg`, `sqlite3_errcode`, `sqlite3_extended_errcode`, `sqlite3_error_offset`, and `sqlite3_system_errno`.
- Public constructors from `Sqlite` and `Sqlite.Stmt` bridge high-level wrappers to the native database handle.
- Accessors `errcode()`, `extendedErrcode()`, `errorOffset()`, and `systemErrno()` expose the saved state.

## Control flow
The exception is built at the point where wrapper code detects a non-OK result. Database-aware constructors read all error metadata immediately, making later connection state changes irrelevant to the exception object.

## State and persistence behavior
The object stores immutable-in-practice primitive snapshots but the fields are not declared `final`. It does not own or close database handles. It persists only the message and captured numeric state for Java error handling.

## Dependencies and integration points
It depends on `CApi`, raw `sqlite3`, `Sqlite`, and `Sqlite.Stmt`. `Sqlite.checkRc()`, `Stmt.checkRc()`, failed `open()`, backup setup, read-only checks, and wrapper argument-validation fallbacks create this exception.

## Risks and edge cases
- Constructing from a closed `Sqlite` would pass a null native handle to the package-private constructor via `nativeHandle()`.
- The statement constructor delegates to `stmt.getDb()`, so finalized statements can produce a null database path.
- The plain string constructor does not preserve a non-default code, so callers needing structured SQLite code should use the integer or handle constructor.

## Test signals
`Tester2.testOpenDb1()`, `testExplain()`, `testBusy()`, `testCommitHook()`, and negative prepare/bind paths validate nonzero codes, extended codes, offsets, and expected result-code propagation.
