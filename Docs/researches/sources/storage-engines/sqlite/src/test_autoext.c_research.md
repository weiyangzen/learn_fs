<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_autoext.c -->
# sources/storage-engines/sqlite/src/test_autoext.c

## Purpose
`test_autoext.c` tests the process-global `sqlite3_auto_extension()` registry. It defines two successful auto-extensions that install SQL functions and one failing extension that returns an error message, then exposes Tcl commands to register, cancel, and reset them.

## Important APIs, Types, and Functions
When loadable extensions are enabled, the file uses `SQLITE_EXTENSION_INIT1/2`, `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, `sqlite3_reset_auto_extension()`, `sqlite3_create_function()`, `sqlite3_mprintf()`, and SQL function callbacks `sqrFunc()` and `cubeFunc()`. Tcl commands include `sqlite3_auto_extension_sqr`, `sqlite3_auto_extension_cube`, `sqlite3_auto_extension_broken`, matching cancel commands, and always `sqlite3_reset_auto_extension`.

## Control Flow
Register commands cast extension initializer functions to the generic auto-extension callback type and return the integer SQLite result. `sqr_init()` and `cube_init()` initialize the extension API table and register `sqr(x)` or `cube(x)`. `broken_init()` initializes the API table, allocates the error string `broken autoext!`, stores it through `pzErrMsg`, and returns non-zero. Cancel commands remove the corresponding initializer from the global registry. Reset clears all registered auto-extensions.

## State and Persistence Behavior
The auto-extension registry is process-global SQLite state, affecting subsequently opened database connections. The SQL functions are registered per connection during extension initialization. The broken initializer tests propagation and freeing of extension error messages. No database files are modified by registration alone.

## Dependencies and Integration Points
The file depends on `sqlite3ext.h`, `tclsqlite.h`, and compile-time `SQLITE_OMIT_LOAD_EXTENSION`. It integrates with connection-open tests that expect new connections to automatically receive `sqr` or `cube`, or fail when the broken extension is active.

## Risks
Global auto-extension state leaks across tests unless reset or canceled. Function pointer casts are standard for this SQLite API but bypass C type checking. The command wrappers do not validate argument count, so extra Tcl arguments are ignored by these object commands. Broken extension registration can intentionally make later opens fail.

## Test Signals
Signals include integer return values from register/cancel, availability of `sqr()` and `cube()` on new connections, failure text from the broken extension, and successful cleanup by `sqlite3_reset_auto_extension`.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_autoext.c -->
