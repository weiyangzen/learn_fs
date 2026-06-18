# sources/storage-engines/sqlite/tool/sqlite3_analyzer.c.in

## Purpose

Template source for the `sqlite3_analyzer` executable, which embeds SQLite, Tcl integration, and the `spaceanal.tcl` script to report database space utilization.

## Important APIs, control flow, and dependencies

The template sets `TCLSH_INIT_PROC` to `sqlite3_analyzer_init_proc`. When `INCLUDE_SQLITE3_C` is active, it includes `sqlite3.c` with analyzer-friendly compile-time options such as `SQLITE_ENABLE_DBSTAT_VTAB`, `SQLITE_THREADSAFE=0`, omitted load extensions, omitted shared cache, and disabled memory status. It always includes `$ROOT/src/tclsqlite.c`, and on Windows includes `sqlite3_stdio` plus a replacement `puts` command, `subst_puts()`, that writes through `sqlite3_fputs()`. `sqlite3_analyzer_init_proc()` installs the Windows `puts` shim when needed and returns the embedded `spaceanal.tcl` script between `BEGIN_STRING` and `END_STRING`.

## State, persistence, and integration

This is not compiled directly as ordinary C; it is processed by SQLite's build/template machinery that expands `INCLUDE`, `IFDEF`, `ELSE`, `ENDIF`, and string markers. Runtime behavior comes from the embedded Tcl script and SQLite's `dbstat` virtual table. The analyzer reads target databases and writes reports to stdout/stderr.

## Risks and test signals

Risks include build-template expansion errors, mismatch between embedded SQLite compile options and the analyzer script's expectations, Tcl command behavior differences on Windows, and stale `spaceanal.tcl` coupling. Test signals include successful generation/compilation both with bundled `sqlite3.c` and external `sqlite3.h`, analyzer execution on known databases, dbstat availability, and Windows output behavior through the substituted `puts`.
