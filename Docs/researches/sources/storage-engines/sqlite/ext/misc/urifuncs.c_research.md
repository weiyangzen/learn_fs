# sources/storage-engines/sqlite/ext/misc/urifuncs.c

## Purpose
Exposes selected SQLite filename and URI C APIs as SQL functions for testing and demonstration.

## Important APIs, Types, And Functions
Functions include `sqlite3_db_filename`, `sqlite3_uri_parameter`, `sqlite3_uri_boolean`, `sqlite3_uri_int64`, `sqlite3_uri_key`, `sqlite3_filename_database`, `sqlite3_filename_journal`, and `sqlite3_filename_wal`. Each has a small `func_*` wrapper, and `sqlite3_urifuncs_init()` registers them.

## Control Flow
Each wrapper reads schema/name/default arguments, obtains the current database handle with `sqlite3_context_db_handle()`, resolves the schema filename with `sqlite3_db_filename()`, calls the corresponding SQLite URI/filename API, and returns text, int, or int64. Registration loops through a static table of function names, arities, and callbacks.

## State And Persistence Behavior
No state is stored or modified. Results reflect the connection's current database filenames and URI metadata.

## Dependencies And Integration Points
Depends on SQLite filename URI APIs and scalar function registration. It is useful in tests for URI parameters, WAL/journal filename derivation, and attached database filename introspection.

## Risks And Edge Cases
Functions generally trust schema names and pass through NULL results as SQL NULL via `sqlite3_result_text()`. URI parameter visibility depends on how the database was opened. These functions are not marked deterministic or innocuous, reflecting their connection-dependent behavior.

## Test Signals
Tests should open URI filenames with parameters, attach databases, query all wrappers for valid and invalid schemas, verify default handling for boolean/int64 URI functions, enumerate keys, and compare derived database/journal/WAL filenames.
