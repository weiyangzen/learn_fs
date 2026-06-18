<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclsh.c -->
# sources/storage-engines/sqlite/src/test_tclsh.c

## Purpose
`test_tclsh.c` is the bootstrap layer for SQLite's enhanced Tcl test shell, commonly `testfixture`. It keeps test-only extension registration out of `tclsqlite.c` and centralizes initialization of the SQLite Tcl command plus the many `test_*.c` modules linked into the test binary.

## Important APIs, Types, And Functions
The main export is `sqlite3TestInit(Tcl_Interp *interp)`. It declares external initializers for SQLite Tcl bindings, config/test modules, R-Tree, quota, multiplex, superlock, syscall, RBU, FTS, session, expert, recover, integrity-check, and related test helpers. `load_testfixture_extensions()` initializes a named slave interpreter.

## Control Flow
On Unix, initialization raises the core-file size soft limit to the hard limit to aid crash debugging. If the interpreter does not already have `sqlite3`, it calls `Sqlite3_Init()`. It then invokes each linked module initializer in a fixed order, respecting compile-time feature guards for ZipVFS, sessions, and FTS3/4. Finally it registers `load_testfixture_extensions`, whose command looks up a Tcl slave interpreter and recursively calls `sqlite3TestInit()` on it.

## State And Persistence Behavior
This file persists no application data. It mutates Tcl interpreter state by adding commands, modules, functions, and linked variables. On Unix it also changes the process resource limit for core dumps. Repeated initialization is partly guarded only for the base `sqlite3` command; most test module initializers are expected to tolerate registration calls.

## Dependencies And Integration Points
It depends on Tcl, `sqlite3.h`, `tclsqlite.h`, many linked SQLite test modules, and feature macros controlling optional initializers. It integrates all files in this work item into testfixture by calling `SqlitetestOnefile_Init()`, `SqlitetestOsinst_Init()`, `Sqlitetestschema_Init()`, `Sqlitetesttclvar_Init()`, `Sqlitetestrtree_Init()`, `Sqlitequota_Init()`, `SqliteSuperlock_Init()`, and `SqlitetestSyscall_Init()`.

## Risks And Test Signals
Risks include missing linker symbols when build feature macros and object lists diverge, duplicate command registration on repeated init, initializer order dependencies, and Unix-only resource-limit side effects. Test signals include a working testfixture startup, all expected Tcl commands present, slave interpreter initialization, feature-gated commands appearing only when compiled, and no duplicate-registration errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_tclsh.c -->
