## sources/storage-engines/sqlite/test/testloadext.c

### Purpose
`testloadext.c` is a loadable extension used to verify that runtime extension loading can call newer SQLite extension APIs. It exposes SQL functions that exercise `sqlite3_set_errmsg()` and 64-bit database status reporting.

### Important APIs, types, and functions
The file uses `sqlite3ext.h`, `SQLITE_EXTENSION_INIT1`, and `SQLITE_EXTENSION_INIT2`. `seterrmsgfunc()` implements `set_errmsg(CODE, MSG)` by calling `sqlite3_context_db_handle()`, `sqlite3_set_errmsg()`, and then returning a formatted tuple of the API return code, current `sqlite3_errcode()`, and current `sqlite3_errmsg()`. `tempbuf_spill_func()` implements `tempbuf_spill(RESET)` using `sqlite3_db_status64()` with `SQLITE_DBSTATUS_TEMPBUF_SPILL`. `sqlite3_testloadext_init()` registers both SQL functions.

### Control flow
SQLite loads the shared object and calls `sqlite3_testloadext_init()`. The initializer stores the extension API table, ignores the extension error-message pointer, registers `set_errmsg`, then registers `tempbuf_spill`, returning the first non-OK registration result.

### State and persistence behavior
The extension does not create persistent schema or files. It mutates only the connection error state through `sqlite3_set_errmsg()` and optionally resets an in-memory DB status counter when `tempbuf_spill(1)` is called.

### Dependencies and integration points
The file is built as a platform-specific shared library and loaded by SQLite extension-loading tests. It depends on the extension API surface rather than direct core symbols, making it a compatibility test for exported API slots.

### Risks and test signals
Risks are API availability mismatches with older SQLite builds, incorrect entry-point naming, and platform-specific symbol export issues. Test signals are successful load, successful function registration, expected `set_errmsg()` return text, and changing `tempbuf_spill()` values when temp-buffer spill behavior is exercised.
