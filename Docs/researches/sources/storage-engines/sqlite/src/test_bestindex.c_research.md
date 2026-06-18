<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_bestindex.c -->
# sources/storage-engines/sqlite/src/test_bestindex.c

## Purpose
`test_bestindex.c` implements a Tcl-scripted virtual table module named `tcl` for planner and xBestIndex testing. It lets Tcl code declare schemas, inspect `sqlite3_index_info`, choose constraint usage, provide scan SQL, test `IN` handling and RHS extraction, and optionally implement xUpdate and xFindFunction behavior.

## Important APIs, Types, and Functions
Core types are `tcl_vtab`, `tcl_cursor`, `TestFindFunction`, and `TestVtabContext`. Important callbacks are `tclConnect`, `tclBestIndex`, `tclFilter`, `tclNext`, `tclColumn`, `tclRowid`, `tclFindFunction`, `tclFunction`, and `tclUpdate`. `testBestIndexObj()` exposes subcommands `constraints`, `orderby`, `mask`, `distinct`, `in`, `rhs_value`, and `collation`. `register_tcl_module` installs either read-only `tclModule` or update-capable `tclModuleUpdate`.

## Control Flow
Connect/create dequote the module argument or use a default Tcl command, call that command with `xConnect`, and pass its result to `sqlite3_declare_vtab()`. During planning, `tclBestIndex()` creates a temporary Tcl command handle over the live `sqlite3_index_info`, calls the script with `xBestIndex <handle>`, deletes the handle, then interprets the script result as key/value pairs for cost, rows, orderby, idxnum, idxstr, used/omitted constraints, or constraint errors. During scanning, `tclFilter()` calls the script with idx data and argument values, including expanded `sqlite3_vtab_in_first/next()` lists, then prepares returned SQL and advances to the first row.

## State and Persistence Behavior
Each vtab owns a retained Tcl command object, a database pointer, and a list of dynamically allocated function-overload records. Cursors own a prepared statement returned by the script's scan SQL. The update-capable module delegates xUpdate to Tcl and uses the script result as the rowid. No storage is owned by the module itself; persistence depends on SQL the Tcl scripts return or execute.

## Dependencies and Integration Points
The file depends on virtual table APIs including newer planner helpers `sqlite3_vtab_distinct()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, and `sqlite3_vtab_collation()`, plus Tcl object APIs and `getDbPointer()`. It is compiled out when virtual tables are omitted and is registered by `Sqlitetesttcl_Init()`.

## Risks
The module intentionally trusts Tcl scripts to return well-formed even-length key/value lists and valid SQL. `tclBestIndex()` indexes `apElem[ii+1]` while stepping by two, so malformed odd-length results are hazardous unless Tcl list parsing or surrounding tests prevent them. `tclUpdate()` returns a Tcl error code directly as a SQLite virtual table result on failure, which may not map to SQLite codes. Script-controlled SQL can produce column layouts inconsistent with `tclColumn()` expectations.

## Test Signals
Signals include the Tcl callback transcripts, planner handle output for constraints/orderby/colUsed, `idxNum`/`idxStr` received by xFilter, expanded IN-list argument values, returned scan rows, function overload callback results, xUpdate rowids, and virtual table error messages from script failures or `constraint` directives.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_bestindex.c -->
