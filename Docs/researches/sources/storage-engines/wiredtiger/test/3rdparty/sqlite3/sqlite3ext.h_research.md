# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3ext.h

Purpose: SQLite loadable-extension API header vendored under WiredTiger tests. It lets extension shared libraries include `sqlite3ext.h` instead of binding directly to SQLite library symbols, routing SQLite calls through an API pointer table supplied by the host SQLite connection.

Important APIs, types, and functions: the central type is `struct sqlite3_api_routines`, an append-only table of function pointers for SQLite public APIs. `sqlite3_loadext_entry` defines the loadable extension entry signature. The `sqlite3_*` macro block remaps API names such as statement binding, result construction, virtual table, WAL, backup, URI, serialization, and newer client-data APIs to `sqlite3_api->...`. `SQLITE_EXTENSION_INIT1`, `SQLITE_EXTENSION_INIT2`, and `SQLITE_EXTENSION_INIT3` declare, initialize, or import the `sqlite3_api` pointer depending on static vs loadable compilation.

Control flow: an extension compiles with this header, calls `SQLITE_EXTENSION_INIT1` at file scope, receives the host API table in its entry point, then calls `SQLITE_EXTENSION_INIT2(pThunk)` before using normal-looking SQLite APIs. When `SQLITE_CORE` or `SQLITE_OMIT_LOAD_EXTENSION` is defined, the remapping macros are disabled and init macros become no-ops so the same source can be statically linked into SQLite.

State and persistence: the only state introduced here is the process-local `const sqlite3_api_routines *sqlite3_api` pointer used by extension code. Persistent database state is owned by SQLite itself; this header stores no data and performs no I/O.

Dependencies and integration points: depends on `sqlite3.h` for all opaque types and base declarations. It integrates with SQLite's `loadext.c`, dynamically loaded extension entry points, virtual table modules, scalar/aggregate/window functions, VFS APIs, hooks, and memory allocators.

Risks and test signals: the table layout is ABI-sensitive; the file explicitly requires new function pointers to be appended only. Mismatched SQLite versions can expose null or absent tail functions if extension code assumes a newer API than the host provides. Test signals are successful compilation of loadable extensions, correct `SQLITE_EXTENSION_INIT2` use, and runtime loading against the vendored SQLite build.
