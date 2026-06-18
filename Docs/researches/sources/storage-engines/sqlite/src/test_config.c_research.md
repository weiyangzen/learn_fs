<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_config.c -->
# sources/storage-engines/sqlite/src/test_config.c

## Purpose
`test_config.c` publishes SQLite compile-time configuration to the Tcl test environment. It fills the global `sqlite_options` array and links selected numeric limits/constants as read-only Tcl variables so tests can skip or adapt to the current build.

## Important APIs, Types, and Functions
The main routine is `set_options(Tcl_Interp*)`, called by `Sqliteconfig_Init()`. It uses `Tcl_SetVar2()` for many feature flags and `Tcl_LinkVar()` through the `LINKVAR` macro for constants such as `SQLITE_MAX_LENGTH`, `SQLITE_MAX_COLUMN`, `SQLITE_DEFAULT_PAGE_SIZE`, `SQLITE_MAX_PAGE_COUNT`, `SQLITE_MAX_WORKER_THREADS`, and `TEMP_STORE`. `STRINGVALUE()` stringifies numeric macros.

## Control Flow
Initialization executes a long series of `#ifdef`, `#ifndef`, and numeric macro checks. Each branch writes a string value, usually `"1"` or `"0"`, into `sqlite_options(feature)`. Some options write macro values, such as `CONFIG_SLOWDOWN_FACTOR`, default autovacuum, worker thread limit, and `SQLITE_ENABLE_SETLK_TIMEOUT`. After feature publication, constant variables are linked as read-only Tcl integers, followed by compiler markers for `_MSC_VER` or `__GNUC__` when present.

## State and Persistence Behavior
State is entirely in the Tcl interpreter: the global `sqlite_options` array and linked read-only variables. There is no database persistence. The values reflect compile-time and platform settings for the loaded testfixture process and do not change after initialization.

## Dependencies and Integration Points
The file depends on `sqliteLimit.h`, `sqliteInt.h`, optional `os_win.h`, `tclsqlite.h`, and a broad set of SQLite compile-time macros. It is a central integration point for Tcl tests that use `$sqlite_options(name)` guards to determine whether features such as JSON, FTS, WAL, virtual tables, loadable extensions, shared cache, UTF16, snapshots, sessions, or debug options are available.

## Risks
Because this file mirrors many build macros manually, it can drift from the actual build surface when features are added, renamed, or combined. Some options are derived from compound conditions, for example session requires both session and preupdate hook. Linked variables point to static const locals declared inside the function block, which is safe because they have static storage but easy to misread. Incorrect flags can cause tests to run in unsupported builds or be skipped accidentally.

## Test Signals
Signals are the contents of `sqlite_options`, read-only Tcl constants, and the assertion that `sqlite3_threadsafe()` matches `SQLITE_THREADSAFE`. Tests typically consume this file indirectly by checking options before executing feature-specific cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_config.c -->
