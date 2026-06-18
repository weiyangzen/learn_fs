# sources/storage-engines/sqlite/ext/intck/sqlite3intck.h

## Purpose
`sqlite3intck.h` declares the incremental integrity-check API and documents its coverage, stepping model, transaction behavior, and test-only SQL introspection.

## Important APIs, Types, And Functions
It defines opaque `sqlite3_intck` and declares `sqlite3_intck_open()`, `sqlite3_intck_close()`, `sqlite3_intck_step()`, `sqlite3_intck_message()`, `sqlite3_intck_unlock()`, `sqlite3_intck_error()`, and `sqlite3_intck_test_sql()`.

## Control Flow
The intended flow is open, repeatedly step while `SQLITE_OK`, read any message after each step, call `sqlite3_intck_error()` when stepping ends, then close. `sqlite3_intck_unlock()` may be called between steps to release and later reopen a read transaction.

## State And Persistence
The header owns no state, but documents that the implementation owns an ongoing handle and may hold a read transaction. Callers should not use the same database handle until the check object is closed.

## Dependencies And Integration Points
It includes `sqlite3.h`, uses SQLite result codes, and supports C++ callers with `extern "C"`. It is used by the implementation and Tcl tests.

## Risks
Misuse includes concurrent database-handle use, continuing after an error state, reading messages at the wrong time, or assuming this is as thorough as `PRAGMA integrity_check`.

## Test Signals
Compile from C and C++, validate the documented lifecycle, exercise unlock, default database name behavior, error reporting, and test-only SQL retrieval.
