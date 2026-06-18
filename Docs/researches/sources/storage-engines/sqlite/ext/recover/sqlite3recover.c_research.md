# sources/storage-engines/sqlite/ext/recover/sqlite3recover.c

## Purpose

`sqlite3recover.c` implements the SQLite recovery extension behind the public `sqlite3_recover_*` API. It attempts to extract schema rows, table records, and optional orphan records from a possibly corrupt database and either writes the result to a new output database or emits equivalent SQL through a callback. The implementation is deliberately tolerant of partial corruption: failure to recover some schema or rows is not itself an error, but I/O, allocation, callback, SQLite API, and transaction failures are reported through the recover handle.

## Important APIs, Types, and Functions

The externally visible functions are `sqlite3_recover_init()`, `sqlite3_recover_init_sql()`, `sqlite3_recover_config()`, `sqlite3_recover_step()`, `sqlite3_recover_run()`, `sqlite3_recover_errmsg()`, `sqlite3_recover_errcode()`, and `sqlite3_recover_finish()`. Internally, `recoverInit()` allocates the opaque `sqlite3_recover` object and records the input database name, output URI or SQL callback, and default rowid policy.

Key state types are `RecoverTable`, `RecoverColumn`, `RecoverBitmap`, `RecoverStateW1`, `RecoverStateLAF`, and `RecoverGlobal`. `RecoverTable` stores recovered schema metadata for a table, including original root page, generated/hidden column handling, rowid binding, and intkey versus WITHOUT ROWID shape. `RecoverStateW1` owns prepared statements and accumulated `sqlite3_value` copies while recovering rows for known schema tables. `RecoverStateLAF` owns bitmap, page-map, and insert state for the optional lost-and-found pass. `RecoverGlobal` holds a temporary process-wide VFS method wrapper protected by `SQLITE_MUTEX_STATIC_APP2`.

Important helper families are error/allocation wrappers, SQL functions registered on the output handle, schema setup, data extraction, lost-and-found recovery, and header/VFS repair. Notable functions include `recoverOpenOutput()`, `recoverTransferSettings()`, `recoverCacheSchema()`, `recoverWriteSchema1()`, `recoverWriteDataStep()`, `recoverLostAndFound*()`, `recoverVfsRead()`, and `recoverInstallWrapper()`.

## Control Flow

`sqlite3_recover_step()` is a state machine. In `RECOVER_STATE_INIT`, it opens the output database, registers `sqlite_dbdata`/`sqlite_dbptr` and local SQL functions, begins a read transaction on the input database, transfers durable settings to the output database, attaches the temporary `recovery` database, and populates `recovery.schema` by walking page 1 with `sqlite_dbptr('getpage()')` and decoding schema records through `sqlite_dbdata('getpage()')`. A VFS wrapper is installed for the first attempt so reads of page 1 can be sanitized; if that path yields `SQLITE_NOTADB`, the code retries without the wrapper for encrypted databases.

After initialization, `recoverWriteSchema1()` creates real tables and UNIQUE indexes early, while virtual table entries are written directly into `sqlite_schema`. Each successfully created table is inspected with `PRAGMA table_xinfo()` and possibly `PRAGMA index_xinfo()` so `RecoverTable` can map on-disk fields to insert bindings, skip generated columns, preserve INTEGER PRIMARY KEY rowids, and recognize WITHOUT ROWID layout.

In `RECOVER_STATE_WRITING`, `recoverWriteDataStep()` iterates schema table roots, recursively traverses child pages with `sqlite_dbptr()`, reads record fields with `sqlite_dbdata()`, accumulates one cell at a time, builds or reuses an insert statement matching the number of recovered fields, binds copied values, and writes `INSERT OR IGNORE` rows. SQL callback mode prepares `SELECT` statements that render insert text using `quote()` and `escape_crlf()` instead of modifying an output table directly.

