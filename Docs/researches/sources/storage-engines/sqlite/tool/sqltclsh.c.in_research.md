# sources/storage-engines/sqlite/tool/sqltclsh.c.in

## Purpose
`sqltclsh.c.in` is an input template for building a Tcl shell with SQLite compiled in. It embeds `sqlite3.c`, SQLite append VFS support, the Tcl SQLite extension wrapper, and optionally ZIP/SQL archive extensions, then returns the startup Tcl script from `tool/sqltclsh.tcl`.

## Important APIs, types, and functions
The template defines `TCLSH_INIT_PROC` as `sqlite3_tclapp_init_proc`, adjusts SQLite compile-time options for a small single-threaded shell, and uses template `INCLUDE` directives for generated amalgamation input. `sqlite3_tclapp_init_proc(Tcl_Interp*)` initializes `appendvfs` and registers `sqlar`/`zipfile` auto-extensions when zlib is enabled.

## Control flow
Generated code starts through the Tcl shell harness. During initialization, the custom init proc registers SQLite-related extensions, then returns an embedded Tcl startup script using the `BEGIN_STRING`/`END_STRING` template mechanism.

## State and persistence behavior
This file itself persists no state. At runtime, it registers process-global SQLite auto-extensions and uses append VFS to locate startup scripts in an appended SQLite database, a database passed as the first argument, a `.tcl` file, or falls back to interactive Tcl.

## Dependencies and integration points
It depends on the SQLite source-generation system that expands `INCLUDE`, Tcl headers/runtime via `tclsqlite-ex.c`, `appendvfs.c`, and optional zlib-backed `zipfile.c` and `sqlar.c`. It is integrated with the SQLite build as a specialized shell target.

## Risks and edge cases
Compile-time options deliberately disable SQLite threadsafety and several metadata/deprecated APIs, so this binary is purpose-built and not a general embedded SQLite distribution. Optional archive features depend on `SQLITE_HAVE_ZLIB`. Startup script lookup relies on append VFS behavior and the generated template expansion.

## Test signals
Build success of the generated shell, startup from an appended database, startup from a database argument, direct `.tcl` execution, interactive fallback, and zlib/no-zlib builds are the main validation signals.
