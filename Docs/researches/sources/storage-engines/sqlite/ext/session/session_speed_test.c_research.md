# sources/storage-engines/sqlite/ext/session/session_speed_test.c

## Purpose
`session_speed_test.c` is a standalone benchmark-style test program for SQLite's sessions module. It creates two databases with the same schema, captures insert/update/delete workloads from one database as changesets, and applies those changesets to the second database.

## Important APIs, Types, And Functions
The file contains a small generic command-line parser built around `CmdLineOption` and option type constants. Parser helpers include `option_requires_argument_error()`, `ambiguous_option_error()`, `unknown_option_error()`, `get_integer_option()`, `get_boolean_option()`, and `parse_command_line()`.

SQLite helpers are `abort_due_to_error()`, `execsql()`, and `xConflict()`. `run_test()` is the benchmark core: it creates a session, attaches all tables, prepares one parameterized SQL statement, runs it `nRow` times in a transaction, extracts a changeset with `sqlite3session_changeset()`, commits, and applies the changeset to the second database with `sqlite3changeset_apply()`.

`main()` parses options, defines rowid and WITHOUT ROWID schemas, text/blob and integer workloads, opens two fresh database files, creates schema in both, and runs insert, update, and delete phases.

## Control Flow
The parser supports abbreviated unambiguous options. Recognized options are `-rows`, `-without-rowid`, `-integer`, `-all`, `-database`, and `-cmdline:verbose`.

For each selected combination, `main()` unlinks old database files, opens the primary and replica databases, creates table `t1`, then calls `run_test()` three times using insert, update, and delete SQL. Each `run_test()` captures only the changes made by that phase and applies the resulting changeset immediately to the replica database.

`xConflict()` always returns `SQLITE_CHANGESET_ABORT`, so any apply conflict aborts the benchmark. Errors are intended to terminate the process through `abort_due_to_error()`.

## State And Persistence Behavior
The program writes two database files: the configured `-database` path and a second path with `2` appended. Existing files at those paths are unlinked before each selected run. It does not persist benchmark results beyond stdout and the final database files.

Session state is transient per phase. Each phase creates and deletes its own `sqlite3_session`, changeset buffer, and prepared statement. Database mutations are committed before applying the captured changeset to the second database.

## Dependencies
The file depends on SQLite with sessions enabled, standard C libraries, `<stddef.h>` for `offsetof`, and `<unistd.h>` for `unlink`. It uses `sqlite3_session`, changeset extraction, and changeset apply APIs.

## Integration Points
This utility is a performance and smoke-test harness for the session extension. It exercises rowid and WITHOUT ROWID tables, text/blob payloads and integer payloads, and the full capture/apply path for inserts, updates, and deletes.

## Risks And Edge Cases
There are two notable defects. `abort_due_to_error()` calls `fprintf(stderr, "Error: %d\n");` without passing `rc`, which is undefined behavior and loses the actual error code. In the `-all` loop, the printed/filter loop variables are `bWithoutRowid` and `bInteger`, but schema and SQL arrays are indexed with `o.bWithoutRowid` and `o.bInteger`; as a result, `-all` appears to repeat the option defaults instead of exercising all four combinations.

The program does not time operations directly despite being a speed test; it depends on external timing. It also does not validate that the two databases are equivalent after apply. Option abbreviation is convenient but can become ambiguous if new options share prefixes.

## Test Signals
Tests should run each option combination explicitly and with `-all`, verify database equivalence after insert/update/delete phases, force apply conflicts to validate abort behavior, and run under sanitizers to catch the `fprintf` varargs bug. Parser tests should cover abbreviations, ambiguity, missing arguments, boolean parsing, and verbose command-line echo.