If `SQLITE_RECOVER_LOST_AND_FOUND` is configured, three additional states run: build a used-page bitmap, map unclaimed pages to likely parents and maximum field count, then create and populate a lost-and-found table. `RECOVER_STATE_SCHEMA2` creates delayed views, triggers, and non-UNIQUE indexes, commits output work, ends the input transaction, emits final callback SQL, and frees transient state.

## State and Persistence Behavior

The recover handle owns all per-run memory, prepared statements, duplicated SQL strings, cached page-1 bytes, table metadata, and optional lost-and-found state. The input database is held in a read transaction after initialization; `bCloseTransaction` ensures `finish()` attempts to close it even if recovery is abandoned. The output path uses a separate `sqlite3 *dbOut`; recovery begins by clobbering any existing output database through a backup from a new empty temp database, then applying selected input pragmas such as page size, encoding, auto-vacuum, user version, and application id.

The attached `recovery` database is a transient state store unless the undocumented config opcode `789` supplies a state database name for debugging. Persistent output includes recovered tables, rows, schema objects, and optionally a lost-and-found table. SQL callback mode does not persist directly to `dbOut`; it uses prepared SQL to render an equivalent script while still relying on the output handle for parsing, temp state, dbdata modules, and schema reasoning.

The VFS wrapper is process-global for the input file descriptor during a short initialization window. It rewrites page-1 reads to a known-good SQLite header, preserving selected metadata and caching both disk and synthetic copies so later `getpage(1)` can return the original disk bytes to dbdata consumers when needed.

## Dependencies and Integration Points

This file depends on SQLite core APIs, virtual table support, `sqlite_dbpage` support on the input connection, and `sqlite3_dbdata_init()` from `dbdata.c` to register `sqlite_dbdata` and `sqlite_dbptr` on the output connection. It integrates tightly with SQLite b-tree page formats, varint decoding, page headers, freelist trunk layout, `sqlite_schema`, `PRAGMA table_xinfo`, `PRAGMA index_xinfo`, backup API behavior, file-control `SQLITE_FCNTL_FILE_POINTER` and `SQLITE_FCNTL_RESET_CACHE`, and VFS method dispatch.

The public header is `sqlite3recover.h`; Tcl tests use `test_recover.c` to expose the API. Repository tests under `ext/recover` exercise normal recovery, SQL-script recovery, corrupt input, page-size/header detection, rowid policy, slow-index behavior, clobbering output databases, and OOM/fault handling.

## Risks and Edge Cases

The VFS wrapper is the highest-risk integration point because it mutates a live `sqlite3_file` method table and relies on a static global. The mutex narrows concurrency risk, but overlapping recovery operations on different connections still depend on correct serialized installation and removal. Header synthesis must infer page size and reserved bytes from damaged files without confusing random bytes for valid b-tree pages.

Recovered schema SQL is executed with best effort: `SQLITE_ERROR` from malformed recovered SQL is ignored, but other errors abort. This is intentional but means missing schema can cascade into lost rows. Generated columns, hidden columns, INTEGER PRIMARY KEY aliases, WITHOUT ROWID tables, `sqlite_sequence`, virtual tables, UNIQUE indexes, and delayed non-UNIQUE indexes all have special handling that can drift as SQLite schema semantics evolve.

Lost-and-found recovery trades precision for salvage. Marking the freelist corrupt can recover more records but can also resurrect deleted content. Root-page inference through `recovery.map` is heuristic for orphan pages. SQL callback mode builds SQL text with `quote()` and newline/carriage-return escaping, so correctness depends on complete literal rendering for all recovered SQLite value types.

## Test Signals

Useful test signals are the Tcl recover suites: `recover1.test`, `recoverold.test`, `recoverrowid.test`, `recoverslowidx.test`, `recoversql.test`, `recoverpgsz.test`, `recoverclobber.test`, `recoverbuild.test`, `recovercorrupt*.test`, `recoverfault.test`, and `recoverfault2.test`. These cover output database parity, SQL callback replay, lost-and-found inserts, rowid preservation toggles, delayed versus early index creation, overwritten output files, corrupted headers/pages, page-size detection, freelist assumptions, and allocation fault resilience.
