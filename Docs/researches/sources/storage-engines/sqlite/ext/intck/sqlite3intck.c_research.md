# sources/storage-engines/sqlite/ext/intck/sqlite3intck.c

## Purpose
`sqlite3intck.c` implements an incremental integrity-check API that checks tables and indexes with generated SQL, reports corruption messages, and allows long checks to be split across read transactions.

## Important APIs, Types, And Functions
Public functions are `sqlite3_intck_open()`, `sqlite3_intck_close()`, `sqlite3_intck_step()`, `sqlite3_intck_message()`, `sqlite3_intck_error()`, `sqlite3_intck_unlock()`, and `sqlite3_intck_test_sql()`. The opaque `sqlite3_intck` struct stores connection/database identity, current object, active check statement, restart key, key arity, corruption message, error state, and generated test SQL. Private helpers prepare/finalize SQL, save errors, save restart keys, find objects, parse CREATE INDEX fragments, and build object-specific check SQL.

## Control Flow
Open allocates state, copies the database name, and registers helper SQL function `parse_create_index()`. Step clears the prior message, finds the next table/index if needed, builds and prepares check SQL, then advances one row. Table checks verify required index entries; index checks verify index entries map back to table rows. `SQLITE_CORRUPT` while reading schema or scanning is converted into a corruption message. Unlock saves a vector restart key and finalizes the statement to release the read transaction. Close finalizes and frees all state.

## State And Persistence
The checker owns transient heap state and one active prepared statement. It can hold a read transaction while active, temporarily registers a connection-local helper function, and toggles `PRAGMA automatic_index` while generating SQL. It does not write database content.

## Dependencies And Integration Points
It uses public SQLite APIs, `sqlite3intck.h`, `sqlite_schema`, `pragma_index_list`, `pragma_index_xinfo`, and the Tcl test bridge in `test_intck.c`.

## Risks
Generated SQL and identifier quoting are complex. Expression/partial index parsing is lightweight. The API forbids concurrent use of the same handle while active. Restart keys for DESC and NULL index fields are subtle. `sqlite3_intck_close()` unregisters `parse_create_index` with arity 1 even though open registers arity 2, which looks suspicious and should be tested.

## Test Signals
Compare with `PRAGMA integrity_check` on normal and corrupted databases; cover rowid/WITHOUT ROWID tables, expression/partial/DESC indexes, NULL keys, attached databases, corrupt schema, object corruption, unlock/resume cycles, error state, test SQL output, and automatic-index restoration.
