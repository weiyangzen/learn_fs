# File Research: sources/os/bsd/netbsd-src/lib/lua/sqlite/sqlite.c

## Summary
Implements a Lua binding for SQLite database connections and prepared statements using userdata-backed `sqlite3 *` and `sqlite3_stmt *` objects.

## Main Responsibilities
- Initialize/shutdown SQLite and report library version/source ID.
- Open databases with `sqlite3_open()` or `sqlite3_open_v2()`.
- Close database handles through explicit method or garbage collection.
- Prepare SQL statements and attach statement metatables.
- Execute SQL directly with `sqlite3_exec()`.
- Expose database error code/message, autocommit state, and change count.
- Bind Lua numbers, strings, and nil values to statement parameters.
- Step, reset, finalize, inspect parameter metadata, and read columns.
- Export SQLite result codes and open flags as Lua constants.

## Key Interfaces
- `luaopen_sqlite(lua_State *L)`.
- Database methods: `close`, `prepare`, `exec`, `errcode`, `errmsg`, `get_autocommit`, `changes`.
- Statement methods: `bind`, `bind_parameter_count`, `bind_parameter_index`, `bind_parameter_name`, `step`, `column`, `column_name`, `column_count`, `reset`, `clear_bindings`, `finalize`.

## Risks
Most SQLite operations return numeric result codes rather than raising Lua errors. Blob columns are returned as `nil`, so blob/null distinction is lost. `stmt_clear_bindings()` clears bindings and then sets the statement pointer to `NULL`, which can make later use of the statement invalid. Integer columns use `sqlite3_column_int()` rather than 64-bit access.
