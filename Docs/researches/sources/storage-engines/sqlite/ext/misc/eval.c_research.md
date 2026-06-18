# sources/storage-engines/sqlite/ext/misc/eval.c

## Purpose

`eval.c` implements scalar SQL function `eval()`, which executes SQL text recursively on the current database connection and concatenates returned column values into one text result.

## Important APIs, types, and functions

`sqlite3_eval_init()` registers one- and two-argument `eval` functions with `SQLITE_DIRECTONLY`. `EvalResult` owns the accumulated result string, separator string, separator length, allocation size, and used byte count. `sqlEvalFunc()` obtains SQL and optional separator arguments, gets the connection from `sqlite3_context_db_handle()`, and calls `sqlite3_exec()`. `callback()` appends every column value from every returned row, substituting empty strings for SQL NULL values.

## Control flow

`sqlEvalFunc()` defaults the separator to a single space. If either SQL or separator is SQL NULL, the function returns NULL. `sqlite3_exec()` runs the supplied SQL; for each result row, `callback()` grows the buffer when needed, emits the separator before every value after the first, and appends the text value. On execution error, the SQLite error string is returned as a function error. On callback allocation failure, the callback clears state and aborts execution.

## State and persistence

The function has no module-global state, but it can run arbitrary SQL on the current connection, so it may read or mutate database state depending on the input SQL. The accumulated result is heap memory transferred to SQLite as the function result.

## Dependencies and integration points

It depends on `sqlite3_exec()` recursion and direct-only function registration. The direct-only flag prevents use from schema objects such as views and triggers, limiting privilege escalation from attacker-controlled database files.

## Risks

The function executes arbitrary SQL supplied at runtime, so it is intentionally powerful. Recursive use can interact with locks, transactions, user-defined functions, and side effects on the same connection. Results are flattened without column or row structure. Very large result sets can allocate large memory; allocation failure is detected through callback abort behavior.

## Test signals

Tests should verify one- and two-argument separators, NULL SQL/separator behavior, multiple rows and columns flattening, NULL column conversion to empty text, propagation of SQL errors, side-effect statements, direct-only restrictions, and large output allocation failure behavior where test infrastructure permits.
