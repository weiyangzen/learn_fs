<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test8.c -->
# sources/storage-engines/sqlite/src/test8.c

## Purpose
`test8.c` implements the `echo` and `echo_v2` virtual table test modules. An echo table mirrors a real backing table, logs module calls into Tcl variables, can inject method failures, and exercises virtual table planning, scanning, writing, transaction, function-overload, rename, and savepoint hooks.

## Important APIs, Types, and Functions
Key types are `echo_vtab`, `echo_cursor`, and `EchoModule`. Major callbacks include `echoCreate`, `echoConnect`, `echoBestIndex`, `echoOpen`, `echoFilter`, `echoNext`, `echoColumn`, `echoRowid`, `echoUpdate`, `echoBegin`, `echoSync`, `echoCommit`, `echoRollback`, `echoFindFunction`, `echoRename`, and v2 savepoint callbacks. Tcl commands are `register_echo_module` and `sqlite3_declare_vtab`.

## Control Flow
Connect/create allocate `echo_vtab`, dequote arguments, derive the backing table name, log arguments, and call `echoDeclareVtab()`. That routine reads the real table SQL from `sqlite_schema`, calls `sqlite3_declare_vtab()`, captures column names, and marks left-most indexed columns. `echoBestIndex()` builds an SQL query in `idxStr` using usable constraints on rowid or indexed columns, sets `argvIndex`, `omit`, `orderByConsumed`, and estimated cost. `echoFilter()` verifies `idxNum` is the hash of `idxStr`, prepares the generated query, binds supplied constraint values, and advances to the first row.

## State and Persistence Behavior
Each virtual table keeps copied backing-table metadata, optional log table name, transaction flag, and Tcl interpreter pointer. Reads come from prepared SELECT statements over the real table. `echoUpdate()` converts virtual table INSERT, UPDATE, DELETE operations into real-table SQL and writes through to the backing table, returning `last_insert_rowid()` for inserts. Transaction callbacks maintain `inTransaction` and log calls. Pattern mode can rename the backing table when the virtual table is renamed.

## Dependencies and Integration Points
The module depends on virtual table APIs, SQLite SQL execution and prepare/bind/finalize, Tcl globals `echo_module`, `echo_module_fail(method,table)`, `echo_module_sync_fail`, `echo_module_begin_fail`, `echo_module_cost`, and optional Tcl procedure `::echo_glob_overload`. `moduleDestroy()` also exercises module destructor behavior by calling `sqlite3_create_function()` during destruction.

## Risks
SQL generated from metadata is quoted in many places but not uniformly for every constructed identifier path, especially pattern rename behavior. Tcl globals drive failure injection and cost behavior, so tests must clean them up. `echoColumn()` assumes SELECT layout with rowid at column zero and data columns offset by one. Transaction assertions require SQLite to invoke hooks in expected order; misuse can abort debug builds.

## Test Signals
Primary signals are entries appended to `::echo_module`, generated `idxStr` SQL, virtual table query plans, injected `echo-vtab-error` messages, real backing table mutations, transaction hook ordering, overloaded `glob` behavior, rename side effects, and v2 savepoint callback coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test8.c -->
