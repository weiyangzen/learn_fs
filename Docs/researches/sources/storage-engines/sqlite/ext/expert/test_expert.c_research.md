<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/test_expert.c -->
# sources/storage-engines/sqlite/ext/expert/test_expert.c

## Purpose
`test_expert.c` exposes the SQLite expert extension to SQLite's Tcl test harness when `SQLITE_TEST` is enabled. It lets Tcl tests create an expert handle from an existing Tcl SQLite connection and invoke the public expert API through Tcl subcommands.

## Important APIs, Types, And Functions
`TestExpert_Init()` registers the top-level Tcl command `sqlite3_expert_new` unless virtual table support is omitted.

`test_sqlite3_expert_new()` validates the Tcl argument count, resolves a Tcl database command to an `sqlite3*`, creates a unique Tcl command name like `sqlite3expert1`, calls `sqlite3_expert_new()`, and installs the command with `testExpertCmd()` as its dispatcher and `testExpertDel()` as its deletion callback.

`testExpertCmd()` implements `$expert sql SQL`, `$expert analyze`, `$expert count`, `$expert report STMT EREPORT`, and `$expert destroy`. It maps Tcl report names `sql`, `indexes`, `plan`, and `candidates` onto the public `EXPERT_REPORT_*` constants.

`dbHandleFromObj()` extracts the underlying `sqlite3*` from a Tcl SQLite command by reading `Tcl_CmdInfo.objClientData`. `testExpertDel()` destroys the expert handle when the Tcl command is deleted.

## Control Flow
Tcl creates a normal SQLite database command first. A test then calls `sqlite3_expert_new DB`, which creates an expert object and returns a new expert command name. Subsequent Tcl subcommands dispatch through `testExpertCmd()`. Successful `sql` and `analyze` calls return normal Tcl OK status with no additional result unless a report or count is requested. `count` sets an integer result. `report` validates both the statement number and report enum, calls `sqlite3_expert_report()`, and sets the Tcl result to that string. `destroy` deletes the command, which triggers `testExpertDel()` to free C state.

If an expert API returns a non-Tcl-OK code, `testExpertCmd()` prefers the expert error string; otherwise it uses `sqlite3ErrName(rc)` for a symbolic SQLite error. All expert error strings are freed after dispatch.

## State And Persistence Behavior
The Tcl command owns one `sqlite3expert*` through its client data. Deleting the Tcl command is the lifetime boundary. The static `iCmd` counter only ensures unique command names during a test process. The wrapper itself persists no files and does not mutate the database beyond whatever the underlying expert analysis reads or prepares.

## Dependencies
The file is compiled only under `SQLITE_TEST`. Most code is additionally excluded under `SQLITE_OMIT_VIRTUALTABLE`, matching the expert implementation's dependency on virtual tables. It depends on `sqlite3expert.h`, Tcl headers and APIs provided through `tclsqlite.h`, `assert.h`, `string.h`, and SQLite's test-only `sqlite3ErrName()` symbol for fallback error names.

## Integration Points
This is the bridge between SQLite's C expert API and Tcl-based regression tests. Test scripts can create real database schemas with the Tcl SQLite command, instantiate expert analysis against the same handle, add SQL, run analysis, and assert on report text without invoking the standalone `expert.c` program.

## Risks And Edge Cases
`dbHandleFromObj()` assumes the Tcl SQLite command's `objClientData` layout contains an `sqlite3**`, so it is coupled to SQLite's Tcl binding internals. `report` passes a possibly NULL `sqlite3_expert_report()` result to `Tcl_NewStringObj(zReport, -1)`; if Tcl does not tolerate NULL there, out-of-range reports or pre-analysis reports could crash rather than return an empty result. The wrapper has no subcommand for `sqlite3_expert_config()`, so Tcl tests using this binding cannot directly exercise sample configuration through the exposed command set.

## Test Signals
Direct tests should cover creation failure for nonexistent DB handles, subcommand arity errors, invalid report enum names, `count` after loading multiple statements, report values after analysis, destroy cleanup, and behavior when virtual table support is omitted. Broader signal comes from any SQLite Tcl tests that assert recommended indexes and plans through these commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/test_expert.c -->
