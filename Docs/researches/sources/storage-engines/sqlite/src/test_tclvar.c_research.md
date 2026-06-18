<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclvar.c -->
# sources/storage-engines/sqlite/src/test_tclvar.c

## Purpose
`test_tclvar.c` implements a Tcl-backed virtual table module named `tclvar`. It lets SQLite tests query and mutate Tcl global variables through SQL, exercising virtual table scan planning, constraint handling, and update paths.

## Important APIs, Types, And Functions
The virtual table schema is `name`, `arrayname`, `value`, and `fullname PRIMARY KEY WITHOUT ROWID`. Types `tclvar_vtab` and `tclvar_cursor` hold the Tcl interpreter and iteration lists. Core methods are `tclvarConnect()`, `tclvarOpen()`, `tclvarFilter()`, `tclvarNext()`, `tclvarColumn()`, `tclvarBestIndex()`, and `tclvarUpdate()`. Registration is via Tcl command `register_tclvar_module`, which also creates helper Tcl procs `like` and `tclvar_filter_cmd`.

## Control Flow
`xBestIndex` recognizes `name =`, `name MATCH`, and `value GLOB/REGEXP/LIKE` constraints and encodes selected constraints into `idxStr`. `xFilter` calls Tcl `tclvar_filter_cmd` with constraint values to get a list of matching variable names. Cursor iteration walks scalar variables and array entries using `info vars` and `array names`. `xColumn` reconstructs `name`, `arrayname`, current Tcl value, and `fullname`. `xUpdate` deletes, inserts, renames, or changes variables using `Tcl_UnsetVar()` and `Tcl_SetVar()`, with `NULL` value meaning delete.

## State And Persistence Behavior
State is the Tcl global namespace of the registered interpreter. Cursor lists are Tcl objects with reference counts and are released on cursor close or refilter. SQL writes immediately mutate Tcl variables; there is no transaction rollback integration for Tcl state.

## Dependencies And Integration Points
It requires virtual-table support, `sqliteInt.h`, `tclsqlite.h`, Tcl command evaluation, and `getDbPointer()`. It is registered into testfixture by `Sqlitetesttclvar_Init()`.

## Risks And Test Signals
Risks include SQL transaction semantics not matching Tcl variable side effects, `tclvarColumn()` assuming non-null Tcl values, constraint omission controlled by global `::tclvar_set_omit`, helper Tcl proc redefinition, no meaningful rowids, and possible Tcl errors during filtering being ignored. Test signals include scalar and array variables scanning correctly, constraints reducing candidate variables, `omit` behavior for value constraints, insert/update/delete of `fullname`, `NULL` value deletion, and clean reference counting across repeated scans.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclvar.c -->
