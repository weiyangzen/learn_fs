# Research: sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009011`: lines 1-5283, `Docs/researches/chunks/subset-b-009011_research.md`
- `subset-b-009012`: lines 5284-10756, `Docs/researches/chunks/subset-b-009012_research.md`
- `subset-b-009013`: lines 10757-17068, `Docs/researches/chunks/subset-b-009013_research.md`
- `subset-b-009014`: lines 17069-22525, `Docs/researches/chunks/subset-b-009014_research.md`
- `subset-b-009015`: lines 22526-30978, `Docs/researches/chunks/subset-b-009015_research.md`
- `subset-b-009016`: lines 30979-39365, `Docs/researches/chunks/subset-b-009016_research.md`
- `subset-b-009017`: lines 39366-47008, `Docs/researches/chunks/subset-b-009017_research.md`
- `subset-b-009018`: lines 47009-55194, `Docs/researches/chunks/subset-b-009018_research.md`
- `subset-b-009019`: lines 55195-62132, `Docs/researches/chunks/subset-b-009019_research.md`
- `subset-b-009020`: lines 62133-68993, `Docs/researches/chunks/subset-b-009020_research.md`
- `subset-b-009021`: lines 68994-76298, `Docs/researches/chunks/subset-b-009021_research.md`
- `subset-b-009022`: lines 76299-83658, `Docs/researches/chunks/subset-b-009022_research.md`
- `subset-b-009023`: lines 83659-91725, `Docs/researches/chunks/subset-b-009023_research.md`
- `subset-b-009024`: lines 91726-99549, `Docs/researches/chunks/subset-b-009024_research.md`
- `subset-b-009025`: lines 99550-107363, `Docs/researches/chunks/subset-b-009025_research.md`
- `subset-b-009026`: lines 107364-114787, `Docs/researches/chunks/subset-b-009026_research.md`
- `subset-b-009027`: lines 114788-122462, `Docs/researches/chunks/subset-b-009027_research.md`
- `subset-b-009028`: lines 122463-130124, `Docs/researches/chunks/subset-b-009028_research.md`
- `subset-b-009029`: lines 130125-137437, `Docs/researches/chunks/subset-b-009029_research.md`
- `subset-b-009030`: lines 137438-144608, `Docs/researches/chunks/subset-b-009030_research.md`
- `subset-b-009031`: lines 144609-151744, `Docs/researches/chunks/subset-b-009031_research.md`
- `subset-b-009032`: lines 151745-158971, `Docs/researches/chunks/subset-b-009032_research.md`
- `subset-b-009033`: lines 158972-165680, `Docs/researches/chunks/subset-b-009033_research.md`
- `subset-b-009034`: lines 165681-172668, `Docs/researches/chunks/subset-b-009034_research.md`
- `subset-b-009035`: lines 172669-179062, `Docs/researches/chunks/subset-b-009035_research.md`
- `subset-b-009036`: lines 179063-186320, `Docs/researches/chunks/subset-b-009036_research.md`
- `subset-b-009037`: lines 186321-194031, `Docs/researches/chunks/subset-b-009037_research.md`
- `subset-b-009038`: lines 194032-202197, `Docs/researches/chunks/subset-b-009038_research.md`
- `subset-b-009039`: lines 202198-210096, `Docs/researches/chunks/subset-b-009039_research.md`
- `subset-b-009040`: lines 210097-218440, `Docs/researches/chunks/subset-b-009040_research.md`
- `subset-b-009041`: lines 218441-226497, `Docs/researches/chunks/subset-b-009041_research.md`
- `subset-b-009042`: lines 226498-234635, `Docs/researches/chunks/subset-b-009042_research.md`
- `subset-b-009043`: lines 234636-242624, `Docs/researches/chunks/subset-b-009043_research.md`
- `subset-b-009044`: lines 242625-251111, `Docs/researches/chunks/subset-b-009044_research.md`
- `subset-b-009045`: lines 251112-259629, `Docs/researches/chunks/subset-b-009045_research.md`
- `subset-b-009046`: lines 259630-262899, `Docs/researches/chunks/subset-b-009046_research.md`

## Chunk Research

### subset-b-009011: lines 1-5283

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 1-5283

## Scope

This chunk covers the beginning of SQLite's `sqlite3.c` amalgamation as vendored under WiredTiger's test third-party tree. The range starts with the amalgamation banner for SQLite 3.50.4, enters the embedded `sqliteInt.h`, includes platform setup fragments (`msvc.h`, `vxworks.h`, large-file and compiler feature macros), and then enters the embedded public `sqlite3.h` header. It ends in the public API documentation for prepared-statement parameter lookup, just after `sqlite3_bind_parameter_name()` and before the rest of the bind-parameter APIs.

The code in this chunk is mostly declarations, public API contracts, preprocessor configuration, and generated API documentation comments. Implementations of the declared APIs appear later in the amalgamation.

## Purpose

The opening amalgamation block makes this single C file a complete SQLite core translation unit and records the upstream SQLite version and Fossil source identifier. The early `sqliteInt.h` section prepares compilation for the host platform before any system headers are included: it defines amalgamation visibility (`SQLITE_CORE`, `SQLITE_AMALGAMATION`, `SQLITE_PRIVATE`), coverage-comment conventions, Tcl calling convention defaults, MSVC warning and alignment workarounds, VxWorks feature switches, POSIX large-file support, compiler-version detection, C99 math availability, GNU/OpenBSD feature macros, fallthrough annotations, MinGW time ABI compatibility, and the optional `SQLITE_CUSTOM_INCLUDE` hook.

The embedded `sqlite3.h` section exposes the public C API used by applications and by WiredTiger's SQLite test dependency. In this range it defines version metadata, core opaque handle types, result/open/sync/lock/file-control constants, the VFS and file I/O interfaces, initialization/configuration contracts, memory allocator hooks, connection configuration constants, basic connection and statement lifecycle APIs, error reporting, limits, SQL preparation, statement inspection, value/function-context opaque types, and the first prepared-statement binding APIs.

## Important APIs, Types, and Data

- `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, and `SQLITE_SOURCE_ID`: identify this vendored SQLite as 3.50.4 from source id `2025-07-30 19:33:53 ...`; `sqlite3_version[]`, `sqlite3_libversion()`, `sqlite3_sourceid()`, and `sqlite3_libversion_number()` expose the same information at runtime.
- `sqlite3`: opaque database connection handle. `sqlite3_open()`, `sqlite3_open16()`, and `sqlite3_open_v2()` construct it; `sqlite3_close()` and `sqlite3_close_v2()` destroy it with different behavior for outstanding statements, blobs, and backups.
- `sqlite3_stmt`: opaque prepared statement handle. The documented lifecycle is prepare, bind, step, reset for reuse, and finalize; this chunk declares prepare and statement-inspection routines but not `sqlite3_step()` or finalization yet.
- `sqlite3_value` and `sqlite3_context`: opaque value and SQL-function execution context types used by later function, column, and result APIs.
- `sqlite3_int64` and `sqlite3_uint64`: portable 64-bit integer typedefs selected from `SQLITE_INT64_TYPE`, MSVC/Borland `__int64`, or `long long`.
- `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3_vfs`: core VFS ABI. `sqlite3_file` stores a `pMethods` table; `sqlite3_io_methods` defines close/read/write/truncate/sync/size/lock/unlock/file-control/sector/device/shared-memory/mmap fetch hooks; `sqlite3_vfs` defines open/delete/access/full-path/dynamic-loading/randomness/sleep/time/system-call override hooks.
- Result code constants: primary result codes (`SQLITE_OK`, `SQLITE_ERROR`, `SQLITE_BUSY`, `SQLITE_IOERR`, `SQLITE_CORRUPT`, `SQLITE_ROW`, `SQLITE_DONE`, and others) plus many extended codes for I/O, locking, busy, readonly, constraint, notice, warning, authorization, and symlink cases.
- Open, lock, sync, I/O capability, shared-memory, and file-control constants: `SQLITE_OPEN_*`, `SQLITE_LOCK_*`, `SQLITE_SYNC_*`, `SQLITE_IOCAP_*`, `SQLITE_SHM_*`, and `SQLITE_FCNTL_*` define the contract between the core, VFS implementations, and `sqlite3_file_control()`.
- Initialization and configuration APIs: `sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_os_init()`, `sqlite3_os_end()`, `sqlite3_config()`, and `sqlite3_db_config()`. Associated constants include `SQLITE_CONFIG_*` for global allocator, mutex, page-cache, logging, URI, mmap, sorter, and memory-database settings, and `SQLITE_DBCONFIG_*` for per-connection flags such as foreign keys, triggers, load extensions, defensive mode, trusted schema, statement scanstatus, ATTACH permissions, and comment handling.
- `sqlite3_mem_methods`: application-supplied allocator vtable with `xMalloc`, `xFree`, `xRealloc`, `xSize`, `xRoundup`, `xInit`, `xShutdown`, and `pAppData`.
- Execution and diagnostics APIs in this range: `sqlite3_exec()`, `sqlite3_compileoption_used()`, `sqlite3_compileoption_get()`, `sqlite3_threadsafe()`, `sqlite3_extended_result_codes()`, `sqlite3_last_insert_rowid()`, `sqlite3_set_last_insert_rowid()`, `sqlite3_changes()`, `sqlite3_changes64()`, `sqlite3_total_changes()`, `sqlite3_total_changes64()`, `sqlite3_interrupt()`, `sqlite3_is_interrupted()`, `sqlite3_complete()`, `sqlite3_complete16()`, `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, `sqlite3_setlk_timeout()`, `sqlite3_get_table()`, `sqlite3_free_table()`, formatted-string helpers, allocation helpers, memory high-water APIs, `sqlite3_randomness()`, authorizer hooks, trace/progress hooks, URI filename helpers, error APIs, and runtime limit APIs.
- Preparation and binding APIs declared before the chunk boundary: `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, UTF-16 prepare variants, `sqlite3_sql()`, `sqlite3_expanded_sql()`, optionally `sqlite3_normalized_sql()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, `sqlite3_bind_blob()`, `sqlite3_bind_blob64()`, `sqlite3_bind_double()`, `sqlite3_bind_int()`, `sqlite3_bind_int64()`, `sqlite3_bind_null()`, `sqlite3_bind_text()`, `sqlite3_bind_text16()`, `sqlite3_bind_text64()`, `sqlite3_bind_value()`, `sqlite3_bind_pointer()`, `sqlite3_bind_zeroblob()`, `sqlite3_bind_zeroblob64()`, `sqlite3_bind_parameter_count()`, and `sqlite3_bind_parameter_name()`.

## Control Flow

There is very little runtime control flow in this chunk because it is largely header material. The active compile-time control flow is preprocessor-driven:

1. The amalgamation guard defines SQLite core/amalgamation symbols and default static linkage for private symbols.
2. Platform sections select MSVC warning suppressions and allocator alignment behavior, VxWorks-specific mutex/load-extension/locking defaults, POSIX large-file macros, compiler version macros, C99 math availability, GNU/OpenBSD feature macros, and MinGW `_USE_32BIT_TIME_T` compatibility.
3. If `SQLITE_CUSTOM_INCLUDE` is defined, a caller-specified header is included after platform setup but before most SQLite feature options take effect.
4. Public API declarations are conditionally exposed or stubbed based on build macros such as `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_FLOATING_POINT`, and `SQLITE_ENABLE_NORMALIZE`.

The documented runtime flows are contracts for later implementations. `sqlite3_exec()` is described as prepare/step/finalize over one or more SQL statements, stopping on errors or callback aborts. `sqlite3_open_v2()` maps flags and URI parameters into connection and VFS behavior. Busy handlers loop by retrying while the callback returns nonzero, unless SQLite detects a deadlock risk. Prepared statements are documented as a lifecycle of prepare, bind, step, reset, and finalize. Binding routines are documented to validate parameter indexes, handle destructor/static/transient lifetimes, copy or reference inputs according to the destructor argument, and leave bindings intact across `sqlite3_reset()`.

## State and Persistence Behavior

The declarations in this chunk define several state domains but do not implement their mutation directly:

- Global process state: initialization/shutdown state, global configuration set by `sqlite3_config()`, threading mode, custom memory allocator/mutex/page-cache/log hooks, URI defaults, mmap defaults, memory status tracking, PRNG seeding, and VFS registration state. Many global configuration options are only valid before `sqlite3_initialize()` or after `sqlite3_shutdown()`.
- Per-connection state: open database handles, lookaside configuration, foreign-key/trigger/view/load-extension flags, defensive and trusted-schema flags, busy and setlk timeouts, last-insert rowid, change counters, interrupt state, authorizer callback, trace callback, progress handler, error code/message/offset, runtime limits, and statement lists.
- VFS/file state: open-file method tables, lock state transitions, shared-memory locks, device capability declarations, file-control operations, WAL/journal/database filename associations, URI query metadata, and optional system-call override tables for testing.
- Persistent storage effects: this chunk itself does not write durable state, but it defines the contracts used later for database creation/opening, rollback journals, WAL files, shared-memory files, checkpoint-on-close behavior, file synchronization, atomic-write controls, powersafe-overwrite behavior, mmap limits, temporary files, and destructive reset-via-VACUUM workflows.

Several documented persistence-sensitive behaviors are important: closing a connection with an open transaction rolls it back; `sqlite3_close_v2()` can defer destruction until outstanding objects finish; WAL files may persist or be removed based on file-control and connection-close settings; `immutable=1` disables locking/change detection and is only safe for truly immutable files; `nolock=1` can corrupt a database if concurrent writers exist; `sqlite3_interrupt()` can roll back an interrupted write transaction; and VFS short reads must zero-fill unread bytes or corruption can follow.

## Dependencies and Integration Points

This vendored file is an upstream SQLite amalgamation embedded under WiredTiger's test tree. WiredTiger code should treat it as third-party source and rely on the SQLite C API rather than editing internal declarations.

The chunk depends on C preprocessor configuration from compiler flags and optional custom includes. It expects platform headers and ABI details for MSVC, MinGW, VxWorks, POSIX large-file support, C99 math, GNU extensions, OpenBSD feature macros, and optional Tcl/test integration. It exposes integration points for application code through the stable SQLite C API, and for lower layers through the VFS and memory/mutex/page-cache vtables.

Key integration surfaces include:

- Application SQL access: connection open/close, `sqlite3_exec()`, prepare APIs, statement binding, and result/error APIs.
- Host resource management: custom memory allocators, page-cache configuration, static heap/pagecache buffers, and memory accounting.
- Concurrency and locking: compile-time thread safety, runtime threading modes, per-connection busy handlers, blocking lock timeouts, VFS lock transitions, and shared-memory WAL locks.
- Filesystem abstraction: `sqlite3_vfs` registration and file method callbacks for database, journal, WAL, temp, transient, and subjournal files.
- Security controls: authorizer callbacks, run-time limits, defensive mode, trusted schema, load-extension gating, ATTACH create/write gating, and SQL comment gating.
- Testing hooks: coverage annotation comments, VFS system-call override hooks, `SQLITE_FCNTL_WIN32_SET_HANDLE`, `SQLITE_CONFIG_SQLLOG`, custom allocators for out-of-memory simulation, and compile-option diagnostics.

## Risks and Edge Cases

- This file is third-party amalgamated source. Local modifications risk diverging from upstream SQLite and can break subtle ABI, macro, and generated-documentation assumptions.
- Header/library mismatch is explicitly guarded by version APIs; embedding code must ensure the paired `sqlite3.h` declarations and compiled `sqlite3.c` implementation are from the same SQLite source id.
- Many APIs have undefined behavior for invalid handles, finalized statements, invalid `sqlite3_filename` pointers, wrong VFS method versions, invalid `sqlite3_open_v2()` flag combinations, negative BLOB lengths, bad text encodings, or incorrect bind destructor lifetimes.
- Threading behavior is easy to misuse. `sqlite3_threadsafe()` reports only compile-time mutex availability, not runtime `sqlite3_config()` changes. Shared connection access can make last-insert rowid, change counts, and error reporting unpredictable unless serialized.
- VFS implementations must honor ABI details exactly: set `sqlite3_file.pMethods` on failed opens, zero-fill short reads, respect lock transition rules, avoid reserved file-control opcode conflicts, implement shared-memory locks consistently, and return `SQLITE_NOTFOUND` for unsupported file controls.
- Configuration timing matters. Most `sqlite3_config()` options return `SQLITE_MISUSE` after initialization, and `sqlite3_db_config(SQLITE_DBCONFIG_LOOKASIDE)` can fail with `SQLITE_BUSY` if lookaside memory is in use.
- URI filename options can change durability or safety. `immutable=1` and `nolock=1` trade correctness guarantees for special deployment assumptions; wrong use can produce stale reads or corruption.
- Error strings and expanded SQL strings have different ownership. `sqlite3_errmsg()` memory is SQLite-owned and volatile, while `sqlite3_exec()` error strings and `sqlite3_expanded_sql()` results require `sqlite3_free()`.
- Busy handlers, authorizers, trace callbacks, logger callbacks, and progress handlers are constrained against reentrant modification of the invoking connection; violating that contract is undefined or explicitly unsupported.

## Test Signals

Useful validation signals for this chunk are mostly compile/API compatibility and behavioral tests that exercise the declarations later implemented in the amalgamation:

- Build the SQLite amalgamation in the WiredTiger test configuration and confirm no platform macro regressions, missing prototypes, or calling-convention mismatches.
- Assert version consistency using `sqlite3_libversion_number() == SQLITE_VERSION_NUMBER`, `sqlite3_libversion()`, and `sqlite3_sourceid()` when tests link this vendored SQLite.
- Exercise connection lifecycle: open/close, close with outstanding statements returning `SQLITE_BUSY`, `sqlite3_close_v2()` deferred cleanup, and automatic rollback on close with an open transaction.
- Exercise VFS contracts with a custom or shim VFS: failed `xOpen()` cleanup behavior, zero-filled short reads, lock transitions, URI parameter retrieval, WAL/journal filename translation, file-control pass-through, mmap fetch/unfetch, and shared-memory locking.
- Exercise configuration timing: successful pre-initialize `sqlite3_config()` calls, `SQLITE_MISUSE` for non-anytime options after initialization, lookaside reconfiguration returning `SQLITE_BUSY` while in use, and no-op/unsupported behavior for omitted features.
- Exercise safety controls: authorizer deny/ignore paths, lowered `sqlite3_limit()` values for untrusted SQL, `SQLITE_DBCONFIG_DEFENSIVE`, trusted-schema restrictions, load-extension gating, and ATTACH create/write controls.
- Exercise statement flow: prepare variants, SQL text introspection, expanded SQL ownership, readonly/explain/busy reporting, binding all scalar/blob/text/pointer/zeroblob variants, destructor invocation on bind failures where specified, index range errors, and persistence of bindings across reset.
- Exercise concurrency and interruption: busy timeout behavior, deadlock-avoidance returning `SQLITE_BUSY`, blocking-lock timeout where enabled, `sqlite3_interrupt()` from another thread, and stable error reporting when callers hold the database mutex.

### subset-b-009012: lines 5284-10756

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 5284-10756

## Scope

This chunk covers a large section of the SQLite amalgamation's public C API declarations and their embedded reference documentation. It starts in the prepared-statement binding/column API area, continues through application-defined functions, collations, hooks, virtual tables, incremental BLOB I/O, VFS and mutex APIs, status/diagnostic APIs, custom page cache, online backup, unlock notification, string helpers, WAL checkpointing, and virtual-table query-planning helpers. The chunk ends mid-comment in the prepared-statement scan-status opcode documentation, so the `SQLITE_SCANSTAT_*` definitions and scan-status functions continue in the next chunk.

This range is declaration-heavy. It does not contain implementation bodies, allocation algorithms, pager logic, B-tree logic, or WiredTiger code. Its role in this repository is to expose the SQLite C ABI used by SQLite's own test build vendored under WiredTiger's third-party test dependency.

## Purpose

The purpose of this section is to define the callable interface and behavioral contract for major SQLite subsystems:

- Prepared statement execution, reset/finalize, bind lookup, result-column metadata, and typed column extraction.
- Application-defined scalar, aggregate, and window functions, including argument access, per-aggregate state, auxiliary data caching, client-data storage, result construction, and subtype propagation.
- Collation registration and collation-needed callbacks.
- Connection and statement state inspection, including autocommit, transaction state, attached database names/files, statement enumeration, and runtime/status counters.
- Commit, rollback, update, autovacuum, WAL, unlock-notify, and extension-loading hooks.
- Virtual table module registration, cursor/table/index ABI, incremental BLOB I/O, and virtual-table planner helper APIs.
- Pluggable VFS discovery/registration, mutex implementation contracts, custom page-cache implementation contracts, online backup, and WAL checkpointing.

The declarations are part of SQLite's public ABI. Downstream C/C++ code compiles against these prototypes and constants, while the actual behavior is implemented later in the amalgamation.

## Important APIs, Types, and Constants

### Prepared Statements and Result Columns

The chunk starts with statement parameter and column APIs:

- `sqlite3_bind_parameter_index()` maps a named host parameter to a 1-based bind index.
- `sqlite3_clear_bindings()` resets all bound host parameters on a statement to SQL NULL.
- `sqlite3_column_count()` and `sqlite3_data_count()` report result-column counts for prepared statements and the current row.
- `sqlite3_column_name()` and `sqlite3_column_name16()` return UTF-8/UTF-16 result-column labels.
- `sqlite3_column_database_name*()`, `sqlite3_column_table_name*()`, and `sqlite3_column_origin_name*()` expose origin metadata when built with `SQLITE_ENABLE_COLUMN_METADATA`.
- `sqlite3_column_decltype()` and `sqlite3_column_decltype16()` expose declared table-column type text for result columns that originate directly from table columns.
- `sqlite3_step()`, `sqlite3_reset()`, and `sqlite3_finalize()` define the normal prepared-statement lifecycle.
- `sqlite3_column_blob()`, `sqlite3_column_double()`, `sqlite3_column_int()`, `sqlite3_column_int64()`, `sqlite3_column_text()`, `sqlite3_column_text16()`, `sqlite3_column_value()`, `sqlite3_column_bytes()`, `sqlite3_column_bytes16()`, and `sqlite3_column_type()` read values from the current `SQLITE_ROW`.

The type constants `SQLITE_INTEGER`, `SQLITE_FLOAT`, `SQLITE_TEXT`/`SQLITE3_TEXT`, `SQLITE_BLOB`, and `SQLITE_NULL` define the five fundamental SQL runtime value classes. The comments emphasize pointer lifetime and type-conversion hazards: text/blob pointers may be invalidated by later conversion calls, and `sqlite3_column_type()` is only meaningful before conversions.

### SQL Functions, Values, and Results

Application-defined functions are declared through:

- `sqlite3_create_function()`, `sqlite3_create_function16()`, `sqlite3_create_function_v2()`, and `sqlite3_create_window_function()`.
- Encoding constants `SQLITE_UTF8`, `SQLITE_UTF16LE`, `SQLITE_UTF16BE`, `SQLITE_UTF16`, `SQLITE_ANY`, and `SQLITE_UTF16_ALIGNED`.
- Function flags `SQLITE_DETERMINISTIC`, `SQLITE_DIRECTONLY`, `SQLITE_INNOCUOUS`, `SQLITE_SUBTYPE`, `SQLITE_RESULT_SUBTYPE`, and `SQLITE_SELFORDER1`.

Function argument/value APIs include `sqlite3_value_blob()`, numeric/text extractors, `sqlite3_value_pointer()`, byte-count accessors, `sqlite3_value_type()`, `sqlite3_value_numeric_type()`, `sqlite3_value_nochange()`, `sqlite3_value_frombind()`, `sqlite3_value_encoding()`, `sqlite3_value_subtype()`, `sqlite3_value_dup()`, and `sqlite3_value_free()`. These APIs operate on `sqlite3_value` objects, with strong caveats around protected versus unprotected values, thread affinity, pointer invalidation, and out-of-memory detection.

Function context APIs include:

- `sqlite3_aggregate_context()` for per-aggregate storage.
- `sqlite3_user_data()` and `sqlite3_context_db_handle()` for callback context.
- `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()` for caching data associated with function arguments.
- `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` for named connection-scoped wrapper-library data.

Result APIs include `sqlite3_result_blob*()`, `sqlite3_result_double()`, `sqlite3_result_error*()`, `sqlite3_result_error_toobig()`, `sqlite3_result_error_nomem()`, `sqlite3_result_error_code()`, integer/null/text result setters, `sqlite3_result_value()`, `sqlite3_result_pointer()`, `sqlite3_result_zeroblob*()`, and `sqlite3_result_subtype()`. `SQLITE_STATIC` and `SQLITE_TRANSIENT` define whether SQLite borrows or copies caller-owned buffers.

### Collations, Extension Loading, Hooks, and Connection State

Collation APIs are `sqlite3_create_collation()`, `sqlite3_create_collation_v2()`, `sqlite3_create_collation16()`, `sqlite3_collation_needed()`, and `sqlite3_collation_needed16()`. The `xCompare` callback must implement stable total-order semantics; otherwise SQLite behavior is undefined.

Connection and process-level APIs in this range include:

- `sqlite3_sleep()`, `sqlite3_temp_directory`, `sqlite3_data_directory`, and Win32 directory setters.
- `sqlite3_get_autocommit()`, `sqlite3_db_handle()`, `sqlite3_db_name()`, `sqlite3_db_filename()`, `sqlite3_db_readonly()`, and `sqlite3_txn_state()` with `SQLITE_TXN_NONE`, `SQLITE_TXN_READ`, and `SQLITE_TXN_WRITE`.
- `sqlite3_next_stmt()` for iterating prepared statements associated with a connection.
- `sqlite3_commit_hook()`, `sqlite3_rollback_hook()`, `sqlite3_update_hook()`, and `sqlite3_autovacuum_pages()`.
- `sqlite3_enable_shared_cache()`, `sqlite3_release_memory()`, `sqlite3_db_release_memory()`, `sqlite3_soft_heap_limit64()`, `sqlite3_hard_heap_limit64()`, and deprecated `sqlite3_soft_heap_limit()`.
- `sqlite3_table_column_metadata()` for schema/type/collation/constraint metadata.
- `sqlite3_load_extension()`, `sqlite3_enable_load_extension()`, `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, and `sqlite3_reset_auto_extension()`.

Security-sensitive warnings appear around extension loading, shared cache, and client-data exposure. The comments recommend enabling only the C extension-loading API through `SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION` when possible so SQL injection cannot call the SQL-level `load_extension()`.

### Virtual Tables and Incremental BLOB I/O

Virtual table types and ABI structs include `sqlite3_vtab`, `sqlite3_index_info`, `sqlite3_vtab_cursor`, and `sqlite3_module`. `sqlite3_module` defines the callback table for virtual table implementations: creation/connection, best-index planning, cursor open/filter/next/eof/column/rowid, update, transaction callbacks, function overloading, rename, savepoint callbacks, shadow-name checks, and integrity checks.

`sqlite3_index_info` is the planner contract passed to `xBestIndex()`. It carries WHERE constraints, ORDER BY terms, output constraint usage, selected index number/string, cost, estimated rows, scan flags, and column-usage mask. Constants include:

- `SQLITE_INDEX_SCAN_UNIQUE` and `SQLITE_INDEX_SCAN_HEX`.
- Constraint operators such as `SQLITE_INDEX_CONSTRAINT_EQ`, range operators, `MATCH`, `LIKE`, `GLOB`, `REGEXP`, `NE`, `IS`, `ISNULL`, `ISNOTNULL`, `LIMIT`, `OFFSET`, and function constraints.

Module registration and helper APIs include `sqlite3_create_module()`, `sqlite3_create_module_v2()`, `sqlite3_drop_modules()`, `sqlite3_declare_vtab()`, `sqlite3_overload_function()`, `sqlite3_vtab_config()`, `sqlite3_vtab_on_conflict()`, `sqlite3_vtab_nochange()`, `sqlite3_vtab_collation()`, `sqlite3_vtab_distinct()`, `sqlite3_vtab_in()`, `sqlite3_vtab_in_first()`, `sqlite3_vtab_in_next()`, and `sqlite3_vtab_rhs_value()`. `SQLITE_VTAB_CONSTRAINT_SUPPORT`, `SQLITE_VTAB_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_USES_ALL_SCHEMAS` configure virtual-table behavior.

Incremental BLOB I/O declares opaque `sqlite3_blob` plus `sqlite3_blob_open()`, `sqlite3_blob_reopen()`, `sqlite3_blob_close()`, `sqlite3_blob_bytes()`, `sqlite3_blob_read()`, and `sqlite3_blob_write()`. These APIs expose a fixed-size BLOB handle bound to a database/table/column/row, with separate readonly/readwrite open modes and explicit offset/length checks.

### VFS, Mutex, File Control, Testing, Strings, and Status

VFS APIs `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, and `sqlite3_vfs_unregister()` manage process-global VFS objects. Mutex APIs include `sqlite3_mutex_alloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, optional debug checks `sqlite3_mutex_held()` and `sqlite3_mutex_notheld()`, `sqlite3_db_mutex()`, mutex type constants, and `sqlite3_mutex_methods` for custom mutex implementations.

Low-level and diagnostic APIs include `sqlite3_file_control()`, `sqlite3_test_control()`, many `SQLITE_TESTCTRL_*` opcodes, SQL keyword helpers, case-insensitive/string pattern helpers, and `sqlite3_log()`. `sqlite3_test_control()` and its opcodes are explicitly unstable and test-only.

Dynamic string APIs define opaque `sqlite3_str` plus `sqlite3_str_new()`, `sqlite3_str_finish()`, append/reset helpers, and status/value accessors. Runtime status APIs include `sqlite3_status()`, `sqlite3_status64()`, `sqlite3_db_status()`, and `sqlite3_stmt_status()` with `SQLITE_STATUS_*`, `SQLITE_DBSTATUS_*`, and `SQLITE_STMTSTATUS_*` constants. These counters expose memory, page-cache, parser stack, lookaside, cache hits/misses/writes/spills, deferred foreign keys, full-scan steps, sort operations, auto-indexing, VM steps, reprepare/run counts, Bloom filter hits/misses, and statement memory use.

### Page Cache, Backup, Unlock Notify, and WAL

Custom page cache types include opaque `sqlite3_pcache`, `sqlite3_pcache_page`, `sqlite3_pcache_methods2`, and obsolete `sqlite3_pcache_methods`. The `sqlite3_pcache_methods2` table defines `xInit`, `xShutdown`, `xCreate`, `xCachesize`, `xPagecount`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, `xDestroy`, and `xShrink`. These callbacks are registered with `sqlite3_config(SQLITE_CONFIG_PCACHE2, ...)` outside this chunk.

Online backup declares opaque `sqlite3_backup` plus `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, `sqlite3_backup_remaining()`, and `sqlite3_backup_pagecount()`. The lifecycle is init, one or more step calls, then finish exactly once.

`sqlite3_unlock_notify()` registers a callback for shared-cache lock release when `SQLITE_ENABLE_UNLOCK_NOTIFY` is enabled. Its documentation defines callback coalescing, immediate invocation races, deadlock detection, and the `DROP TABLE`/`DROP INDEX` special case where there may be no blocking connection.

WAL APIs include `sqlite3_wal_hook()`, `sqlite3_wal_autocheckpoint()`, `sqlite3_wal_checkpoint()`, and `sqlite3_wal_checkpoint_v2()`. Checkpoint modes are `SQLITE_CHECKPOINT_PASSIVE`, `SQLITE_CHECKPOINT_FULL`, `SQLITE_CHECKPOINT_RESTART`, and `SQLITE_CHECKPOINT_TRUNCATE`.

## Control Flow and Lifecycles

This chunk declares APIs rather than implementing control flow, but it documents several externally visible lifecycles:

- Prepared statements: prepare occurs earlier in the file, then callers bind parameters, call `sqlite3_step()` until `SQLITE_ROW`, `SQLITE_DONE`, or an error, optionally read columns while the row is valid, call `sqlite3_reset()` to run again, and eventually call `sqlite3_finalize()`.
- SQL functions: registration installs callback pointers on a connection. SQLite invokes callbacks during statement execution. Aggregate functions allocate state with `sqlite3_aggregate_context()`, scalar functions may cache argument-derived auxiliary data, and result APIs set the callback result or error.
- Collations and modules: registration stores caller-provided function tables or compare callbacks on a connection. The `_v2` variants add destructors for caller-owned context, but `sqlite3_create_collation_v2()` has a documented destructor-on-failure exception.
- Virtual tables: SQLite calls `xCreate`/`xConnect`, then `xBestIndex()` during planning, then cursor methods `xOpen`, `xFilter`, repeated `xColumn`/`xRowid`/`xNext`, and `xClose` during execution. Transaction and savepoint callbacks mirror surrounding SQL transaction state.
- Incremental BLOBs: `sqlite3_blob_open()` creates a handle, read/write calls operate within fixed blob bounds, `sqlite3_blob_reopen()` retargets the row, and `sqlite3_blob_close()` releases resources.
- Online backup: `sqlite3_backup_init()` opens the backup object and destination write transaction, repeated `sqlite3_backup_step()` calls transfer pages, and `sqlite3_backup_finish()` commits or rolls back and releases the object.
- WAL: commit hooks fire after WAL commits; autockpt is implemented as a WAL hook; explicit checkpoint modes vary in whether they wait for writers/readers and whether the WAL is reset or truncated.

## State and Persistence Behavior

Most persistent state controlled by these APIs lives in SQLite database connections, prepared statements, database files, WAL files, or application-owned callback contexts:

- Statement state includes bound values, VM execution position, current row values, cached column-name encodings, reset/finalize status, and statement counters.
- Connection state includes registered SQL functions, collations, modules, hooks, client data, extension-loading flags, autocommit/transaction state, attached database handles, page/cache/memory counters, VFS bindings, and WAL hook/autocheckpoint settings.
- Database-file state includes table contents, schema metadata, BLOB contents, journal/WAL frames, checkpoint progress, autovacuum free-page handling, and backup destination contents.
- Virtual table state is owned by module implementations through `sqlite3_vtab` and `sqlite3_vtab_cursor` subclasses. SQLite owns the ABI fields and calls into the module; the module owns any persistent backing store and must honor transaction/constraint semantics.
- Page-cache state is owned by the registered `sqlite3_pcache_methods2` implementation, which caches page buffers and per-page extras for SQLite pager users.
- Callback context pointers and auxiliary/client data carry application state and destructor responsibilities; misuse can leak memory, double free, or expose process control through scripting bindings.

The comments repeatedly document pointer lifetime. Many returned pointers are valid only until statement finalization, automatic reprepare, reset/finalize, the next call requesting a different encoding, the next string-builder mutation, or the end of a virtual-table callback. Several APIs are thread-affine or undefined if used concurrently on the same statement/connection without SQLite's required serialization.

## Dependencies and Integration Points

This chunk depends on types and result-code constants declared earlier in `sqlite3.c`, including `sqlite3`, `sqlite3_stmt`, `sqlite3_value`, `sqlite3_context`, `sqlite3_vfs`, `sqlite3_mutex`, `sqlite3_filename`, integer typedefs, result codes, open flags, and configuration opcodes.

In this repository, the source path is under `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/`, so the practical integration point is WiredTiger's test-side vendored SQLite dependency rather than MongoDB's production storage engine. The declarations are still broad public SQLite ABI and may be exercised by:

- SQLite TCL/C tests or WiredTiger compatibility tests that compile the vendored amalgamation.
- Any local test harness that opens SQLite databases, prepares statements, binds values, reads result rows, registers SQL functions/collations, or uses backup/WAL APIs.
- Extension or virtual-table tests that depend on the `sqlite3_module`, `sqlite3_index_info`, BLOB, page-cache, mutex, VFS, unlock-notify, and WAL contracts.

Because this is an amalgamation, implementations for these declarations live later in the same file. Merge-level research should connect this chunk to adjacent chunks containing earlier type definitions and later function bodies, scan-status declarations, pager/VDBE/virtual-table implementation details, and compile-option guards.

## Risks

- This range is public ABI surface. Changing prototypes, constants, struct layouts, or callback signatures can break source or binary compatibility for SQLite consumers and extensions.
- Pointer lifetime is a major hazard. Column values, `sqlite3_value` text/blob data, dynamic-string buffers, metadata strings, virtual-table RHS values, and backup/status pointers can become invalid after later SQLite API calls.
- Many APIs are thread-sensitive. Misusing unprotected `sqlite3_value` objects, invoking SQLite APIs inside unlock-notify callbacks, sharing a destination backup connection concurrently, or using statement column APIs across reset/finalize/step boundaries can produce undefined behavior or deadlock.
- Extension loading and client-data APIs are security-sensitive. Exposing them to untrusted scripting or enabling SQL-level `load_extension()` can permit arbitrary native code execution.
- Virtual-table planning flags are correctness-sensitive. Incorrect `xBestIndex()` `omit`, `orderByConsumed`, `SQLITE_INDEX_SCAN_UNIQUE`, `sqlite3_vtab_distinct()`, IN handling, or constraint-support decisions can yield wrong query answers or incorrect rollback behavior.
- WAL checkpoint modes change concurrency behavior. FULL/RESTART/TRUNCATE can block on writers/readers and invoke busy handlers; PASSIVE may leave work incomplete. Hook replacement between `sqlite3_wal_hook()` and `sqlite3_wal_autocheckpoint()` is easy to miss.
- Custom mutex and page-cache methods are low-level extension points. Violating initialization, thread-safety, fetch/unpin/rekey/truncate, or memory-allocation requirements can corrupt database state or crash the process.
- The chunk ends mid scan-status documentation, so a final per-file report must reconcile this boundary with the following chunk before claiming full scan-status API coverage.

## Test and Validation Signals

Useful validation signals for this chunk are API, ABI, and behavioral tests rather than unit tests for local implementation bodies:

- Compile tests should include `sqlite3.c` and representative consumers that call prepared-statement, function, collation, hook, virtual-table, BLOB, backup, WAL, and status APIs.
- Statement lifecycle tests should cover bind lookup/clear, repeated `sqlite3_step()`, column type conversion, `sqlite3_data_count()`, `sqlite3_reset()`, and `sqlite3_finalize()` error propagation.
- Function tests should register scalar, aggregate, and window functions; exercise `sqlite3_value_*`, aggregate context, auxdata caching/destructors, pointer passing, subtypes, error result codes, and text/blob destructor modes.
- Virtual-table tests should cover `xBestIndex()` constraint mapping, `orderByConsumed`, DISTINCT/GROUP BY modes, RHS literal extraction, all-at-once IN constraints, `xUpdate()` conflict policy, `sqlite3_vtab_nochange()`, and module destruction.
- BLOB tests should validate readonly/readwrite handles, row retargeting, out-of-range reads/writes, schema-change expiry, and handle closure.
- Backup tests should cover incremental stepping, retryable `SQLITE_BUSY`/`SQLITE_LOCKED`, fatal IO/NOMEM/READONLY paths, source changes during backup, and destination connection isolation.
- WAL tests should cover hook replacement, autocheckpoint threshold behavior, PASSIVE/FULL/RESTART/TRUNCATE checkpoint modes, attached-database checkpointing, busy-handler behavior, and output frame counts.
- Extension-loading tests should verify default-disabled behavior and the difference between `sqlite3_enable_load_extension()` and connection-level database configuration.
- Status and diagnostic tests should query/reset `sqlite3_status*`, `sqlite3_db_status()`, `sqlite3_stmt_status()`, keyword helpers, string comparison/pattern helpers, and log callback behavior.

### subset-b-009013: lines 10757-17068

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 10757-17068

## Scope

This chunk starts near the end of the public `sqlite3.h` API declarations and continues into the first internal SQLite amalgamation headers embedded in `sqliteInt.h`. The covered range includes:

- Statement scan-status constants and APIs.
- Cache flush, pre-update hook, low-level system error, WAL snapshot, serialization/deserialization, R-Tree, session/changeset, and FTS5 extension APIs.
- The close of `sqlite3.h` and the beginning of internal configuration defaults, platform/compiler macros, parser token numbers, generic hash-table contracts, OS wrapper declarations, pager declarations, btree declarations, and the start of VDBE/opcode declarations.

This range is mostly interface and macro contract code, not implementation bodies. It defines ABI/API surfaces and private subsystem boundaries that later source sections implement.

## Purpose

The public part of the chunk exposes optional SQLite features to embedders and extensions. It describes how applications inspect query-plan execution statistics, flush dirty cache pages mid-transaction, register pre-update callbacks, use WAL snapshots, serialize databases, register R-Tree geometry callbacks, capture and apply session changesets, and extend FTS5 with custom tokenizers and auxiliary functions.

The internal part prepares SQLite's core build environment and subsystem interfaces. It fixes compile-time limits, normalizes compiler/platform behavior, assigns parser token IDs, defines small shared data structures such as `Hash`, declares the VFS/OS access wrapper layer, and specifies the pager, btree, and VDBE contracts used by the actual storage and bytecode engine implementations later in the amalgamation.

Within WiredTiger, this is vendored third-party SQLite test infrastructure. The chunk is not WiredTiger's storage engine, but it affects the SQLite library and shell behavior used by the vendored SQLite test tree.

## Important APIs, Types, and Functions

- `SQLITE_SCANSTAT_*`, `sqlite3_stmt_scanstatus()`, `sqlite3_stmt_scanstatus_v2()`, and `sqlite3_stmt_scanstatus_reset()` expose predicted and measured query-plan loop data when `SQLITE_ENABLE_STMT_SCANSTATUS` is compiled in. The `SQLITE_SCANSTAT_COMPLEX` flag broadens reporting from loop nodes to all `EXPLAIN QUERY PLAN` elements.
- `sqlite3_db_cacheflush()` asks all schemas on a connection to write eligible dirty pager-cache pages to disk without changing the connection error state.
- `sqlite3_preupdate_hook()` plus `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and `sqlite3_preupdate_blobwrite()` define the optional pre-update event API used by the sessions module.
- `sqlite3_system_errno()` exposes the OS-level error associated with recent I/O/open failures.
- `sqlite3_snapshot`, `sqlite3_snapshot_get()`, `sqlite3_snapshot_open()`, `sqlite3_snapshot_free()`, `sqlite3_snapshot_cmp()`, and `sqlite3_snapshot_recover()` define the experimental WAL snapshot lifecycle.
- `sqlite3_serialize()` and `sqlite3_deserialize()` move an entire schema database image between SQLite and caller-owned memory. Flags include `SQLITE_SERIALIZE_NOCOPY`, `SQLITE_DESERIALIZE_FREEONCLOSE`, `SQLITE_DESERIALIZE_RESIZEABLE`, and `SQLITE_DESERIALIZE_READONLY`.
- `sqlite3_rtree_geometry_callback()`, `sqlite3_rtree_query_callback()`, `sqlite3_rtree_geometry`, and `sqlite3_rtree_query_info` expose R-Tree custom geometry/query callbacks, including scored traversal state and within/partly-within/full-within outcomes.
- `sqlite3_session`, `sqlite3_changeset_iter`, and the `sqlite3session_*`, `sqlite3changeset_*`, `sqlite3changegroup_*`, and `sqlite3rebaser_*` declarations define change capture, changeset iteration, patchset generation, conflict-aware apply, change grouping, rebasing, and streaming variants.
- `Fts5ExtensionApi`, `Fts5Context`, `Fts5PhraseIter`, `fts5_extension_function`, `fts5_tokenizer_v2`, legacy `fts5_tokenizer`, and `fts5_api` define FTS5 extension hooks for auxiliary functions and tokenizers, including locale-aware tokenizer APIs and versioned API tables.
- `Hash` and `HashElem` are SQLite's generic internal string-keyed hash table types, with `sqlite3HashInit()`, `sqlite3HashInsert()`, `sqlite3HashFind()`, `sqlite3HashClear()`, and iteration macros.
- `TK_*` constants from `parse.h` assign parser token numbers for SQL syntax and expression operators. These values bind the tokenizer, lemon parser, expression tree code, and VDBE code generator.
- `sqlite3Os*` declarations wrap `sqlite3_file` and `sqlite3_vfs` methods behind SQLite's internal OS abstraction, including file I/O, locking, shared-memory WAL operations, mmap fetch/unfetch, dynamic loading, randomness, sleep, and current time.
- `Pager`, `DbPage`, `Pgno`, `PAGER_*` constants, and `sqlite3Pager*` declarations define page-cache, rollback journal, WAL, savepoint, sync, mmap, and page reference operations.
- `Btree`, `BtCursor`, `BtShared`, `BtreePayload`, `BTREE_*` constants, and `sqlite3Btree*` declarations define database btree opening, transactions, schema storage, table/index creation, cursor movement, payload reads/writes, metadata, WAL checkpoints, integrity checks, and shared-cache mutex entry/leave routines.
- `Vdbe`, `VdbeOp`, `VdbeOpList`, `SubProgram`, and `SubrtnSig` begin the VDBE contract. `P4_*`, `P5_Constraint*`, `COLNAME_*`, `ADDR()`, and initial `OP_*` opcodes describe instruction operands, ownership rules, result-column metadata slots, unresolved label encoding, and bytecode numbers.

## Control Flow

There is little direct runtime control flow in this chunk. The important flow is contractual:

- Scan-status callers prepare and run a statement, then query each loop or query-plan element by index. `idx == -1` may request whole-query information; out-of-range indexes leave output unchanged and return nonzero.
- `sqlite3_db_cacheflush()` walks schemas on the connection and attempts to flush non-pinned dirty pages. If locks cannot be obtained for one database, it may skip that database and continue, returning `SQLITE_BUSY` if skips occurred without other errors.
- Pre-update hooks are installed per connection, invoked before real-table row changes, and allow old/new column access only during the callback. Blob writes are reported as delete-style callbacks with `sqlite3_preupdate_blobwrite()` identifying the written column.
- Snapshot flow is explicit: a non-autocommit WAL read transaction is required or opened by `sqlite3_snapshot_get()`, the returned object is later used by `sqlite3_snapshot_open()`, compared with `sqlite3_snapshot_cmp()`, released with `sqlite3_snapshot_free()`, and recovered into the wal-index with `sqlite3_snapshot_recover()` when needed.
- Session flow starts with `sqlite3session_create()`, optional object configuration, table attach/filter setup, change recording through the pre-update hook, extraction through changeset or patchset APIs, iteration via `sqlite3changeset_start()` and `sqlite3changeset_next()`, and application through `sqlite3changeset_apply()` or `_v2()` with filter and conflict callbacks.
- Changeset conflict handling is callback-driven. A conflict handler returns `SQLITE_CHANGESET_OMIT`, `SQLITE_CHANGESET_REPLACE`, or `SQLITE_CHANGESET_ABORT`, and `_apply_v2()` can return rebase information for later `sqlite3rebaser_*` processing.
- FTS5 extension flow is version-table based. Applications obtain `fts5_api`, register tokenizers or auxiliary functions, then FTS5 calls tokenizer methods for document, query, prefix-query, or auxiliary tokenization and calls extension functions with `Fts5ExtensionApi` accessors for current-row and current-query metadata.
- Internal subsystem flow is layered. SQL text is tokenized into `TK_*` values, compiled into `VdbeOp` bytecode, VDBE opcodes call btree cursor operations, btree calls pager page and transaction operations, pager calls OS wrappers, and OS wrappers invoke the active VFS and `sqlite3_file` methods.

## State and Persistence Behavior

The public API declarations in this range mostly describe state owned elsewhere:

- Scan-status counters live on prepared statements and can be reset without re-preparing the statement.
- Cache flushing affects dirty pager-cache pages and durable database files, but not the connection's stored error code/message.
- Pre-update hooks are connection-local singleton callbacks. Session objects also use that hook, making application pre-update hooks and sessions mutually exclusive on the same connection.
- WAL snapshots are heap-owned handles representing historical WAL state. They are only meaningful while WAL content needed by the snapshot remains available and has not been checkpointed away.
- Serialization returns either a caller-freed heap copy or a temporary no-copy pointer into SQLite's contiguous in-memory representation. Deserialization replaces a schema with an in-memory database image and can transfer ownership of the buffer to SQLite.
- Session objects accumulate primary-key based change records in memory, then compare those records to current database content when generating changesets. Changes to rows with NULL primary-key fields are omitted, and changes to `sqlite_stat1` have special encoding compatibility behavior.
- Streaming session APIs avoid single large contiguous buffers by using input and output callbacks, with global stream chunk size controlled by `sqlite3session_config(SQLITE_SESSION_CONFIG_STRMSIZE, ...)`.
- `sqliteLimit.h` constants influence persistent file compatibility and resource ceilings, especially page size, maximum page count, SQL length, column count, trigger recursion, attached database count, and default cache/WAL settings.
- Pager and btree declarations define persistence-critical behavior: rollback journal modes, WAL support, savepoints, sync/fullfsync/cache-spill flags, auto-vacuum modes, schema metadata slots, database header versioning, and cursor payload insert/delete semantics.
- The locking constants around `PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, and `SHARED_SIZE` are file-format sensitive because lock bytes must not overlap allocated database pages.

## Dependencies and Integration Points

- Optional public APIs are gated by compile-time macros such as `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_RTREE_INT_ONLY`, `SQLITE_ENABLE_SESSION`, and FTS5 availability.
- The WASI branch forces `SQLITE_WASI`, disables loadable extensions, and defaults `SQLITE_THREADSAFE` to 0 if not specified.
- Configuration macros establish defaults for `SQLITE_THREADSAFE`, memory allocator selection, `SQLITE_DEFAULT_MEMSTATUS`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_POWERSAFE_OVERWRITE`, mmap limits, temp storage, worker threads, recursive triggers, and file-format version.
- Platform/compiler integration includes pointer/integer cast macros, inline/noinline attributes, MSVC intrinsics and SEH gating, byte-order detection, fixed-size integer typedefs, alignment macros, and debug/coverage helper macros such as `testcase()`, `ALWAYS()`, `NEVER()`, `TREETRACE()`, and `WHERETRACE()`.
- `parse.h` token IDs are generated from the parser grammar and must stay synchronized with tokenizer and parser tables later in `parse.c`.
- OS wrapper declarations depend on the public `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3_vfs` APIs defined earlier in `sqlite3.h`. Pager and btree depend on those wrappers rather than calling VFS methods directly.
- Pager and btree constants intentionally mirror each other in some places: `PAGER_OMIT_JOURNAL` and `PAGER_MEMORY` must match `BTREE_OMIT_JOURNAL` and `BTREE_MEMORY`.
- Btree integrates with parser/codegen through `KeyInfo`, `UnpackedRecord`, `sqlite3_value`, cursor hints, and `BtreePayload`. It integrates with pager for page storage and WAL checkpoints.
- VDBE declarations bridge code generation and execution. `VdbeOp.p4` can carry pointers to `FuncDef`, `CollSeq`, `KeyInfo`, `Table`, `SubProgram`, virtual table objects, expressions, and other internal objects, so `p4type` ownership rules are critical.

## Risks and Edge Cases

- Many APIs in this range are compile-time optional. Downstream tests or code that assumes their symbols exist will fail when the corresponding macros are disabled.
- Scan-status `iScanStatusOp` values outside the documented constants have undefined behavior. The `_v2()` flags currently define only `SQLITE_SCANSTAT_COMPLEX`, leaving future flag expansion sensitive to callers passing stray bits.
- Pre-update helper APIs are only valid during the callback and with the same connection pointer. Misuse is explicitly undefined and can expose destroyed `sqlite3_value` objects after callback return.
- Session objects and application pre-update hooks conflict because both rely on the single connection pre-update hook slot.
- Snapshot APIs are constrained to WAL databases, non-autocommit transactions, no open write transaction for `get`, and no active statements for some `open` cases. Checkpoints can invalidate old snapshots, returning `SQLITE_ERROR_SNAPSHOT`.
- `SQLITE_SERIALIZE_NOCOPY` returns a borrowed pointer that is invalidated by the next write or connection close. `sqlite3_deserialize()` cannot target `temp`, fails if the schema is busy or in backup, and WAL-format serialized input must be converted to rollback mode before use.
- Session changesets ignore rows with NULL primary-key columns, compress multiple changes to the same key into net changes, and may represent primary-key updates as delete plus insert. These semantics are easy to misinterpret in replication tests.
- Conflict handlers for changeset apply must return values appropriate to the conflict type; returning `SQLITE_CHANGESET_REPLACE` for unsupported conflict classes makes apply fail with `SQLITE_MISUSE`.
- FTS5 tokenizer callbacks must report tokens in order and must not mark the first token as `FTS5_TOKEN_COLOCATED`. Versioned tokenizer structs differ in locale parameters, so mixing v1 and v2 callbacks incorrectly breaks ABI expectations.
- Raising limits such as `SQLITE_MAX_COLUMN`, page size, attached database count, or maximum variable number can overflow storage assumptions or create incompatible behavior. The code enforces some hard bounds but leaves many defaults compile-time tunable.
- Changing `PENDING_BYTE` is a subtle file-format compatibility change because the pager skips pages overlapping lock bytes.
- Internal `Hash` is not fully opaque because macros read fields directly. Structural changes have wide blast radius.
- `VdbeOp.p4type` values above `P4_FREE_IF_LE` do not own resources, while values at or below it require freeing. Incorrect tagging causes leaks, use-after-free, or double free.
- Opcode and token numeric values are generated contracts. Manual edits or mismatches with generated parser/opcode tables would corrupt SQL parsing or VDBE execution.

## Test Signals

Useful signals for this chunk are mostly API-contract and build-configuration tests:

- Build matrices toggling `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_OMIT_DESERIALIZE`, `SQLITE_ENABLE_SESSION`, FTS5, R-Tree, WAL, shared-cache, debug, and test options.
- Scan-status tests comparing `SQLITE_SCANSTAT_NLOOP`, `NVISIT`, `EST`, `NAME`, `EXPLAIN`, `SELECTID`, `PARENTID`, and `NCYCLE` output against `EXPLAIN QUERY PLAN`, plus reset behavior.
- Cache-flush tests with active readers, dirty pages, busy handlers, attached databases, and page 1 pinned.
- Pre-update hook tests for INSERT/UPDATE/DELETE, rowid vs WITHOUT ROWID tables, trigger depth, blob-write reporting, and invalid call sites.
- Snapshot tests covering WAL prerequisites, autocommit rejection, checkpoint invalidation, snapshot comparison, recovery, and active statement rejection.
- Serialize/deserialize tests for disk-backed, memory, read-only, resizeable, free-on-close, no-copy, busy schema, backup, temp schema rejection, and WAL-input failure.
- R-Tree tests registering geometry and scored query callbacks, checking `eWithin`, `rScore`, queue counts, level fields, and integer-only coordinate builds.
- Session tests for attach/filter behavior, primary-key requirements, NULL primary-key omission, `sqlite_stat1` special handling, changeset vs patchset output, streaming callbacks, conflict outcomes, and rebasing after `_apply_v2()`.
- FTS5 extension tests for auxiliary API version fields, column/phrase/instance accessors, auxdata lifetime, locale-aware tokenization, legacy tokenizer compatibility, prefix token handling, and synonym colocation rules.
- Internal regression tests should exercise parser token consistency, hash insertion/deletion/iteration, OS wrapper error propagation, pager journal/WAL/savepoint paths, btree cursor insert/delete/payload paths, shared-cache mutex no-op vs real paths, and VDBE opcode metadata consistency.

### subset-b-009014: lines 17069-22525

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 17069-22525

## Scope

This chunk covers the transition from generated SQLite VDBE opcode metadata into a large part of SQLite's private internal header surface. It begins inside `opcodes.h` with opcode numeric assignments from `OP_IfNullRow` through `OP_Abortable`, includes opcode property flags and `SQLITE_MX_JUMP_OPCODE`, then resumes `vdbe.h`, `pcache.h`, `mutex.h`, most of `sqliteInt.h`, `os_common.h`, and the beginning of generated `ctime.c` compile-option reporting.

The range is mostly declarations, macro contracts, and structure layouts rather than function bodies. Its main purpose is to define the in-memory ABI used by the implementation chunks that follow: VDBE bytecode construction, pager cache pages, connection/schema state, parse-tree state, SQL function metadata, virtual table metadata, expression/select/upsert/window trees, memory/debug hooks, parser and code-generator entry points, and optional test or diagnostic surfaces.

## Purpose

The opcode section defines the bytecode vocabulary and metadata consumed by the VDBE code generator and interpreter. The generated values and `OPFLG_*` bitvectors describe which operands are inputs, outputs, jump targets, or cycle counters, and `SQLITE_MX_JUMP_OPCODE` is tuned so label-resolution helpers can scan jump opcodes efficiently.

The `vdbe.h` declarations expose the private API for building, mutating, preparing, explaining, resetting, finalizing, and introspecting VDBE programs. Parser and code-generation code uses these routines to append opcodes, patch operands, manage labels, attach P4 payloads such as `KeyInfo`, annotate explain output, and track coverage.

The `pcache.h` section defines the pager cache page header and the cache interface used between the pager, btree, and pcache implementations. It establishes how pages are fetched, pinned, marked dirty or clean, truncated, spilled, reference-counted, and iterated under debug/test builds.

The large `sqliteInt.h` section defines SQLite's central private object model. It describes database connections (`sqlite3`), attached database slots (`Db`), schemas (`Schema`), lookaside state (`Lookaside`), SQL functions (`FuncDef`), tables/indexes/columns/foreign keys, expression and SELECT trees, parser state, virtual tables, CTEs, window functions, global configuration, and the private function prototypes tying the tokenizer, parser, resolver, planner, code generator, btree/pager glue, virtual table subsystem, foreign key subsystem, memory allocator, and diagnostics together.

The final `os_common.h` and `ctime.c` start provide shared OS-layer test/tracing macros and the generated compile-option list returned by SQLite diagnostics.

## Important APIs, Types, and Functions

- `OP_*` opcode constants and `OPFLG_*`: define VDBE instruction IDs and operand behavior. This chunk includes control-flow opcodes (`OP_Seek*`, `OP_Rewind`, `OP_Next`, `OP_Goto`-adjacent jump metadata from prior chunk), record/table/index access (`OP_Column`, `OP_MakeRecord`, `OP_OpenRead`, `OP_Insert`, `OP_Delete`, `OP_IdxInsert`), aggregate/window support (`OP_AggStep`, `OP_AggInverse`, `OP_AggFinal`), virtual table opcodes (`OP_VOpen`, `OP_VColumn`, `OP_VNext`), and diagnostics (`OP_Trace`, `OP_Explain`).
- VDBE builder API: `sqlite3VdbeCreate`, `sqlite3VdbeAddOp0/1/2/3/4`, `sqlite3VdbeAddFunctionCall`, `sqlite3VdbeAddOpList`, `sqlite3VdbeChangeP1/P2/P3/P4/P5`, `sqlite3VdbeJumpHere`, `sqlite3VdbeResolveLabel`, `sqlite3VdbeMakeReady`, `sqlite3VdbeFinalize`, `sqlite3VdbeReset`, `sqlite3VdbeDelete`, and related helpers.
- VDBE diagnostics and coverage: `sqlite3VdbeExplain`, `sqlite3VdbeExplainPop`, `sqlite3VdbeExplainParent`, `VdbeComment`, `VdbeNoopComment`, `VdbeCoverage*`, `sqlite3VdbeScanStatus*`, and `sqlite3VdbePrintOp`.
- `PgHdr` and `PCache`: represent page-cache entries and cache instances. `PgHdr` stores page data, extra metadata, owner cache, pager, page number, flags, reference count, and dirty-list links.
- Pcache API: `sqlite3PcacheInitialize`, `sqlite3PcacheOpen`, `sqlite3PcacheFetch`, `sqlite3PcacheFetchStress`, `sqlite3PcacheFetchFinish`, `sqlite3PcacheRelease`, `sqlite3PcacheMakeDirty`, `sqlite3PcacheMakeClean`, `sqlite3PcacheDirtyList`, `sqlite3PcacheTruncate`, `sqlite3PcacheClear`, `sqlite3PcacheClose`, `sqlite3PcacheSetCachesize`, `sqlite3PcacheSetSpillsize`, and `sqlite3PcacheShrink`.
- Mutex selection macros: choose `SQLITE_MUTEX_OMIT`, `SQLITE_MUTEX_NOOP`, `SQLITE_MUTEX_PTHREADS`, or `SQLITE_MUTEX_W32` from `SQLITE_THREADSAFE` and OS macros. In omit mode, mutex APIs compile to no-op macros returning sentinel success values.
- `Db` and `Schema`: attach database handles to btrees and schema caches. `Schema` stores schema cookie, generation, hashes for tables/indexes/triggers/foreign keys, encoding, format, flags, and default cache size.
- `sqlite3`: the central connection object. This chunk defines the fields for VFS, VDBE list, mutex, attached databases, flags, transaction/autocommit state, error state, lookaside allocator, callbacks, progress/busy handlers, virtual table transactions, function/collation hashes, savepoints, deferred constraints, unlock notify, and extension handles.
- `Lookaside` and `LookasideSlot`: per-connection fixed-size allocation pools, including optional two-size lookaside. `DisableLookaside` and `EnableLookaside` manipulate `bDisable` and the fast-path `sz` field.
- `FuncDef`, `FuncDestructor`, and `FuncDefHash`: describe built-in and application SQL functions, aggregate/window callbacks, function flags, hashing, and reference-counted destructors for `sqlite3_create_function_v2`.
- `Column`, `CollSeq`, affinity and comparison flags: define column metadata, collation callbacks, affinity constants, NULL-comparison modifiers, hidden/generated column flags, and type-checking relationships used by code generation and VDBE comparison.
- `VTable`, `Table`, `FKey`, `Index`, `IndexSample`, `KeyInfo`, and `UnpackedRecord`: core schema/planner/runtime metadata for ordinary tables, virtual tables, foreign keys, btree indexes, STAT4 samples, collation/sort descriptors, and decoded index probe keys.
- Parser tree types: `Token`, `Expr`, `ExprList`, `SrcItem`, `SrcList`, `NameContext`, `Upsert`, `Select`, `SelectDest`, `AggInfo`, `Trigger`, `TriggerPrg`, `Parse`, `With`, `Cte`, `CteUse`, `Window`, `Walker`, and `DbFixer`.
- Code-generation and parser prototypes: declarations cover expression allocation/deletion/coding, SELECT preparation/execution, WHERE planning, DDL/DML generation, schema init/reset, table/index creation/drop, triggers, foreign keys, UPSERT, CTEs, virtual tables, name resolution, collation lookup, affinity handling, varints, value conversion, error propagation, memory allocation, parser entry points, and module registration.
- Debug/test/diagnostic hooks: `sqlite3FaultSim`, fault injector IDs, benign malloc markers, memory-debug type tags, `SimulateIOError`, `SimulateDiskfullError`, `OpenCounter`, parser tracing/coverage, I/O tracing, tree-view printers, VDBE coverage, scan status, and compile-option diagnostics.

## Control Flow and Contracts

There is little executable control flow in this chunk, but it defines several important control-flow contracts for later code:

- VDBE code generation constructs bytecode by appending opcodes, reserving labels, then patching unresolved `P2` jump targets with `sqlite3VdbeJumpHere()` or `sqlite3VdbeResolveLabel()`. `OPFLG_JUMP` and `SQLITE_MX_JUMP_OPCODE` let the VDBE builder and verifier identify jump instructions cheaply.
- `VdbeCoverage*` macros annotate branches at code-generation time. With `SQLITE_VDBE_COVERAGE`, they record the source line and expected branch shape; without it, they compile away.
- Page cache fetch is split into allocation and finish phases: `sqlite3PcacheFetch()` obtains an underlying `sqlite3_pcache_page`, `sqlite3PcacheFetchFinish()` maps it to a `PgHdr`, and each successful fetch pins the page until `sqlite3PcacheRelease()`.
- Dirty-page handling is list-based. `sqlite3PcacheMakeDirty()` places a page on the cache dirty list, `sqlite3PcacheMakeClean()` removes it, and `sqlite3PcacheDirtyList()` returns a page-number-sorted list for pager writeback.
- Schema access is guarded by mutex rules documented on `Schema`: normal schemas require the corresponding btree mutex and connection mutex; TEMP schema needs only the connection mutex.
- Parse state is split into a zero-initialized header, a non-recursive region, and a recursive tail. `PARSE_HDR_SZ`, `PARSE_RECURSE_SZ`, and `PARSE_TAIL_SZ` encode that layout for parser reentry and nested parse cleanup.
- Name resolution walks nested `NameContext` objects from innermost to outermost, increments `nRef` on a match, and records aggregate/window/subquery side effects with `NC_*` flags.
- SELECT code generation routes rows through `SelectDest.eDest`. The `SRT_*` constants distinguish output, memory scalar, set membership, ephemeral table, coroutine, queue, recursive queue, and update-from destinations.
- Virtual table state is per connection even when schema is shared. `VTable` objects are moved to `sqlite3.pDisconnect` for deferred disconnection to avoid mutex-order deadlocks.
- Compile-time feature macros replace entire subsystems with no-op stubs when omitted. Examples include virtual tables, foreign keys, CTEs, UPSERT, WAL, generated columns, window functions, shared cache, unlock notify, and memory debugging.

## State and Persistence Behavior

This chunk defines the in-memory state model that persists for the lifetime of a SQLite connection, statement, schema, or cache object:

- Persistent connection state lives in `sqlite3`: attached database array, open VDBEs, autocommit and transaction counters, error state, callback registrations, limits, flags, lookaside pools, function/collation registries, busy/progress handlers, savepoints, deferred constraints, virtual table transactions, and unlock-notify links.
- Persistent schema state lives in `Schema` and subordinate `Table`, `Index`, `Trigger`, and `FKey` structures. Schema cookies and generation counters detect changes; hash tables cache lookup by object name.
- Pager-cache state lives in `PCache` and `PgHdr`. Page flags (`PGHDR_DIRTY`, `PGHDR_WRITEABLE`, `PGHDR_NEED_SYNC`, `PGHDR_DONT_WRITE`, `PGHDR_MMAP`, `PGHDR_WAL_APPEND`) encode writeback, journaling, mmap, and WAL interactions.
- Parse state in `Parse` is transient but complex. It owns temporary registers, VDBE cursor allocation counters, label tables, constant-expression lists, cleanup callbacks, trigger programs, active WITH clauses, rename metadata, and recursive parse fields.
- Expression trees may be full, reduced, or token-only. `EP_Reduced` and `EP_TokenOnly` are memory-layout contracts; consumers must not read fields past the allowed prefix.
- `FuncDestructor` persists until all generated `FuncDef` variants release it. This is critical when a single application function definition expands into multiple encodings.
- `KeyInfo` is reference counted and shared between VDBE programs or cursors that need collation/sort metadata for index keys.
- Global process state is represented by `Sqlite3Config`, declared here for non-amalgamation builds. It stores allocator, mutex, pcache, mmap, logging, lookaside defaults, initialization flags, test hooks, compile-time tuning, and global diagnostics.
- `os_common.h` test state is global under `SQLITE_TEST`: simulated I/O error counters and open-file counts influence later OS backend behavior and test assertions.

The declarations themselves do not write durable data. Durable effects occur later through pager, journal, WAL, schema, and VDBE implementations that honor the structures and flags defined here.

## Dependencies and Integration Points

This chunk is a central integration point for the SQLite amalgamation:

- VDBE builder declarations are consumed by parser actions, expression code generation, DML/DDL emitters, trigger code, foreign key enforcement, virtual table code, and query planner output.
- Pcache interfaces connect the pager to the configured page-cache backend (`sqlite3_pcache_methods2`) and to memory-pressure logic via the `xStress` callback supplied to `sqlite3PcacheOpen()`.
- Mutex macros depend on `SQLITE_THREADSAFE`, `SQLITE_OS_UNIX`, and `SQLITE_OS_WIN`, then feed every subsystem that needs connection, global, pcache, malloc, or shared-cache locking.
- Schema and table/index metadata connect parser DDL, schema loading, query planning, name resolution, bytecode generation, ANALYZE statistics, foreign keys, triggers, generated columns, hidden columns, and virtual table support.
- `sqlite3` embeds public API callback state such as commit/rollback/update hooks, trace/profile hooks, WAL hooks, progress and busy handlers, collation-needed callbacks, preupdate hooks, autovacuum callbacks, and client data.
- `Parse` integrates the tokenizer/parser, resolver, code generator, VDBE program builder, trigger compiler, schema authorization, virtual table declaration mode, ALTER TABLE rename tracking, RETURNING handling, and cleanup queue.
- Private prototypes tie together source modules that are separate in canonical SQLite but fused in this amalgamation: `build.c`, `expr.c`, `select.c`, `where.c`, `vdbe*.c`, `btree.c`, `pager.c`, `pcache.c`, `vtab.c`, `fkey.c`, `insert.c`, `update.c`, `delete.c`, `resolve.c`, `alter.c`, `analyze.c`, `func.c`, `utf.c`, `util.c`, `fault.c`, and OS backends.
- `ctime.c` integrates with `sqlite3_compileoption_get()` / `sqlite3_compileoption_used()` implementations later in the file by constructing a sorted array of compile-time option strings.

Within WiredTiger, this is vendored third-party SQLite test code. The practical integration risk is not that WiredTiger uses these internal structures directly, but that WiredTiger's test build inherits SQLite compile-time feature selections, diagnostics, and fault/test surfaces from this amalgamated source.

## Risks and Edge Cases

- Opcode numeric values are generated and must remain consistent with VDBE interpreter switch cases, opcode-name tables, explain output, and property flags. Manual edits would break bytecode execution or diagnostics.
- `OPFLG_INITIALIZER` must align exactly with opcode IDs. A shifted or missing entry causes operand ownership/jump analysis mistakes in code generation and VDBE validation.
- Many bit values have documented equality constraints across subsystems, enforced by assertions elsewhere. Examples include `SQLITE_FUNC_*` versus public flags and VDBE operand flags, `EP_*` versus `NC_*` and `SF_*`, `COLFLAG_*` versus `TF_*`, `OPFLAG_*` versus btree flags, and `WHERE_USE_LIMIT` versus `SF_FixedLimit`.
- Structure layout is performance- and memory-sensitive. `Expr` supports truncated allocations, `Parse` has recursive/non-recursive layout boundaries, `KeyInfo` and flexible-array structs use `offsetof()` sizing macros, and `sqlite3` contains conditional fields controlled by compile-time options.
- Mutex omission mode returns sentinel mutex pointers and reports all mutexes as held/not-held. Any code path that assumes real mutex behavior in `SQLITE_THREADSAFE=0` builds would be wrong.
- Lookaside enable/disable mutates both `bDisable` and `sz`; mismatched nesting can leave lookaside accidentally disabled or enabled in parser/schema-loading paths.
- Virtual table lifetime is deliberately deferred through `sqlite3.pDisconnect`. Freeing or disconnecting `VTable` objects eagerly can deadlock or invalidate prepared statements.
- Foreign key support is split from trigger support. With `SQLITE_OMIT_TRIGGER` but not `SQLITE_OMIT_FOREIGN_KEY`, declarations allow parsing some FK metadata while enforcement helpers become no-ops.
- Debug/test macros can change control flow in test builds: simulated I/O and disk-full errors execute caller-supplied code blocks; VDBE coverage asserts if generated branches are unannotated; memory-debug tags assert allocator ownership.
- `SQLITE_ASCII` and locale-dependent ctype branches behave differently. SQLite's ASCII tables provide deterministic SQL token rules; falling back to libc ctype could vary by locale if configured that way.
- `SQLITE_OMIT_*` macros replace functions with no-op macros that may drop side effects from arguments if future callers are not careful.
- The compile-option array must remain sorted for diagnostics and binary-search style consumers later in `ctime.c`.

## Test Signals

Useful test and validation signals for this chunk include:

- Amalgamation builds compile with default features and with representative `SQLITE_OMIT_*` combinations, proving macro stubs and conditional fields remain coherent.
- VDBE bytecode generation tests pass under `SQLITE_DEBUG` with opcode property assertions enabled.
- VDBE branch coverage builds using `SQLITE_VDBE_COVERAGE` do not report missing `VdbeCoverage*` annotations for branch opcodes generated by later code.
- Pager/pcache tests exercise fetch/release reference counts, dirty-list ordering, page-size changes, truncation, cache spilling through `xStress`, mmap page flags, and sync flags.
- Threading tests cover `SQLITE_THREADSAFE=0`, pthread mutexes, Win32 mutexes, and noop mutex builds where applicable.
- Lookaside tests verify hit/miss/full counters, disable/enable nesting, two-size lookaside behavior, and schema parsing with lookaside disabled.
- Parser and resolver tests stress expression depth, token-only/reduced expression allocation, nested name contexts, aggregates, windows, CTE materialization flags, UPSERT target analysis, generated columns, hidden columns, and RIGHT/FULL join flags.
- Virtual table tests cover per-connection `VTable` handles, transaction hooks, eponymous modules, shadow table detection, `xConnect`/`xCreate` error propagation, and deferred disconnect cleanup.
- Foreign key tests cover builds with full FK enforcement, FK parsing without triggers, and complete FK omission.
- Fault-injection tests using `sqlite3FaultSim`, benign malloc markers, `SimulateIOError`, and `SimulateDiskfullError` confirm later pager/OS code responds to allocation and I/O failures without corrupting state.
- Compile-option diagnostic tests compare `sqlite3_compileoption_get()` and `sqlite3_compileoption_used()` against the build flags represented in `sqlite3azCompileOpt[]`.

### subset-b-009015: lines 22526-30978

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 22526-30978

## Scope

This chunk covers a large core-runtime segment of SQLite's amalgamated `sqlite3.c`, starting in the compile-option diagnostics table and ending at the first line of `mallocWithAlarm()` in the front-end allocator wrapper. The amalgamated source sections included here are:

- Tail of `ctime.c`: compile-time option name emission and `sqlite3CompileOptions()`.
- `global.c`: process-wide constants, character lookup tables, default configuration, opcode/type metadata, and tracing globals.
- `status.c`, including the embedded `vdbeInt.h`: VDBE private structures and global/database status accounting.
- `date.c`: SQLite's SQL date/time parser, modifier engine, date/time scalar functions, fallback current-time functions, and registration hook.
- `os.c`: common `sqlite3_file` and `sqlite3_vfs` wrappers, test fault injection points, VFS registry management.
- `fault.c`: benign malloc failure hooks.
- `mem0.c`, `mem1.c`, `mem2.c`, `mem3.c`, `mem5.c`: low-level allocator backends selected by compile-time configuration.
- `mutex.c`, `mutex_noop.c`, `mutex_unix.c`, `mutex_w32.c`, and embedded `os_win.h`: mutex method selection and platform mutex implementations.
- Start of `malloc.c`: public heap-limit APIs, allocator initialization/shutdown, memory-use status APIs, and alarm entrypoint.

The range is third-party SQLite code vendored under WiredTiger's test tree. It is not a WiredTiger storage engine path; it supplies SQLite runtime behavior for the vendored SQLite test/tooling environment.

## Purpose

The common theme is SQLite process infrastructure: how the library reports its build shape, initializes global defaults, parses built-in date/time functions, routes abstract OS/VFS calls, chooses and instruments memory allocators, chooses and instruments mutex implementations, and exposes memory status and limits.

Within the SQLite core, this code sits below SQL compilation/execution and above platform/runtime services. Higher layers call these helpers rather than calling `malloc()`, `pthread_mutex_*`, Win32 `CRITICAL_SECTION`, `localtime()`, or VFS methods directly. That centralization lets SQLite add compile-time feature gates, fault injection, status counters, memory-pressure handling, and portability shims without scattering platform-specific logic through the pager, btree, VDBE, parser, and extension code.

## Important APIs, Types, and Functions

- `sqlite3CompileOptions(int *pnOpt)`: returns the static `sqlite3azCompileOpt` array of compile-option strings generated through many `#ifdef` branches. This backs compile-option diagnostics when `SQLITE_OMIT_COMPILEOPTION_DIAGS` is not set.
- `sqlite3UpperToLower`, `sqlite3CtypeMap`, `sqlite3aLTb`, `sqlite3aEQb`, `sqlite3aGTb`: global lookup tables for ASCII/EBCDIC folding, SQLite-specific character classification, and comparison-opcode truth tables.
- `sqlite3Config`: the global `Sqlite3Config` singleton. It captures default mutex, allocator, page-cache, mmap, URI, lookaside, sorter, statement-journal, localtime, test, and debug-tuning defaults used during `sqlite3_initialize()` and configuration.
- `sqlite3BuiltinFunctions`, `sqlite3PendingByte`, `sqlite3TreeTrace`, `sqlite3WhereTrace`, `sqlite3OpcodeProperty`, `sqlite3StrBINARY`, `sqlite3StdType*`: global function registry and constants shared by parser, VDBE, pager, planner, and type-affinity code.
- `VdbeCursor`, `VdbeFrame`, `Mem`/`sqlite3_value`, `sqlite3_context`, `ScanStatus`, `DblquoteStr`, `Vdbe`, `PreUpdate`, `ValueList`: private VDBE data structures pulled into `status.c` by amalgamation. They define cursor state, VM frames, SQL value representation, function-call contexts, scan-status records, normalized-SQL double-quote tracking, statement lifecycle state, pre-update hook state, and value-list cleanup state.
- `sqlite3_status64()`, `sqlite3_status()`, `sqlite3_db_status()`, `sqlite3StatusUp()`, `sqlite3StatusDown()`, `sqlite3StatusHighwater()`, `sqlite3StatusValue()`, `sqlite3LookasideUsed()`: status APIs and internal counter mutators for global memory/page-cache/parser metrics and per-connection lookaside, cache, schema, statement, pager, and foreign-key metrics.
- `DateTime` plus `parseDateOrTime()`, `parseModifier()`, `isDate()`, `computeJD()`, `computeYMD()`, `computeHMS()`, `toLocaltime()`: the internal state machine for SQL date/time conversion. `iJD` is Julian day in milliseconds; validity flags track whether YMD/HMS/JD/raw numeric state is current.
- Date/time SQL functions: `juliandayFunc()`, `unixepochFunc()`, `datetimeFunc()`, `timeFunc()`, `dateFunc()`, `strftimeFunc()`, `timediffFunc()`, `ctimeFunc()`, `cdateFunc()`, `ctimestampFunc()`, fallback `currentTimeFunc()`, and debug-only `datedebugFunc()`.
- `sqlite3RegisterDateTimeFunctions()`: inserts the date/time built-ins into the global function table.
- OS wrappers: `sqlite3OsClose()`, `sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsSync()`, `sqlite3OsOpen()`, `sqlite3OsDelete()`, `sqlite3OsAccess()`, `sqlite3OsFullPathname()`, shared-memory wrappers, mmap `sqlite3OsFetch()/sqlite3OsUnfetch()`, dynamic-library wrappers, randomness/sleep/current-time wrappers, and `sqlite3OsOpenMalloc()/sqlite3OsCloseFree()`.
- VFS registry APIs: `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, `sqlite3_vfs_unregister()`, plus internal `vfsUnlink()`.
- Fault hooks: `sqlite3BenignMallocHooks()`, `sqlite3BeginBenignMalloc()`, `sqlite3EndBenignMalloc()`.
- Allocator backend method providers: `sqlite3MemSetDefault()` for zero/system/debug allocators, `sqlite3MemGetMemsys3()`, `sqlite3MemGetMemsys5()`, plus backend-specific malloc/free/realloc/size/roundup/init/shutdown methods.
- Debug allocator APIs: `sqlite3MemdebugSetType()`, `sqlite3MemdebugHasType()`, `sqlite3MemdebugNoType()`, `sqlite3MemdebugBacktrace()`, `sqlite3MemdebugBacktraceCallback()`, `sqlite3MemdebugSettitle()`, `sqlite3MemdebugSync()`, `sqlite3MemdebugDump()`, `sqlite3MemdebugMallocCount()`.
- Mutex front-end APIs: `sqlite3MutexInit()`, `sqlite3MutexEnd()`, `sqlite3_mutex_alloc()`, `sqlite3MutexAlloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, debug `sqlite3_mutex_held()` and `sqlite3_mutex_notheld()`, and optional `sqlite3MutexWarnOnContention()`.
- Mutex method providers: `sqlite3NoopMutex()`, `sqlite3DefaultMutex()` for pthread or Win32 builds, and `multiThreadedCheckMutex()` when multithreaded checks are enabled.
- Malloc front-end APIs at the end of the chunk: `sqlite3_release_memory()`, `sqlite3_memory_alarm()`, `sqlite3_soft_heap_limit64()`, `sqlite3_soft_heap_limit()`, `sqlite3_hard_heap_limit64()`, `sqlite3MallocInit()`, `sqlite3HeapNearlyFull()`, `sqlite3MallocEnd()`, `sqlite3_memory_used()`, `sqlite3_memory_highwater()`, `sqlite3MallocAlarm()`, `test_oom_breakpoint()`, and the opening of `mallocWithAlarm()`.

## Control Flow

Compile-option diagnostics are built entirely at compile time. Each enabled compile flag contributes a string literal to `sqlite3azCompileOpt`; `sqlite3CompileOptions()` simply stores the array length through `pnOpt` and returns the array.

`global.c` establishes immutable lookup tables and the initial `sqlite3Config` contents before any runtime initialization. Later `sqlite3_config()` calls can replace parts of `sqlite3Config` before `sqlite3_initialize()`, but the defaults here determine normal embedded behavior: URI filenames off unless requested, covering-index scans on, lookaside defaults, statement-journal spill threshold, mmap limits, page-cache defaults, and memory allocator/mutex placeholders.

The status subsystem stores current and high-water counters in `sqlite3Stat`. Each status category is mapped to either the malloc mutex or the pcache mutex through `statMutex[]`. Internal code mutates counters only while holding the proper mutex, and public `sqlite3_status64()` selects the same mutex, copies current/high-water values, and optionally resets the high-water mark to the current value.

`sqlite3_db_status()` runs under the database connection mutex and dispatches by `op`. Lookaside counters are derived from free/init slot lists, lookaside hit/miss counters are read and optionally reset, cache memory walks all attached btrees/pagers, schema and prepared-statement memory are measured by temporarily redirecting destructor paths to count freed bytes without truly freeing live state, pager cache statistics are accumulated per attached database, and deferred foreign-key status is read from connection counters.

The date/time path starts with `isDate()`. It initializes a `DateTime`, parses the first argument as current time, numeric Julian/unix candidate, ISO-like text, time-only text, `now`, or `subsec`, then applies each modifier through `parseModifier()`. Modifiers can reinterpret raw numeric values (`auto`, `unixepoch`, `julianday`), adjust calendar/time values (`+NNN days`, `+YYYY-MM-DD`, `+HH:MM:SS`), resolve month overflow (`ceiling`, `floor`), snap to boundaries (`start of month/year/day`), move to a weekday, shift between UTC and local time, or request subsecond output. After modifiers, `computeJD()` normalizes to a validated Julian-day millisecond value. Output functions then convert that canonical value into numeric, text, or formatted results.

The OS layer is a thin dispatch layer over `sqlite3_file` and `sqlite3_vfs` method tables. It applies test OOM injection before selected I/O calls, normalizes behavior such as `xSync` with zero flags returning `SQLITE_OK`, falls back from `xCurrentTimeInt64` to `xCurrentTime`, masks open flags before passing them to VFS `xOpen`, and maintains a process-global linked list of registered VFS implementations under the static main mutex.

The low-level allocator backend is selected by compile-time macros or explicit configuration. `SQLITE_ZERO_MALLOC` installs no-op methods that always fail allocation. `SQLITE_SYSTEM_MALLOC` wraps system malloc/realloc/free and either uses platform usable-size APIs or stores an 8-byte size header. `SQLITE_MEMDEBUG` wraps system allocation with headers, guard words, backtrace/title metadata, randomized fill, active-allocation lists, and counters. `SQLITE_ENABLE_MEMSYS3` exposes a fixed-pool allocator based on variable-sized chunks and freelists/hash buckets. `SQLITE_ENABLE_MEMSYS5` exposes a fixed-pool buddy allocator where allocation sizes round to powers of two and adjacent buddies coalesce on free.

Mutex initialization first copies a method table into `sqlite3GlobalConfig.mutex` if one was not supplied through configuration. If core mutexes are disabled, it selects the no-op provider. If enabled, it selects the platform default provider or the multithreaded-check wrapper. After copying all function pointers except `xMutexAlloc`, it issues a memory barrier and installs `xMutexAlloc` last, making partially initialized method tables less visible to racing readers. Allocation and enter/leave public APIs then dispatch through that method table.

The pthread provider uses static mutex objects for `SQLITE_MUTEX_STATIC_*`, dynamic allocations for fast/recursive mutexes, optional native recursive mutex attributes, and optional home-grown recursive tracking. The Win32 provider explicitly initializes static `CRITICAL_SECTION` objects during `winMutexInit()`, uses interlocked state to serialize initialization/shutdown, and uses `TryEnterCriticalSection()` only when available on NT-class builds. Debug builds in both providers track owner/refcount and assert correct recursive versus non-recursive use.

The start of `malloc.c` is the allocator front-end around whichever backend was selected. `sqlite3MallocInit()` installs defaults if no allocator exists, obtains the static memory mutex, validates page-cache backing memory, and calls the selected backend `xInit`. Heap-limit APIs update `mem0.alarmThreshold`, `mem0.hardLimit`, and `mem0.nearlyFull` under the malloc mutex, then try to release page-cache memory if current usage exceeds the new soft limit. `sqlite3_memory_used()` and `sqlite3_memory_highwater()` are small wrappers over `sqlite3_status64(SQLITE_STATUS_MEMORY_USED, ...)`.

## State and Persistence Behavior

Most state in this chunk is process-global SQLite runtime state:

- `sqlite3Config` persists across the process and drives initialization, unless reset by shutdown/reconfiguration paths outside this chunk.
- `sqlite3BuiltinFunctions` becomes the read-only built-in SQL function registry after initialization.
- `sqlite3PendingByte` is a global database-file format parameter; changing it through test controls creates incompatible file layouts and is only for testing.
- `sqlite3TreeTrace`, `sqlite3WhereTrace`, coverage counters, profile counters, I/O fault counters, diskfull counters, and open-file counters are test/debug globals.
- `sqlite3Stat` stores global status counters and high-water marks; public reset only lowers high-water values to current values, not current usage.
- `vfsList` is a global linked list of VFS implementations. Registration order matters because the head is the default VFS.
- Allocator global structs (`mem`, `mem3`, `mem5`, `mem0`) hold active heap accounting, fixed-pool state, debug allocation lists, and heap limit state.
- Mutex static arrays in no-op/debug/pthread/Win32 providers hold process-global static mutex objects.

Database-file persistence is indirect. The date/time, status, mutex, and allocator sections do not themselves write database pages. The OS wrapper section dispatches all VFS file writes, syncs, truncates, deletes, shared-memory operations, and file controls used by pager and WAL code elsewhere. That makes it a persistence boundary: failures, flag masking, mmap availability, VFS registration order, and test fault injection here affect durability and recovery semantics elsewhere.

The date/time functions are mostly stateless. The exception is "current" time, which reads statement time through `sqlite3StmtCurrentTime()` and the active VFS time method, and local-time conversion, which depends on C library timezone behavior or test-supplied localtime fault hooks.

## Dependencies and Integration Points

This chunk depends on many SQLite internal subsystems defined outside the range: mutex and allocator configuration structures, pager/btree APIs, pcache mutexes, VDBE deletion and memory routines, hash-table iterators, schema/table/trigger destructors, SQL function registration, `sqlite3StmtCurrentTime()`, string accumulators, public `sqlite3_value_*` and `sqlite3_result_*` helpers, VFS/file method tables, and public initialization/configuration routines.

Compile-time flags are major integration points. The behavior in this range changes significantly under `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_DATETIME_FUNCS`, `SQLITE_OMIT_LOCALTIME`, `SQLITE_UNTESTABLE`, `SQLITE_TEST`, `SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_ZERO_MALLOC`, `SQLITE_SYSTEM_MALLOC`, `SQLITE_MEMDEBUG`, `SQLITE_ENABLE_MEMSYS3`, `SQLITE_ENABLE_MEMSYS5`, `SQLITE_MUTEX_OMIT`, `SQLITE_MUTEX_NOOP`, `SQLITE_MUTEX_PTHREADS`, `SQLITE_MUTEX_W32`, `SQLITE_ENABLE_MULTITHREADED_CHECKS`, `SQLITE_HOMEGROWN_RECURSIVE_MUTEX`, `SQLITE_ENABLE_API_ARMOR`, Windows platform macros, Apple zone-malloc macros, and feature flags listed in the compile-option table.

The VFS wrapper functions integrate directly with platform-specific `os_unix.c`, `os_win.c`, and any third-party VFS. The VFS registry is also used by shell/test tooling and by callers that select a named VFS through URI or open flags. `sqlite3OsRandomness()` can be made deterministic through `sqlite3Config.iPrngSeed`, which is important for repeatable tests.

The memory subsystem is layered: backend providers implement `sqlite3_mem_methods`; the front-end in `malloc.c` handles limits, stats, alarms, zero-size and oversized requests, and public APIs. The status subsystem reads memory usage through the same global counters, so allocator changes must preserve expected counter semantics.

The mutex subsystem is similarly layered: platform providers implement `sqlite3_mutex_methods`; `sqlite3MutexInit()` installs one method table globally; all internal mutex use routes through `sqlite3_mutex_*`/`sqlite3MutexAlloc()`. Fixed-pool allocators and status counters depend on the static memory mutex, while VFS registration and localtime fallback use the static main mutex.

Within WiredTiger, the integration concern is vendored SQLite build/test behavior. Changes here would alter SQLite test harness behavior, date/time SQL semantics, allocator and mutex portability, VFS fault injection, and compile-option reporting used by tests.

## Risks and Edge Cases

- The compile-option list is preprocessor-driven. A missing branch can make diagnostics lie about the binary, while an incorrect value macro can expose stale or malformed option strings.
- `sqlite3UpperToLower` also stores comparison truth tables after the 256-byte mapping. Pointer arithmetic depends on comparison opcodes remaining consecutive in the documented `NE EQ GT LE LT GE` order.
- `sqlite3PendingByte` controls a reserved lock byte page in the database file. Moving it outside tests makes files incompatible.
- Status counters rely on callers holding the correct mutex. The public API protects reads, but internal `sqlite3StatusUp/Down/Highwater/Value` assert rather than acquire locks.
- `sqlite3_db_status()` schema and statement memory measurements intentionally run destructors in counting mode. Bugs in `db->pnBytesFreed` handling or lookaside boundary manipulation could corrupt live connection state.
- Date/time parsing accepts flexible modifiers but has strict numeric ranges. Month/year arithmetic tracks `nFloor` for overflow resolution, so changing normalization order can alter `floor`/`ceiling` behavior for dates such as February 31.
- `localtime` conversion maps out-of-range years into a 1970-2038 equivalent before mapping back. This depends on calendar equivalence assumptions and host timezone rules, including DST behavior.
- `utc` conversion iterates at most four guesses to resolve localtime offset. Ambiguous or nonexistent local times around DST transitions are inherently delicate.
- Date/time `now`, `localtime`, `utc`, `subsec`, and `subsecond` are gated through `sqlite3NotPureFunc()` where appropriate. Removing those checks would make non-deterministic functions appear pure.
- OS wrappers use `DO_OS_MALLOC_TEST()` in test builds. Adding a new wrapper without the macro can leave OOM/fault-injection coverage gaps.
- `sqlite3OsOpen()` masks open flags before VFS dispatch. New public open flags must be intentionally added to the mask if they should reach the VFS.
- VFS registration is a linked-list mutation under the static main mutex. Registering the same object unlinks then reinserts it; default VFS order changes if `makeDflt` is true.
- `SQLITE_ZERO_MALLOC` deliberately makes SQLite unusable until a real allocator is configured. Accidentally selecting it in a normal build causes initialization/allocation failure.
- The system allocator path either trusts platform usable-size APIs or stores a private 8-byte prefix. Mixing allocators or freeing pointers not returned by the active backend is fatal.
- The debug allocator has strict guard-word and padding assertions. It also always moves allocations on realloc, intentionally exposing stale-pointer bugs.
- `memsys3` and `memsys5` require fixed heap memory supplied before initialization. Heap size, minimum request size, and alignment errors can make initialization fail or greatly increase fragmentation.
- `memsys3`'s key-block and freelist invariants are subtle: chunk headers encode checked-out and previous-free state in low bits, and coalescing depends on correct tail `prevSize`.
- `memsys5` caps allocations at 1 GiB and rounds to powers of two. Internal fragmentation is expected and tracked in debug/test counters.
- Mutex method installation uses memory barriers and installs `xMutexAlloc` last. Reordering that sequence can expose partially initialized method tables.
- No-op mutexes are only correct for single-threaded operation. Debug no-op mutexes catch misuse but still provide no mutual exclusion.
- Pthread debug owner checks rely on `pthread_equal()` being safe enough for assert-only use; comments call out platforms where this may be unreliable.
- Win32 static mutex initialization uses global interlocked state and waits with `sqlite3_win32_sleep(1)`. Incorrect shutdown ordering could delete static critical sections still in use.
- `sqlite3_soft_heap_limit64()` computes `excess = sqlite3_memory_used() - n` after releasing the mutex. Concurrent allocation/free can make release attempts approximate rather than exact.
- The chunk ends at the start of `mallocWithAlarm()`, so allocation-front-end behavior after alarm triggering continues in the next chunk and should be reconciled there.

## Test Signals

Useful signals for this chunk include:

- Compile-option introspection returns enabled options with expected `NAME` or `NAME=value` strings and correct count from `sqlite3CompileOptions()`.
- Character classification tests cover ASCII/EBCDIC case folding, identifier characters, quote characters, and comparison opcode truth-table assumptions.
- `sqlite3_status64()` returns `SQLITE_MISUSE_BKPT` for invalid ops and resets high-water values only when requested.
- `sqlite3_db_status()` reports lookaside used/high-water, lookaside hit/miss counters, pager cache memory, shared cache memory, schema memory, statement memory, cache hit/miss/write/spill counters, and deferred foreign-key state without changing current connection behavior.
- Date/time SQL tests cover ISO dates, negative years, time-only inputs, numeric Julian days, `now`, `subsec`, `unixepoch`, `auto`, `julianday`, `floor`, `ceiling`, `start of` modifiers, `weekday`, `localtime`, `utc`, large range limits, invalid modifiers returning NULL, `strftime()` conversion codes, `timediff()` invariants, and fallback `CURRENT_TIME/DATE/TIMESTAMP` builds when full datetime support is omitted.
- Localtime tests can use `sqlite3GlobalConfig.bLocaltimeFault` and `xAltLocaltime` in non-untestable builds to force success/failure paths.
- VFS tests verify wrapper delegation, masked open flags, `xCurrentTimeInt64` fallback, deterministic randomness under `iPrngSeed`, mmap stubs when mmap is disabled, `xSync` no-op for zero flags, VFS register/find/unregister order, and test OOM injection through `DO_OS_MALLOC_TEST()`.
- Benign malloc tests verify begin/end hooks are invoked only when `SQLITE_UNTESTABLE` is not defined.
- Allocator tests should run under system malloc, memdebug, memsys3, memsys5, and zero-malloc/custom allocator configurations where applicable. Signals include allocation size reporting, roundup behavior, realloc semantics, OOM logging, guard-word assertions, backtrace/title dumps, fixed-pool initialization failure without `pHeap`, memsys3 coalescing/key-block state, memsys5 buddy splitting/coalescing, and dump counters in debug/test builds.
- Mutex tests should cover no-op single-thread mode, debug misuse assertions, pthread fast/recursive/static mutex allocation, Win32 static initialization/shutdown, `sqlite3_mutex_try()` busy/ok behavior, API-armor invalid static IDs, and multithreaded-check warnings on database-handle contention.
- Heap-limit tests cover querying prior soft/hard values, hard limit constraining soft limit, `sqlite3HeapNearlyFull()` updates, memory-used/high-water wrappers, and `sqlite3_release_memory()` returning zero when `SQLITE_ENABLE_MEMORY_MANAGEMENT` is absent.

### subset-b-009016: lines 30979-39365

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 30979-39365

Chunk id: `subset-b-009016`

Source range researched: `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c` lines 30979-39365.

## Purpose

This chunk covers several core SQLite subsystems inside the amalgamated `sqlite3.c` copy vendored under WiredTiger tests:

- the memory allocator facade, connection-scoped allocation helpers, lookaside allocator handling, OOM propagation, and API exit error normalization;
- SQLite's locale-independent printf/string-accumulator implementation, reference-counted strings, and debug parse-tree rendering;
- process-global random bytes, portable worker thread wrappers, UTF-8/UTF-16 conversion helpers, numeric parsing, varint encoding, endian helpers, overflow-safe arithmetic, logarithmic estimates, VList symbol storage, and generic hash tables;
- opcode-name metadata for VDBE explain/debug builds;
- the complete experimental `kvvfs` key/value VFS and the start of the Unix VFS declarations and syscall indirection table.

The code is foundational infrastructure rather than a single feature path. It is used by nearly every upper SQLite layer in the amalgamation: parser, VDBE, btree/pager, virtual tables, test controls, extension APIs, and VFS dispatch.

## Important APIs, Types, And Functions

Memory and OOM handling:

- `sqlite3Malloc()`, `sqlite3_malloc()`, `sqlite3_malloc64()`, `sqlite3_free()`, `sqlite3Realloc()`, `sqlite3_realloc()`, and `sqlite3_realloc64()` wrap the configured global allocator in `sqlite3GlobalConfig.m`, enforce `SQLITE_MAX_ALLOCATION_SIZE`, maintain memory status counters when `bMemstat` is enabled, and use `mem0.mutex` around global memory accounting.
- `sqlite3DbMallocRaw()`, `sqlite3DbMallocRawNN()`, `sqlite3DbMallocZero()`, `sqlite3DbFreeNN()`, `sqlite3DbNNFreeNN()`, `sqlite3DbFree()`, `sqlite3DbRealloc()`, and `sqlite3DbReallocOrFree()` add connection-aware behavior, including lookaside allocation, `db->mallocFailed` consistency, `db->pnBytesFreed` measurement mode, and memory-debug type tags.
- `sqlite3OomFault()`, `sqlite3OomClear()`, `apiHandleError()`, and `sqlite3ApiExit()` centralize how an OOM flips `db->mallocFailed`, disables lookaside, interrupts active VDBEs, records parse errors, and maps API returns to `SQLITE_NOMEM_BKPT`.
- String duplication helpers include `sqlite3DbStrDup()`, `sqlite3DbStrNDup()`, `sqlite3DbSpanDup()`, and `sqlite3SetString()`.

Formatting and string accumulation:

- `sqlite3_str_vappendf()` implements SQLite's custom formatter. It supports standard conversions plus SQLite extensions: `%q`, `%Q`, `%w`, `%z`, `%T`, `%S`, `%r`, and the alternate `!` flag for UTF-8 character width/precision or higher precision floating-point formatting.
- `StrAccum` APIs include `sqlite3StrAccumSetError()`, `sqlite3StrAccumEnlarge()`, `sqlite3_str_append()`, `sqlite3_str_appendall()`, `sqlite3_str_appendchar()`, `sqlite3_str_appendf()`, `sqlite3StrAccumFinish()`, `sqlite3ResultStrAccum()`, `sqlite3_str_new()`, `sqlite3_str_finish()`, `sqlite3_str_reset()`, `sqlite3_str_errcode()`, `sqlite3_str_length()`, and `sqlite3_str_value()`.
- Public printf wrappers are `sqlite3_vmprintf()`, `sqlite3_mprintf()`, `sqlite3_vsnprintf()`, `sqlite3_snprintf()`, and `sqlite3_log()`. Internal wrappers include `sqlite3VMPrintf()` and `sqlite3MPrintf()`.
- `sqlite3RCStrRef()`, `sqlite3RCStrUnref()`, `sqlite3RCStrNew()`, and `sqlite3RCStrResize()` manage heap strings with a small reference-count header.

Debug tree views:

- Under `SQLITE_DEBUG`, `sqlite3TreeViewLine()`, `sqlite3TreeViewExpr()`, `sqlite3TreeViewExprList()`, `sqlite3TreeViewSelect()`, `sqlite3TreeViewSrcList()`, `sqlite3TreeViewWith()`, `sqlite3TreeViewWindow()`, `sqlite3TreeViewWinFunc()`, `sqlite3TreeViewUpsert()`, `sqlite3TreeViewTrigger()` and related `sqlite3Show*()` entry points print parser structures for diagnostics.

Randomness and threading:

- `sqlite3_randomness()` exposes random bytes from a process-global ChaCha20 PRNG state, seeded from the active VFS using `sqlite3OsRandomness()`.
- `sqlite3PrngSaveState()` and `sqlite3PrngRestoreState()` are test-control helpers when not compiled with `SQLITE_UNTESTABLE`.
- `sqlite3ThreadCreate()` and `sqlite3ThreadJoin()` abstract worker execution across pthreads, Win32 threads, or a no-real-thread fallback depending on platform macros and `SQLITE_MAX_WORKER_THREADS`.

Text encoding and utility functions:

- UTF helpers include `sqlite3AppendOneUtf8Character()`, `sqlite3Utf8Read()`, `sqlite3Utf8ReadLimited()`, `sqlite3VdbeMemTranslate()`, `sqlite3VdbeMemHandleBom()`, `sqlite3Utf8CharLen()`, `sqlite3Utf16to8()`, `sqlite3Utf16ByteLen()`, and test-only `sqlite3UtfSelfTest()`.
- Error utilities include `sqlite3Error()`, `sqlite3ErrorClear()`, `sqlite3SystemError()`, `sqlite3ErrorWithMsg()`, `sqlite3ProgressCheck()`, `sqlite3ErrorMsg()`, and `sqlite3ErrorToParser()`.
- Token/string helpers include `sqlite3Dequote()`, `sqlite3DequoteExpr()`, `sqlite3DequoteNumber()`, `sqlite3DequoteToken()`, `sqlite3TokenInit()`, `sqlite3_stricmp()`, `sqlite3StrICmp()`, `sqlite3_strnicmp()`, and `sqlite3StrIHash()`.
- Numeric helpers include `sqlite3AtoF()`, `sqlite3Int64ToText()`, `sqlite3Atoi64()`, `sqlite3DecOrHexToI64()`, `sqlite3GetInt32()`, `sqlite3Atoi()`, `sqlite3FpDecode()`, and `sqlite3GetUInt32()`.
- Binary encoding helpers include `sqlite3PutVarint()`, `sqlite3GetVarint()`, `sqlite3GetVarint32()`, `sqlite3VarintLen()`, `sqlite3Get4byte()`, `sqlite3Put4byte()`, `sqlite3HexToInt()`, and `sqlite3HexToBlob()`.
- Safety/math/planner helpers include `sqlite3SafetyCheckOk()`, `sqlite3SafetyCheckSickOrOk()`, `sqlite3AddInt64()`, `sqlite3SubInt64()`, `sqlite3MulInt64()`, `sqlite3AbsInt32()`, `sqlite3FileSuffix3()`, `sqlite3LogEstAdd()`, `sqlite3LogEst()`, `sqlite3LogEstFromDouble()`, and `sqlite3LogEstToInt()`.
- `sqlite3VListAdd()`, `sqlite3VListNumToName()`, and `sqlite3VListNameToNum()` implement a compact integer-array-backed variable-name map.
- `sqlite3HashInit()`, `sqlite3HashClear()`, `sqlite3HashFind()`, and `sqlite3HashInsert()` implement SQLite's case-insensitive string-key hash table.

VFS code:

- `sqlite3OpcodeName()` maps VDBE opcode integers to names and optional explain comments.
- `KVVfsFile`, `sqlite3OsKvvfsObject`, `kvvfs_db_io_methods`, `kvvfs_jrnl_io_methods`, and `sqlite3_kvvfs_methods` define the experimental key/value VFS.
- `kvstorageRead()`, `kvstorageWrite()`, and `kvstorageDelete()` are the native low-level key/value adapter; WASM builds may replace them through `sqlite3KvvfsMethods`.
- `kvvfsEncode()`, `kvvfsDecode()`, `kvvfsDecodeJournal()`, `kvvfsReadFileSize()`, and `kvvfsWriteFileSize()` implement the text-only persistence encoding for binary database pages and rollback journals.
- `kvvfsOpen()`, `kvvfsReadDb()`, `kvvfsWriteDb()`, `kvvfsReadJrnl()`, `kvvfsWriteJrnl()`, `kvvfsTruncateDb()`, `kvvfsTruncateJrnl()`, `kvvfsSyncJrnl()`, `kvvfsFileControlDb()`, and related methods implement the `sqlite3_io_methods` and `sqlite3_vfs` contracts.
- The start of `os_unix.c` defines Unix VFS feature macros, `unixFile`, `UnixUnusedFd`, syscall wrappers such as `osOpen`, `osClose`, `osRead`, `osPread`, `osWrite`, `osPwrite`, and related platform configuration.

## Control Flow

Allocation flow usually enters through either a public API allocator or a connection-scoped helper. Public calls initialize SQLite unless auto-init is omitted, reject zero or oversized allocations, and delegate to `sqlite3Malloc()` or `sqlite3Realloc()`. With memory statistics enabled, allocations enter `mem0.mutex`, round up sizes via the configured allocator, check soft and hard memory limits, possibly fire the malloc alarm, perform allocation, and update status counters. Connection-scoped allocations first try lookaside if enabled and the request fits; otherwise they call heap allocation and, on failure, set the connection OOM state.

OOM flow is deliberately sticky per connection. Once `db->mallocFailed` is set, later `sqlite3DbMallocRawNN()` calls fail consistently until `sqlite3OomClear()` sees no active VDBEs. `sqlite3ApiExit()` is the normal API-exit gate that converts pending OOM state or `SQLITE_IOERR_NOMEM` into `SQLITE_NOMEM_BKPT` and updates the connection error object.

Formatting flow in `sqlite3_str_vappendf()` scans ordinary text until `%`, parses flags, width, precision, length modifiers, and conversion type, then dispatches through `fmtinfo`. Integer conversions build output backwards into a stack or temporary buffer. Floating-point conversions call `sqlite3FpDecode()` and then render fixed, exponential, or generic form. SQL escaping conversions count required extra bytes before allocation, then duplicate quotes or emit `unistr()`-style escapes for alternate forms. Internal-only `%T` and `%S` return immediately if the `SQLITE_PRINTF_INTERNAL` flag is absent.

`StrAccum` grows lazily. Appends use the current buffer if possible, otherwise `sqlite3StrAccumEnlarge()` doubles toward the maximum allocation and preserves stack-buffer content when switching to heap. Error states are sticky and reset/free allocated buffers when necessary.

Tree-view routines recursively walk parse structures. `sqlite3TreeViewPush()` and `sqlite3TreeViewPop()` maintain indentation state, while each structure-specific routine computes how many child nodes remain so printed branches have correct continuation markers. These routines are compiled only in debug/test-oriented builds.

The PRNG flow locks `SQLITE_MUTEX_STATIC_PRNG`, optionally resets state for `N<=0` or null buffer, seeds ChaCha20 state from the active VFS on first use, and emits bytes from a cached 64-byte block, generating new blocks and incrementing the block counter as needed.

Thread wrapper flow creates an opaque `SQLiteThread` object. On pthread/Win32 builds it attempts to spawn a worker unless core mutexes are disabled or fault simulation requests deterministic sequential execution. The fallback implementation records the task and either runs it at create time or join time.

UTF translation branches by source and destination encoding. UTF-16 endian swaps happen in-place after making the `Mem` writeable. UTF-8/UTF-16 conversions allocate a worst-case output buffer, iterate code points with validation behavior controlled by compile-time options, release the old `Mem`, and install the new text buffer.

Numeric parsing uses conservative, encoding-aware scanners. `sqlite3AtoF()` parses sign, significand, decimal point, exponent, and trailing whitespace, then performs double-double scaling with `dekkerMul2()` for precision. `sqlite3Atoi64()` skips spaces and zeros, accumulates a 64-bit unsigned magnitude, compares 19-digit values to 2^63, and returns detailed status codes for overflow or trailing text.

Varint flow uses short fast paths for 1- and 2-byte encodings and a longer optimized decoder that reads alternating bytes into bit slots for up to 9 bytes. Hash-table insertion first searches by case-insensitive hash and key, replaces/removes existing elements if found, otherwise allocates a `HashElem`, resizes when count exceeds bucket pressure, and links into both the global list and optional bucket chain.

`kvvfs` maps SQLite file operations to text keys. Database pages are keyed by page number and encoded as text. Rollback journal writes accumulate in memory and persist on `xSync` as a length-prefixed encoded blob. Database size is stored separately under key `sz` and refreshed on lock acquisition. The VFS accepts only `local`, `session`, `local-journal`, and `session-journal` names.

The Unix VFS section in this chunk is setup-oriented: it selects feature macros, includes platform headers, defines `unixFile` state, and begins the syscall table so later VFS code can call `osOpen`, `osRead`, etc. through runtime-overridable function pointers.

## State And Persistence Behavior

Global process state includes:

- `sqlite3GlobalConfig`, especially allocator methods, logging callback, test callback, and core mutex mode;
- `mem0`, which tracks memory mutex, alarm threshold, hard limit, and near-full status;
- `sqlite3Prng`, a writable-static-data PRNG state vector with cached output bytes;
- `randomnessPid` in the Unix VFS prelude, used later to detect fork-related PRNG reseeding needs;
- `aSyscall[]`, the Unix VFS syscall indirection table, which can be overridden for tests and sandboxing.

Connection-local state includes:

- `db->lookaside` freelists and statistics, including optional two-size lookaside pools;
- `db->mallocFailed`, `db->bBenignMalloc`, `db->nVdbeExec`, `db->u1.isInterrupted`, `db->pParse`, `db->pErr`, `db->errCode`, `db->errByteOffset`, and `db->iSysErrno`;
- `db->pnBytesFreed`, which switches free paths into size-measurement mode instead of actually freeing.

`StrAccum` instances carry their own buffer pointer, allocation size, maximum allocation, character count, error code, database pointer, and flags indicating whether the buffer is heap-owned or internal formatting is allowed.

`kvvfs` persists state externally through text keys. Native non-WASM builds implement those keys as local files named `kvvfs-<class>-<key>`. Database page keys are page numbers; `sz` stores file size; `jrnl` stores the rollback journal. The VFS keeps per-open in-memory cache state in `KVVfsFile`: `aData`, `aJrnl`, `nJrnl`, `szPage`, `szDb`, and the selected storage class.

The hash table keeps an insertion/global iteration list (`Hash.first`) plus an optional bucket table (`Hash.ht`). Keys are not copied on insertion, so callers own key lifetimes.

## Dependencies And Integration Points

This chunk depends heavily on definitions from earlier parts of the amalgamation: `sqlite3`, `Mem`, `Parse`, `Expr`, `Select`, `SrcList`, `With`, `Window`, `Trigger`, `Hash`, `HashElem`, `VList`, `FpDecode`, `StrAccum`, `PrintfArguments`, allocator/debug macros, opcodes, token constants, mutex APIs, VFS APIs, and VDBE memory APIs.

External and platform dependencies include:

- C runtime functions such as `memcpy`, `memset`, `strlen`, `strspn`, `strncmp`, `strcmp`, `strtoll`, `fopen`, `fputs`, `fread`, `fclose`, and `fprintf`;
- math `isnan()` where available;
- pthreads or Win32 `_beginthreadex()` for worker threads;
- Unix headers and calls such as `open`, `close`, `access`, `stat`, `fstat`, `fcntl`, `read`, `pread`, `write`, `pwrite`, `ftruncate`, `unlink`, `mkdir`, `rmdir`, `gettimeofday`, and optional mmap/locking headers.

Integration points include:

- application-facing APIs: `sqlite3_malloc*`, `sqlite3_free`, `sqlite3_realloc*`, `sqlite3_mprintf`, `sqlite3_snprintf`, `sqlite3_str_*`, `sqlite3_log`, `sqlite3_randomness`, `sqlite3_stricmp`, and `sqlite3_strnicmp`;
- parser and error reporting: `%T`/`%S` formatter extensions, error byte offsets, `sqlite3ErrorMsg()`, `sqlite3ErrorToParser()`, and tree-view debugging;
- VDBE and pager encoding: varints, endian integer access, UTF memory translation, rowid/numeric parsing, opcode names, and overflow-checked arithmetic;
- VFS registration: `sqlite3_os_init()` for `SQLITE_OS_KV`, `sqlite3KvvfsInit()` for optional Unix `kvvfs`, and the Unix VFS syscall abstraction used by later file I/O code.

## Risks And Edge Cases

- The allocator path relies on correct mutex discipline. Many connection-scoped functions assert that `db->mutex` is held; violating that can corrupt lookaside freelists or read stale OOM state.
- Lookaside pointer classification is range-based. Incorrect `pStart`, `pMiddle`, `pEnd`, or `pTrueEnd` setup would cause wrong free-list routing or wrong size reporting.
- `db->mallocFailed` is intentionally sticky. Code that bypasses `sqlite3ApiExit()` or clears it too early can make later allocation assumptions unsafe.
- `sqlite3_str_vappendf()` handles width, precision, SQL escaping, UTF-8 character counting, and floating-point rendering in one large state machine. Risks concentrate around large precision/width values, `mxAlloc` enforcement, `%z` ownership transfer, and internal-only format strings being exposed incorrectly.
- `sqlite3_log()` intentionally uses a fixed stack buffer and no dynamic allocation because it can be called while allocator mutexes are held. Format strings used while logging from allocator-sensitive paths must avoid conversions that require temporary allocation.
- UTF conversion behavior around invalid surrogate pairs differs with `SQLITE_REPLACE_INVALID_UTF`. Callers should not assume all malformed UTF is rejected in the same way across builds.
- Numeric parsing has many boundary conditions: 2^63, `SMALLEST_INT64`, signed zero, huge exponents, UTF-16 high bytes, digit separators in quoted numbers, and optional hexadecimal integers.
- Varint decoding assumes callers have enough readable bytes for the encoded value. Short or corrupt database records are normally guarded by higher-level page/record validation.
- Hash keys are not copied by `sqlite3HashInsert()`. The table becomes unsafe if callers pass temporary key storage.
- `kvvfsDecodeJournal()` appears sensitive to malformed length prefixes; the loop increments `i` before using `zTxt[i]` for digit value, so corrupted or unexpected text could produce an incorrect allocation size before decode failure. This VFS is explicitly experimental.
- `kvvfs` has no real locking, returns zero randomness, supports only rollback-journal style methods, and stores binary database content through text expansion. It is mainly a constrained or WASM-oriented storage bridge, not a general durable multi-process filesystem replacement.
- `kvvfsReadDb()` uses a large fixed `SQLITE_KVOS_SZ` scratch buffer and special handling for reads below offset 512. The page-size and offset assertions matter for pager integration.
- The Unix VFS prelude is compile-option dense. Platform macro drift can change locking style, pread/pwrite selection, WASI behavior, permissions, and syscall availability.

## Test Signals

Useful validation signals for this chunk include:

- SQLite OOM and malloc tests that exercise `sqlite3FaultSim()`, malloc alarms, hard memory limits, lookaside allocation and release, `db->mallocFailed` stickiness, and `sqlite3ApiExit()` conversion to `SQLITE_NOMEM`.
- Formatter tests covering `%q`, `%Q`, `%w`, `%z`, `%!s`, `%!c`, `%r`, large width/precision limits, NaN/Infinity handling, UTF-8 width accounting, `sqlite3_mprintf()`, `sqlite3_snprintf()`, and `sqlite3_str_*` growth/error states.
- Parser diagnostics that verify error messages, byte offsets, and debug tree-view output under `SQLITE_DEBUG` and `TREETRACE_ENABLED`.
- PRNG tests using `sqlite3_test_control()` save/restore/reset controls and checks that `sqlite3_randomness()` initializes from the active VFS and is mutex-protected.
- Thread tests with `SQLITE_MAX_WORKER_THREADS>0`, pthread/Win32 paths, and `sqlite3FaultSim(200)` deterministic fallback.
- UTF tests including BOM removal, endian swap, UTF-8 to UTF-16 and back, malformed surrogate handling, `sqlite3Utf8ReadLimited()`, and `sqlite3UtfSelfTest()`.
- Numeric and binary-format tests for integer overflow, 32-bit extraction, decimal/hex parsing, floating-point round trips, varint encode/decode length, big-endian 4-byte helpers, and blob literal conversion.
- Hash and VList tests that cover insertion, replacement, deletion, rehashing after bucket pressure, case-insensitive lookup, and OOM during benign hash resize.
- `EXPLAIN` or debug builds that confirm `sqlite3OpcodeName()` returns names matching generated opcode numbers.
- `kvvfs` tests that open `local` and `session` databases, write pages, sync and reload size state, create/read/truncate rollback journals, delete journal keys, simulate short reads, and exercise optional WASM method replacement.
- Unix VFS tests later in the file should observe that syscall overrides can replace entries in `aSyscall[]` and that feature macros select the intended locking and I/O paths for target platforms.

## Cross-Chunk Notes

This chunk begins in the middle of `malloc.c`; preceding lines define `mem0`, memory-subsystem initialization, and the start of `mallocWithAlarm()`. Later chunks continue `os_unix.c` from the syscall table into concrete Unix file, locking, shared-memory, and VFS method implementations. The final merged research for `sqlite3.c` should connect this infrastructure to the pager, btree, VDBE, parser, and platform VFS code covered in adjacent chunks.

### subset-b-009017: lines 39366-47008

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 39366-47008

## Chunk Purpose

This chunk is the main Unix VFS implementation from SQLite's amalgamated `os_unix.c` section. It connects SQLite's generic `sqlite3_vfs` and `sqlite3_file` interfaces to Unix-like system calls, implements database file locking, ordinary file I/O, WAL shared-memory mapping, mmap-backed fetches, temporary file naming, path canonicalization, dynamic extension loading, randomness/time/sleep services, and Unix VFS registration.

The code is compiled under `SQLITE_OS_UNIX` and is heavily feature-gated for POSIX, VxWorks, macOS locking styles, WAL, mmap, QNX, WASI, F2FS batch atomic write support, loadable extensions, and SQLite test/debug builds. In this vendored copy under WiredTiger tests, it supplies SQLite's storage-facing Unix behavior whenever the test build uses this embedded SQLite source.

## Important APIs, Types, and Functions

- System-call override layer: `aSyscall[]` entries are exposed through macros such as `osRmdir`, `osFchown`, `osMmap`, `osMunmap`, `osMremap`, `osGetpagesize`, `osReadlink`, `osLstat`, and `osIoctl`. `unixSetSystemCall()`, `unixGetSystemCall()`, and `unixNextSystemCall()` implement the `sqlite3_vfs` xSetSystemCall/xGetSystemCall/xNextSystemCall hooks used by tests, embedders, and sandboxes to replace or inspect low-level calls.
- Robust syscall wrappers: `robust_open()` retries EINTR, avoids file descriptors below `SQLITE_MINIMUM_FILE_DESCRIPTOR`, enforces exact journal/WAL permissions when requested, and sets close-on-exec. `robust_ftruncate()` retries EINTR and avoids unsafe >2GiB truncation on Android. `robust_close()` logs but does not retry close failures. `robustFchown()` only calls `fchown()` as root to avoid security-log noise.
- Global and per-inode locking state: `unixBigLock` protects process-wide inode/shared-memory lists; `unixFileId` identifies files by device and inode or by VxWorks canonical path; `unixInodeInfo` tracks per-inode locks, reference counts, deferred close descriptors, optional WAL shared-memory node, and platform-specific state.
- VxWorks canonical IDs: `vxworksFileId`, `vxworksSimplifyName()`, `vxworksFindFileId()`, and `vxworksReleaseFileId()` replace inode identity with canonical absolute path identity on VxWorks.
- POSIX locking methods: `unixCheckReservedLock()`, `unixFileLock()`, `unixLock()`, `posixUnlock()`, `unixUnlock()`, and `unixClose()` implement SQLite's lock ladder over POSIX byte-range locks (`NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, `EXCLUSIVE_LOCK`).
- Alternate locking methods: `nolock*` ignores locks; `dotlock*` uses a sibling `.lock` directory; `flock*` uses `flock()` when `SQLITE_ENABLE_LOCKING_STYLE`; `semX*` uses named semaphores on VxWorks; `afp*` uses macOS AFP byte-range locking through `fsctl`; `nfsUnlock()` uses a two-phase downgrade to work around macOS/BSD NFS lockd behavior.
- File I/O methods: `seekAndRead()`, `unixRead()`, `seekAndWriteFd()`, `seekAndWrite()`, `unixWrite()`, `full_fsync()`, `openDirectory()`, `unixSync()`, `unixTruncate()`, `unixFileSize()`, and `unixFileControl()` implement `sqlite3_io_methods` operations.
- Capacity and file-control helpers: `fcntlSizeHint()` expands files/chunks and may map them; `unixModeBit()` handles query/set file-control bits; `setDeviceCharacteristics()`, `unixSectorSize()`, and `unixDeviceCharacteristics()` advertise sector and `SQLITE_IOCAP_*` flags, including powersafe overwrite, subpage read, QNX filesystem characteristics, and optional F2FS atomic batches.
- WAL shared-memory types: `unixShmNode` is the process-wide representation of a `*-shm` wal-index file for one inode; `unixShm` is the per-connection handle. Lock arrays and masks record local shared/exclusive locks for `SQLITE_SHM_NLOCK` slots.
- WAL shared-memory functions: `unixFcntlExternalReader()`, `unixShmSystemLock()`, `unixShmRegionPerMap()`, `unixShmPurge()`, `unixLockSharedMemory()`, `unixOpenSharedMemory()`, `unixShmMap()`, `unixShmLock()`, `unixShmBarrier()`, and `unixShmUnmap()` implement xShmMap/xShmLock/xShmBarrier/xShmUnmap.
- Mmap fetch functions: `unixUnmapfile()`, `unixRemapfile()`, `unixMapfile()`, `unixFetch()`, and `unixUnfetch()` implement xFetch/xUnfetch when `SQLITE_MAX_MMAP_SIZE>0`.
- I/O method registration: the `IOMETHODS` macro constructs `sqlite3_io_methods` tables and finder functions for POSIX, no-lock, dotfile, flock, semaphore, AFP, NFS, and proxy modes. `autolockIoFinderImpl()` and `vxworksIoFinderImpl()` choose methods based on filesystem or fcntl support.
- VFS operations: `fillInUnixFile()`, `unixOpen()`, `unixDelete()`, `unixAccess()`, `unixFullPathname()`, `unixDlOpen()`, `unixDlError()`, `unixDlSym()`, `unixDlClose()`, `unixRandomness()`, `unixSleep()`, `unixCurrentTimeInt64()`, `unixCurrentTime()`, and `unixGetLastError()` provide the Unix `sqlite3_vfs` method table.
- macOS proxy locking: `proxyLockingContext`, `proxyGetLockPath()`, `proxyCreateLockPath()`, `proxyCreateUnixFile()`, `proxyGetHostID()`, `proxyBreakConchLock()`, `proxyConchLock()`, `proxyTakeConch()`, `proxyReleaseConch()`, `proxyCreateConchPathname()`, `switchLockProxyPath()`, `proxyGetDbPathForUnixFile()`, `proxyTransformUnixFile()`, `proxyFileControl()`, `proxyCheckReservedLock()`, `proxyLock()`, `proxyUnlock()`, and `proxyClose()` move database locks to a local proxy file while coordinating host ownership through a conch file.
- VFS lifecycle: `sqlite3_os_init()` registers Unix VFS variants (`unix`, `unix-none`, `unix-dotfile`, `unix-excl`, and optionally `unix-posix`, `unix-flock`, `unix-afp`, `unix-nfs`, `unix-proxy`, `unix-namedsem`) and initializes `unixBigLock` and temp directories. `sqlite3_os_end()` clears `unixBigLock`.

## Control Flow

Opening starts in `unixOpen()`. It validates SQLite open flags, resets randomness after fork/pid change, optionally reuses deferred file descriptors for main DB files, creates a temp name for unnamed temp files, converts SQLite flags to POSIX flags, determines creation mode/owner from the database for WAL/journals through `findCreateFileMode()`, opens with `robust_open()`, falls back from read-write to read-only when allowed, applies delete-on-close handling, captures filesystem flags, sets `UNIXFILE_*` control bits, optionally enables proxy locking, then delegates to `fillInUnixFile()`.

`fillInUnixFile()` stores the descriptor and VFS pointers in `unixFile`, chooses a locking implementation through the VFS finder, allocates per-inode state when required, creates platform-specific contexts such as AFP, dotlock, or VxWorks semaphores, installs the selected `sqlite3_io_methods`, and verifies the database file for hard-link, symlink, and moved-file hazards.

The POSIX lock path uses in-memory inode state to compensate for POSIX advisory-lock semantics. `unixLock()` checks requested lock ordering, serializes on `pInode->pLockMutex`, returns `SQLITE_BUSY` if another connection in the same process has an incompatible lock, coalesces shared locks within the same process, and only calls `fcntl()` when the process-level state actually transitions. It takes PENDING before SHARED or before upgrading RESERVED to EXCLUSIVE, read-locks the shared range for SHARED, write-locks the reserved byte for RESERVED, and write-locks the shared range for EXCLUSIVE. `posixUnlock()` reverses this, optionally using an NFS-specific split downgrade on macOS, and defers descriptor close until all locks on the inode are gone.

The normal read/write path is direct `pread`/`pwrite` or seek-plus-read/write depending on platform macros. `unixRead()` first satisfies reads from an active mmap region when possible, then calls `seekAndRead()`, zero-filling short reads and distinguishing corrupt filesystem errors. `unixWrite()` tracks debug transaction-counter invariants, writes through mmap when enabled for read-write mappings, loops until the request is complete, and maps short/non-space writes to `SQLITE_FULL` or I/O errors. Sync, truncate, and file-size calls update persistence guarantees and mmap bounds.

WAL shared memory opens lazily on first `unixShmMap()`. `unixOpenSharedMemory()` creates or reuses a `unixShmNode` per inode, opens `<db>-shm` or a configured shared-memory directory file, copies permissions/ownership from the DB, locks the deadman switch through `unixLockSharedMemory()`, then links a per-connection `unixShm`. `unixShmMap()` extends and maps 32KiB regions in page-size-aligned groups, writing the last byte of each new page to reduce later SIGBUS risk. `unixShmLock()` maintains both process-local lock masks and system `fcntl()` locks; in `SQLITE_ENABLE_SETLK_TIMEOUT` builds it uses per-slot mutexes and try-lock behavior to avoid blocking-lock deadlocks.

Mmap fetch control is separate from WAL shared memory. `unixFetch()` maps the database file on demand through `unixMapfile()` and returns a pointer only if the mapping covers the requested bytes plus a 256-byte EOF safety buffer. `unixUnfetch()` decrements outstanding fetch references or unmaps the file on invalidation. Remapping is disabled while fetch references are outstanding.

For macOS proxy locking, a file can be transformed after open. `proxyTakeConch()` obtains or updates the conch file, validates host ID and proxy path, creates/opens the local proxy file, reopens the database descriptor if necessary, and then later `proxyLock()`/`proxyUnlock()` forward lock operations to the proxy file. Stale conch locks may be broken only after host ID and modification-time checks.

`sqlite3_os_init()` builds static VFS tables with xOpen/xDelete/xAccess/xFullPathname/xDl*/xRandomness/xSleep/xCurrentTime/xSetSystemCall hooks and registers each configured Unix VFS with SQLite. The next chunk starts the Windows VFS; this chunk ends the Unix implementation.

## State and Persistence Behavior

- File descriptor state lives in `unixFile`: descriptor `h`, selected VFS, path, lock level, control flags, last errno, directory-sync state, chunk size, mmap fields, and optional locking contexts.
- Cross-connection state for a database inode lives in `unixInodeInfo`, including process-local lock counters, the highest lock level, outstanding lock count, deferred descriptors in `pUnused`, and optional `pShmNode`.
- POSIX locks are persisted in the kernel on fixed byte ranges of the database file. SQLite mirrors them in `unixInodeInfo` to avoid same-process POSIX lock surprises and to avoid close() on one descriptor silently dropping another descriptor's locks.
- Dotlock locking persists as a `"<db>.lock"` directory. Failure to remove it can leave a stale exclusive lock.
- WAL shared memory persists as `"<db>-shm"` unless `unix-excl` simulates shared memory with heap memory. The DMS byte is used to detect first opener and force safe truncation/reinitialization.
- Journal/WAL creation attempts to copy permissions and ownership from the associated database file, preserving recoverability for other users that can write the DB.
- `unixSync()` fsyncs the file and one-time fsyncs the containing directory for newly created journals/WAL files when `UNIXFILE_DIRSYNC` is set.
- Temporary file directory preference is `sqlite3_temp_directory`, `SQLITE_TMPDIR`, `TMPDIR`, `/var/tmp`, `/usr/tmp`, `/tmp`, then `.`.
- Mmap state (`pMapRegion`, `mmapSize`, `mmapSizeActual`, `mmapSizeMax`, `nFetchOut`) is process-local and is dropped on close, truncate shrink, failed mapping, or explicit unfetch invalidation.
- Proxy locking persists a conch file beside the DB and a proxy lock file under the configured or generated local proxy directory. These files are intentionally not deleted.

## Dependencies and Integration Points

- Integrates with SQLite core through `sqlite3_vfs`, `sqlite3_io_methods`, `sqlite3_file_control()` opcodes, SQLite memory allocators, mutexes, random number generation, URI parameter access, logging, and error-code conventions.
- Uses POSIX/Unix APIs: `open`, `close`, `read`, `write`, `pread`, `pwrite`, `lseek`, `fcntl`, `fsync`/`fdatasync`, `ftruncate`, `fstat`, `stat`, `lstat`, `readlink`, `access`, `unlink`, `rmdir`, `mkdir`, `mmap`, `munmap`, optional `mremap`, `getcwd`, `gettimeofday`, `nanosleep`/`usleep`/`sleep`, `dlopen`/`dlsym`/`dlclose`, and platform-specific calls like `fsctl`, `statfs`, `confstr`, `gethostuuid`, `sem_open`, and Linux F2FS `ioctl`.
- WAL integration depends on `SQLITE_SHM_NLOCK==8`, `UNIX_SHM_BASE==120`, and `UNIX_SHM_DMS==128`; `sqlite3_os_init()` asserts those assumptions.
- File-control integration includes lock state, last errno, chunk size, size hints, persistent WAL, powersafe overwrite, VFS name, temp filename generation, moved-file detection, mmap-size limit, lock timeout, block-on-connect, proxy lock file get/set, and external-reader detection.
- Test/debug integrations include `SimulateIOError`, `SimulateDiskfullError`, sync counters, fake current time, deterministic randomness under `SQLITE_TEST`, host-id perturbation for proxy tests, OSTRACE, lock tracing, and debug assertions around transaction-counter updates.

## Risks and Edge Cases

- Lock correctness is the dominant risk. POSIX locks are process-scoped and close-sensitive, so bugs in `nShared`, `nLock`, `eFileLock`, or deferred-close handling can lead to dropped locks or false `SQLITE_BUSY` results.
- Multiple fallback locking modes intentionally reduce concurrency. `nolock`, dotlock, flock, sem, AFP, NFS, and proxy behavior differ substantially; choosing the wrong finder for a filesystem may trade safety, availability, or performance.
- `robust_open()` deliberately rejects file descriptors 0, 1, and 2 and opens `/dev/null` to move past them. This avoids confusing stdin/stdout/stderr with database handles but can fail in constrained environments.
- Directory fsync is best-effort. Some systems cannot fsync directories and the code ignores that failure, leaving a residual crash-recovery risk on filesystems that need directory persistence.
- Short reads are converted to zero-filled buffers with `SQLITE_IOERR_SHORT_READ`, which upper layers expect. Any caller that ignores the return code could consume synthetic zeros.
- `unixRead()` maps selected low-level errors (`ERANGE`, `EIO`, `ENXIO`, `EDEVERR`) to `SQLITE_IOERR_CORRUPTFS`, allowing the higher API exit path to convert them to corruption signals.
- WAL shared-memory initialization carefully avoids using a stale or crash-corrupted `*-shm` file by using the DMS byte and truncating first-open files. Any change to this flow risks database corruption after power loss.
- `unixShmMap()` assumes page writes during extension prevent later SIGBUS. Filesystems with unusual allocation behavior remain a risk.
- Mmap is disabled after a failed mapping by setting `mmapSizeMax=0`; this protects correctness but can cause silent performance fallback.
- Proxy locking is complex and macOS-specific. Stale conch breaking, host ID matching, database descriptor reopening, and proxy path switching are all sensitive to races and filesystem semantics.
- In `proxyCheckReservedLock()`, the lockless branch assigns `pResOut=0` rather than `*pResOut=0`. This is a visible local bug pattern: it does not update the caller's output value if `conchHeld<0`.
- `unixAccess()` only asserts `EXISTS` and `READWRITE` even though comments mention `READONLY`; the implementation treats non-EXISTS as read-write.
- Compile-time feature combinations change behavior heavily. WASI disables Unix mmap/WAL syscalls; Android avoids >2GiB truncate; QNX reports special device capabilities; macOS enables AFP/NFS/proxy/autolock branches.

## Test Signals

- Existing SQLite test hooks are embedded directly: syscall override APIs, `SimulateIOError`, `SimulateDiskfullError`, benign I/O error regions, sync counters, fake current time, deterministic randomness, `sqlite3_hostid_num`, OSTRACE, lock tracing, and many assertions.
- Meaningful tests for this chunk should exercise:
  - VFS registration and default VFS selection under `sqlite3_os_init()`.
  - `xSetSystemCall`/`xGetSystemCall`/`xNextSystemCall` replacement and reset behavior.
  - Opening main DB, WAL, journal, temp, read-only fallback, delete-on-close, and reusable deferred descriptors.
  - POSIX lock transitions, same-process multi-connection shared locks, RESERVED/EXCLUSIVE contention, and close deferral while locks remain.
  - Dotlock/flock/nolock/proxy behavior when those compile-time modes are enabled.
  - Crash-persistence paths: `unixSync()` full/data-only sync, directory sync, journal/WAL ownership/mode preservation, and `unixDelete()` dirsync.
  - Short read zero-fill and corrupt-filesystem error mapping.
  - WAL shared-memory open, DMS first-opener truncation, read-only SHM handling, region extension/mapping, lock slot transitions, external-reader detection, and unmap/delete behavior.
  - Mmap fetch/unfetch reference counting, remap limits, failed mmap fallback, and truncation below mapped size.
  - Path canonicalization, symlink resolution, maximum symlink handling, temp-name collision retries, and dynamic loader error reporting.

## Unresolved Cross-Chunk References

- The definitions of `unixFile`, `UnixUnusedFd`, `sqlite3FileSuffix3()`, global variables such as `randomnessPid`, constants like `PENDING_BYTE`, `SHARED_FIRST`, `SQLITE_OPEN_*`, and many SQLite core helpers are outside this chunk and must be reconciled with earlier amalgamation chunks.
- The Windows VFS starts immediately after this chunk, so any final per-file report should contrast this Unix implementation with later OS-specific implementations only after the Windows chunks are read.

### subset-b-009018: lines 47009-55194

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 47009-55194

## Scope And Purpose

This chunk spans several SQLite amalgamation module boundaries. It begins at the end of the Unix VFS initializer, covers the full Windows VFS implementation (`os_win.c`), then covers the full in-memory database VFS and serialization/deserialization support (`memdb.c`), the full sparse bitmap utility (`bitvec.c`), and the opening comments for the page-cache module (`pcache.c`).

Within the WiredTiger test tree this is vendored SQLite infrastructure used by SQLite tests and by any embedded SQLite execution in the test harness. The code is not WiredTiger-specific, but it is foundational portability logic: it binds SQLite's abstract `sqlite3_vfs` and `sqlite3_io_methods` interfaces to Windows file APIs, implements an optional heap allocator backed by Win32 heaps, supplies public Win32 path/encoding helpers, implements WAL shared-memory on Windows, provides an in-memory VFS used by `sqlite3_serialize()` and `sqlite3_deserialize()`, and implements the `Bitvec` data structure used by pager/transaction code to track page sets.

The chunk ends immediately after the introductory `pcache.c` comments start describing dirty and clean page cache entries. No page-cache implementation is visible in this chunk.

## Unix VFS Tail

The first lines complete Unix VFS registration. The `UNIXVFS(VFSNAME, FINDER)` macro constructs `sqlite3_vfs` objects whose methods point to Unix VFS functions such as `unixOpen`, `unixDelete`, `unixAccess`, `unixFullPathname`, dynamic-loading methods, randomness, sleep, current time, last error, and system-call override hooks. The `aVfs[]` array registers platform-conditional variants including `unix`, `unix-none`, `unix-dotfile`, `unix-excl`, and optional Apple/VxWorks variants such as `unix-posix`, `unix-flock`, `unix-afp`, `unix-nfs`, `unix-proxy`, and `unix-namedsem`.

`sqlite3_os_init()` for Unix registers every VFS in `aVfs[]`, optionally honoring `SQLITE_DEFAULT_UNIX_VFS`, initializes the key-value optional VFS, allocates `unixBigLock`, asserts WAL shared-memory lock byte assumptions, initializes the temp-file directory array, and returns `SQLITE_OK`. `sqlite3_os_end()` for Unix just clears `unixBigLock`. This section integrates with the SQLite core via `sqlite3_vfs_register()` and the global OS lifecycle hooks.

## Windows VFS Data Model

The Windows VFS is compiled under `SQLITE_OS_WIN`. It defines platform availability macros for ANSI and wide APIs, WinRT/WinCE differences, long-path limits, file mapping availability, and deprecated `GetVersionEx` behavior. Many declarations are compile-time gated by `SQLITE_OS_WINNT`, `SQLITE_OS_WINCE`, `SQLITE_OS_WINRT`, `SQLITE_OMIT_WAL`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_WIN32_MALLOC`, and related feature flags.

Important types in this chunk:

- `winFile`: the concrete subclass of `sqlite3_file`. It stores the Windows `HANDLE`, current SQLite lock level, chosen shared lock byte, control flags (`WINFILE_RDONLY`, `WINFILE_PERSIST_WAL`, `WINFILE_PSOW`), last Win32 error, path, chunk-size hint, optional WAL `winShm`, optional WinCE lock state, optional memory-map state, and optional blocking-lock timeout fields.
- `winVfsAppData`: per-VFS app-data that selects an I/O method table and whether locking is disabled.
- `winceLock`: WinCE-only shared locking state, with reader count and pending/reserved/exclusive booleans.
- `winMemData`: optional Win32 heap allocator state with heap handle, ownership flag, and debug magic values.
- `winShmNode` and `winShm`: WAL shared-memory backing state. `winShmNode` represents the process-wide mapped `*-shm` file and tracks regions, locks, reference count, and read-only/unlocked state. `winShm` is per-open-file shared-memory connection state with lock masks and its own lock handle.
- `EntropyGatherer`: a small randomness accumulator used by `winRandomness()`.

## System Call Indirection

The large `aSyscall[]` table maps symbolic names to overridable Windows and Cygwin system-call pointers. Entries include file APIs (`CreateFileW`, `ReadFile`, `WriteFile`, `DeleteFileW`, `GetFileAttributesExW`, `LockFileEx`, `UnlockFileEx`), heap APIs (`HeapAlloc`, `HeapCreate`, `HeapDestroy`, `HeapReAlloc`, `HeapCompact`), mapping APIs (`CreateFileMapping*`, `MapViewOfFile*`, `FlushViewOfFile`, `UnmapViewOfFile`), dynamic loader APIs, timers, randomness inputs, WinRT APIs, UUID APIs, blocking-lock helpers, and Cygwin helpers (`getenv`, `getcwd`, `readlink`, `lstat`, `cygwin_conv_path`).

`winSetSystemCall()`, `winGetSystemCall()`, and `winNextSystemCall()` implement the `sqlite3_vfs` system-call override API. They allow tests and embedders to inject failures, restore defaults, and enumerate active calls. The `sqlite3_os_init()` assertion that `ArraySize(aSyscall)==89` is a strong test signal that any edit to the table must be accompanied by count updates and wrapper consistency.

## Win32 Memory Allocator

When `SQLITE_WIN32_MALLOC` is enabled, SQLite installs a `sqlite3_mem_methods` implementation backed by either an isolated Win32 heap or the process heap:

- `winMemMalloc()`, `winMemFree()`, `winMemRealloc()`, and `winMemSize()` wrap `HeapAlloc`, `HeapFree`, `HeapReAlloc`, and `HeapSize`, validate debug magic, optionally validate heap integrity, and log Win32 errors through `sqlite3_log()`.
- `winMemInit()` creates an isolated heap when configured, with initial and maximum sizes derived from SQLite global heap/cache settings, or falls back to `GetProcessHeap()`.
- `winMemShutdown()` destroys owned heaps and clears allocator state.
- `sqlite3MemGetWin32()` returns the method table and `sqlite3MemSetDefault()` registers it through `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)`.
- Public helpers `sqlite3_win32_compact_heap()` and `sqlite3_win32_reset_heap()` compact or recreate the heap. Reset is guarded by main and memory mutexes and requires the heap to be owned and `sqlite3_memory_used()==0`.

Risk is concentrated around allocator ownership and lifecycle: `winMemShutdown()` can invalidate all allocations from the isolated heap, so callers must only reset/shutdown under the mutex and zero-allocation conditions enforced here.

## Encoding, Directories, Error Reporting, And Retry Policy

The Windows VFS converts between UTF-8, UTF-16, and ANSI/OEM code pages using SQLite heap allocation:

- `winUtf8ToUnicode()`, `winUnicodeToUtf8()`, `winMbcsToUnicode()`, `winUnicodeToMbcs()`, `winMbcsToUtf8()`, and `winUtf8ToMbcs()` are the internal conversion primitives.
- Public wrappers include `sqlite3_win32_utf8_to_unicode()`, `sqlite3_win32_unicode_to_utf8()`, `sqlite3_win32_mbcs_to_utf8()`, `sqlite3_win32_mbcs_to_utf8_v2()`, `sqlite3_win32_utf8_to_mbcs()`, and `sqlite3_win32_utf8_to_mbcs_v2()`. With API armor, null pointers return misuse.
- `sqlite3_win32_set_directory8()`, `sqlite3_win32_set_directory16()`, and `sqlite3_win32_set_directory()` update `sqlite3_data_directory` or `sqlite3_temp_directory` under `SQLITE_MUTEX_STATIC_TEMPDIR`.

`winGetLastErrorMsg()` converts `FormatMessageW/A()` output into UTF-8. `winLogErrorAtLine()` logs a normalized SQLite error code, Win32 code, function name, path, source line, and message. I/O retry behavior is controlled by `winIoerrRetry`, `winIoerrRetryDelay`, `winIoerrCanRetry1()`, optional `winIoerrCanRetry2()`, `winRetryIoerr()`, and `winLogIoerr()`. The retry policy is aimed at transient sharing, antivirus, device, and network errors. `SQLITE_FCNTL_WIN32_AV_RETRY` exposes the retry count and delay for tuning.

## Windows File I/O And Locking

The main `sqlite3_io_methods` implementation is `winIoMethod`; `winIoNolockMethod` swaps in no-op locking functions but keeps the same read/write/truncate/sync/file-control/mmap methods.

Core file operations:

- `winClose()` unmaps memory, retries `CloseHandle()`, handles WinCE delete-on-close cleanup, destroys WinCE lock state, updates the open counter, and logs close failures.
- `winRead()` uses memory mapping when possible, then `ReadFile()` with overlapped offsets except on WinCE/no-overlapped builds. Short reads zero-fill the unread tail and return `SQLITE_IOERR_SHORT_READ`.
- `winWrite()` optionally writes through an mmap region when writable mapping is enabled, otherwise loops until all bytes are written or an unretryable error occurs. Disk-full Win32 errors map to `SQLITE_FULL`; other failures map to `SQLITE_IOERR_WRITE`.
- `winTruncate()` honors `SQLITE_FCNTL_CHUNK_SIZE`, avoids truncation while `xFetch` mappings are outstanding, unmaps/remaps around `SetEndOfFile()`, and treats `ERROR_USER_MAPPED_FILE` specially.
- `winSync()` flushes mapped views first, then calls `FlushFileBuffers()`, unless `SQLITE_NO_SYNC` is defined. Test counters `sqlite3_sync_count` and `sqlite3_fullsync_count` are incremented under `SQLITE_TEST`.
- `winFileSize()`, `winHandleSeek()`, `winSeekFile()`, `winHandleTruncate()`, `winHandleSize()`, and `winHandleClose()` provide reusable handle-level helpers.

Locking maps SQLite's `NO_LOCK`, `SHARED_LOCK`, `RESERVED_LOCK`, `PENDING_LOCK`, and `EXCLUSIVE_LOCK` protocol to Windows byte-range locks. `winLock()` enforces legal transitions, temporarily uses the pending byte while acquiring shared locks, upgrades through pending to exclusive, and falls back to read-lock reacquisition on exclusive-lock failure. `winUnlock()` drops exclusive/shared/reserved/pending byte locks to `SHARED_LOCK` or `NO_LOCK`. `winCheckReservedLock()` probes the reserved byte when the local descriptor does not already hold it.

WinCE lacks native byte-range locking, so `winceCreateLock()`, `winceDestroyLock()`, `winceLockFile()`, and `winceUnlockFile()` emulate lock state with a named mutex and shared file mapping. `winLockFile()` and `winUnlockFile()` route to WinCE emulation, `LockFileEx`/`UnlockFileEx`, or older ANSI APIs depending on platform. `winHandleLockTimeout()` adds optional blocking-lock support via overlapped `LockFileEx()`, events, `WaitForSingleObject`, timeout mapping, and `CancelIo()`.

The no-lock methods (`winNolockLock()`, `winNolockUnlock()`, `winNolockCheckReservedLock()`) are intentionally unsafe for concurrent writers and are only appropriate for read-only/external-locking cases.

## Windows File Control, mmap, And Device Capabilities

`winFileControl()` implements important `xFileControl` operations:

- `SQLITE_FCNTL_LOCKSTATE`, `SQLITE_FCNTL_LAST_ERRNO`, `SQLITE_FCNTL_CHUNK_SIZE`, and `SQLITE_FCNTL_SIZE_HINT`.
- `SQLITE_FCNTL_PERSIST_WAL` and `SQLITE_FCNTL_POWERSAFE_OVERWRITE` through `winModeBit()`.
- `SQLITE_FCNTL_VFSNAME`, `SQLITE_FCNTL_WIN32_AV_RETRY`, `SQLITE_FCNTL_WIN32_GET_HANDLE`, test-only `SQLITE_FCNTL_WIN32_SET_HANDLE`, `SQLITE_FCNTL_NULL_IO`, and `SQLITE_FCNTL_TEMPFILENAME`.
- `SQLITE_FCNTL_MMAP_SIZE`, which caps against `sqlite3GlobalConfig.mxMmap`, handles 32-bit `SIZE_T` limits, and remaps when safe.
- Optional `SQLITE_FCNTL_LOCK_TIMEOUT` and `SQLITE_FCNTL_BLOCK_ON_CONNECT`.

`winSectorSize()` returns `SQLITE_DEFAULT_SECTOR_SIZE`. `winDeviceCharacteristics()` advertises undeletable-when-open and subpage-read, plus powersafe-overwrite when enabled.

Memory-mapped database reads use `winMapfile()`, `winUnmapfile()`, `winFetch()`, and `winUnfetch()`. Mapping size is capped by `mmapSizeMax`, aligned to `winSysInfo.dwPageSize`, and degraded gracefully: create/map failures are logged but normal `xRead`/`xWrite` continues. `winFetch()` requires an extra 256 bytes beyond the requested range to tolerate small parser overreads of corrupt pages and increments `nFetchOut` until `winUnfetch()` releases it.

## Windows WAL Shared Memory

When WAL is enabled, the Windows VFS implements `xShmMap`, `xShmLock`, `xShmBarrier`, and `xShmUnmap`.

`winOpenSharedMemory()` creates or reuses a process-wide `winShmNode` for the `*-shm` path, opens one handle used for mapping and DMS-lock work plus a per-connection handle for locks, initializes node mutexes, and tracks per-node references under `winBigLock`. `winShmPurge()` destroys zero-reference nodes, unmaps all mapped regions, closes mapping handles, optionally deletes the `*-shm` file, and removes the node from `winShmNodeList`.

`winLockSharedMemory()` implements the deadman-switch protocol: it tries for an exclusive DMS lock to detect first opener, truncates the shared-memory file to zero when allowed, releases that lock, then takes a shared DMS lock. Read-only openers that would need initialization return `SQLITE_READONLY_CANTINIT`.

`winShmLock()` maps SQLite shared/exclusive WAL lock requests to byte-range locks beginning at `WIN_SHM_BASE`. It tracks local shared and exclusive lock masks in `winShm`, supports blocking lock timeouts through `winFileBusyTimeout()`, and asserts valid lock-ordering in debug builds. `winShmMap()` lazily creates/truncates the `*-shm` file, grows the `aRegion` array, creates file mappings, maps each region with allocation-granularity offset adjustment, and returns a pointer adjusted to the requested region. If the node is read-only, successful mapping returns `SQLITE_READONLY`.

## Windows VFS Methods And Lifecycle

`winGetTempname()` creates `etilqs_` temporary filenames from `sqlite3_temp_directory`, Cygwin environment variables, Win32 temp paths, or fallbacks, and appends 15 randomized characters salted with the process id. `winIsDir()` checks directory attributes. `winOpen()` converts UTF-8 names to native encoding, rejects directories, translates SQLite open flags to access/share/create/attribute flags, creates temp names when needed, retries transient open failures, downgrades read-write opens to read-only when possible, initializes WinCE locks, sets `winFile` fields and mmap defaults, and returns output flags. The URI parameter `exclusive=1` disables file sharing; `psow` toggles powersafe overwrite for main DBs.

`winDelete()` converts names, rejects directories, retries transient delete failures, maps missing files to `SQLITE_IOERR_DELETE_NOENT`, and logs non-benign failures. `winAccess()` checks existence/read/read-write attributes, treats zero-length files as non-existent for `SQLITE_ACCESS_EXISTS`, and supports the internal `NORETRY` bit to avoid nested antivirus retry loops during `winOpen()` fallback checks.

Path handling includes `winIsLongPathPrefix()`, `winIsDriveLetterAndColon()`, `winIsVerbatimPathname()`, Cygwin `winSimplifyName()`/`mkFullPathname()`, and `winFullPathnameNoMutex()`. Long and UNC paths, `/C:` prefixes, `sqlite3_data_directory`, WinCE/WinRT limitations, Cygwin symlink following, and ANSI/wide full-path APIs are all handled. `winFullPathname()` serializes this through the temp-directory mutex because global directory variables are involved.

Dynamic loading is implemented by `winDlOpen()`, `winDlError()`, `winDlSym()`, and `winDlClose()` unless extension loading is omitted. `winRandomness()` gathers entropy from system time, process id, tick counter, performance counter, and optionally UUID APIs; test or randomness-omitted builds return zero-filled buffers. `winSleep()` rounds microseconds up to milliseconds and calls `sqlite3_win32_sleep()`. `winCurrentTimeInt64()` converts `FILETIME` to SQLite Julian-day milliseconds, with `sqlite3_current_time` overriding under `SQLITE_TEST`; `winCurrentTime()` returns the double Julian-day form. `winGetLastError()` returns `GetLastError()` and formats it if a buffer is provided.

Windows `sqlite3_os_init()` registers four VFS names when available: `win32` as default, `win32-longpath`, `win32-none`, and `win32-longpath-none`. It initializes `winSysInfo` for page size and mapping granularity and allocates `winBigLock` for WAL. `sqlite3_os_end()` closes the WinRT sleep event if allocated and clears `winBigLock`.

## Memdb VFS And Serialization

The `memdb.c` portion is compiled when `SQLITE_OMIT_DESERIALIZE` is not defined. It implements a VFS named `memdb` where database bytes live in a contiguous `MemStore.aData` buffer.

Important types and globals:

- `MemStore`: in-memory file storage with current size, allocation size, maximum size, backing bytes, optional mutex, mmap reference count, deserialize flags, reader/writer lock counters, reference count, and optional shared filename.
- `MemFile`: an open `sqlite3_file` with a `MemStore` pointer and current lock level.
- `memdb_g`: process-global list of shared named `MemStore` objects, protected by `SQLITE_MUTEX_STATIC_VFS1`.
- `memdb_vfs`: VFS object registered by `sqlite3MemdbInit()`. It delegates dynamic loading, randomness, sleep, current time, and last-error behavior to the lower VFS stored in `pAppData`.
- `memdb_io_methods`: in-memory file method table. Shared-memory/WAL methods are null; memdb operates in rollback mode.

`memdbOpen()` creates either a shared store when the filename begins with `/` or `\`, or a separate store for unnamed/private use and `sqlite3_deserialize()`. Shared stores are looked up or inserted in `memdb_g.apMemStore`; separate stores have no global name. New stores default to `SQLITE_DESERIALIZE_RESIZEABLE | SQLITE_DESERIALIZE_FREEONCLOSE` and `sqlite3GlobalConfig.mxMemdbSize`.

`memdbClose()` decrements references, removes the store from the shared array when the final named reference closes, frees `aData` if `SQLITE_DESERIALIZE_FREEONCLOSE` is set, frees the mutex, and frees the store. `memdbRead()` copies from memory and zero-fills short reads. `memdbWrite()` refuses read-only stores, grows the buffer with `memdbEnlarge()` when allowed, zero-fills gaps, and updates `sz`. `memdbTruncate()` only shrinks and returns `SQLITE_CORRUPT` if asked to grow, which should only happen for corrupt WAL-mode input. `memdbSync()` is a no-op, `memdbFileSize()` reports `sz`, and `memdbDeviceCharacteristics()` advertises atomic, powersafe-overwrite, safe-append, and sequential behavior.

`memdbLock()` and `memdbUnlock()` implement SQLite lock levels with `nRdLock` and `nWrLock`; write locks are refused for `SQLITE_DESERIALIZE_READONLY`. `memdbFetch()` exposes direct pointers to immutable/non-resizeable memory and increments `nMmap`; resizeable stores return no mapping so resizing cannot invalidate outstanding pointers. `memdbUnfetch()` decrements `nMmap`.

`memdbFileControl()` supports `SQLITE_FCNTL_VFSNAME` and `SQLITE_FCNTL_SIZE_LIMIT`. Size limits lower than current size are clamped up to current size, and negative input restores the maximum. `memdbAccess()` always reports no disk files, and `memdbFullPathname()` copies the provided name as canonical because memdb names are virtual.

`memdbFromDbSchema()` uses `SQLITE_FCNTL_FILE_POINTER` to retrieve a `MemFile` from a schema and rejects shared named stores. `sqlite3_serialize()` returns the bytes for a memdb database directly, or for ordinary btree-backed schemas computes `PRAGMA page_count`, optionally forces an empty database into existence with `BEGIN IMMEDIATE; COMMIT;`, allocates a buffer, and copies each page through pager APIs. `SQLITE_SERIALIZE_NOCOPY` only succeeds for private memdb stores; ordinary pager-backed databases return null for no-copy mode.

`sqlite3_deserialize()` reopens a schema as memdb by preparing `ATTACH x AS <schema>`, setting `db->init.reopenMemdb`, stepping the statement, locating the resulting `MemFile`, and installing the caller-provided byte buffer plus size, allocation, maximum, and flags. It rejects schema index 1 (`temp`) and invalid sizes under API armor, holds `db->mutex`, and frees `pData` on failure when `SQLITE_DESERIALIZE_FREEONCLOSE` is set. `sqlite3IsMemdb()` tests pointer equality with `memdb_vfs`, and `sqlite3MemdbInit()` registers the VFS above the current default VFS with `szOsFile` large enough for `MemFile`.

## Bitvec Utility

The `bitvec.c` portion implements a fixed-size sparse bitmap whose bits are numbered from 1. SQLite uses it to track pages journaled during a transaction or pages with the pager "dont-write" property. The design optimizes for frequent tests, relatively few sets, rare clears, and very large possible page-number ranges.

`Bitvec` is exactly `BITVEC_SZ` bytes. It has three representations:

- For small ranges (`iSize <= BITVEC_NBIT`), `u.aBitmap[]` is a direct bit array.
- For larger sparse ranges with `iDivisor==0`, `u.aHash[]` is an open-addressed hash table of set bit numbers. `nSet` counts occupied entries.
- When the hash becomes dense (`nSet >= BITVEC_MXHASH`), the object converts to a recursive array of sub-bitmaps in `u.apSub[]`. `iDivisor` defines the range handled by each sub-bitmap.

Public/internal functions:

- `sqlite3BitvecCreate()` allocates and zeroes a bitmap for a maximum bit index.
- `sqlite3BitvecTestNotNull()` and `sqlite3BitvecTest()` test whether a bit is set, walking sub-bitmaps as needed and probing the hash table for sparse large maps.
- `sqlite3BitvecSet()` sets a bit. It recursively creates sub-bitmaps when already subdivided, sets direct bitmap bits for small maps, inserts into the hash for sparse maps, and rehashes into recursive representation once the hash is too full.
- `sqlite3BitvecClear()` clears a bit, walking recursive maps and either clearing a direct bitmap bit or rebuilding the hash table in caller-provided temporary storage.
- `sqlite3BitvecDestroy()` frees recursive sub-bitmaps and the top-level object.
- `sqlite3BitvecSize()` returns the configured maximum.
- `sqlite3BitvecBuiltinTest()` is compiled unless `SQLITE_UNTESTABLE` and executes a small opcode-driven randomized test program against a linear bit-array reference.

Key risks are off-by-one errors because the public bit numbers are 1-based while internal indexes are 0-based, hash-table fullness/rehash behavior, and caller responsibility for valid non-null/range arguments in `sqlite3BitvecSet()` and adequate scratch space in `sqlite3BitvecClear()`.

## State And Persistence Behavior

The Windows VFS persists state in open `winFile` handles, byte-range locks, mapped database views, WAL `*-shm` files, process-global `winShmNodeList`, configurable global retry counters, global temp/data directory strings, optional Win32 heap state, and global VFS registration. File state survives through real filesystem objects, WAL shared-memory files, OS file handles, and memory mappings. The code is careful to unmap before closing/truncating, to close mapping handles, to retry transient sharing violations, and to maintain local lock state in `winFile.locktype`.

The memdb VFS persists database content only in process memory. Shared memdb stores persist while at least one connection references the named store in `memdb_g`; private stores persist only for their owning database connection/file. Deserialized buffers may be owned by SQLite and freed on close, or caller-managed depending on flags. The `nMmap` counter prevents resizing while direct memory pointers are outstanding.

Bitvec state is heap-only and private to its owner. Its representation can mutate from bitmap to hash to recursive sub-bitmaps as density changes, but the externally visible state is just the set of bit numbers up to `iSize`.

## Dependencies And Integration Points

This chunk depends on SQLite core APIs and compile-time configuration: mutex allocation, memory allocation, logging, random bytes, URI parameters, pager/btree APIs, VFS registration, file-control constants, SQLite lock constants, WAL shared-memory constants, and test fault-injection macros (`SimulateIOError`, `SimulateDiskfullError`, `OSTRACE`, `testcase`, `NEVER`, `ALWAYS`).

The Windows VFS integrates directly with Win32/WinRT/WinCE APIs and Cygwin compatibility APIs. Its `sqlite3_vfs` objects are the platform boundary used by all SQLite pager and WAL code on Windows. The memdb VFS integrates with the core VFS registry as a secondary VFS layered over the current default VFS for non-storage services. `sqlite3_serialize()` and `sqlite3_deserialize()` integrate memdb with public SQLite APIs and with btree/pager page access for ordinary database serialization.

The `Bitvec` utility is not a VFS component. It is a pager/transaction support data structure and is expected to be consumed by later chunks that implement journaling and page cache behavior.

## Risks And Edge Cases

- Windows path handling is highly conditional. Long-path prefixes, UNC paths, Cygwin conversion, WinRT relative-path limitations, `sqlite3_data_directory`, and ANSI-vs-wide APIs all have distinct behavior.
- Locking correctness is critical. The byte ranges for pending/reserved/shared locks and WAL locks must match SQLite's cross-process protocol. The no-lock VFS is intentionally dangerous for concurrent writers.
- WinCE lock emulation relies on named mutexes and shared mappings derived from normalized filenames; naming collisions or conversion errors would corrupt lock semantics.
- Retry loops mitigate antivirus/indexer conflicts but can hide timing-sensitive bugs or add latency. `NORETRY` exists to prevent nested retries during access checks.
- mmap logic intentionally degrades to regular I/O on mapping failure, so tests must inspect logs or behavior carefully if mapping coverage matters.
- `winTruncate()` is a no-op when fetch references are outstanding, which can leave files larger than requested but avoids invalidating active mapped cursors.
- `sqlite3_deserialize()` mutates schema state via an internal attach/reopen path and must hold `db->mutex`; failures must free owned buffers exactly once.
- `memdbFetch()` only returns direct pointers for non-resizeable buffers; changing this would risk invalidating outstanding page pointers.
- `Bitvec` has dense/sparse representation transitions and 1-based indexing, both common sources of subtle boundary defects.

## Test Signals

Visible test hooks and signals include:

- `assert(ArraySize(aSyscall)==89)` in Windows `sqlite3_os_init()` and the Unix syscall-count assertion just before this chunk.
- Fault-injection paths through `SimulateIOError`, `SimulateIOErrorBenign`, and `SimulateDiskfullError`.
- Public test globals `sqlite3_sync_count`, `sqlite3_fullsync_count`, `sqlite3_os_type`, and `sqlite3_current_time`.
- VFS system-call override APIs (`xSetSystemCall`, `xGetSystemCall`, `xNextSystemCall`) for injected Win32 failures.
- `SQLITE_FCNTL_WIN32_SET_HANDLE`, `SQLITE_FCNTL_NULL_IO`, `SQLITE_FCNTL_WIN32_AV_RETRY`, lock-timeout controls, mmap-size controls, and file-handle retrieval.
- Logging through `sqlite3_log()` with source line numbers in `winLogErrorAtLine()`.
- `sqlite3BitvecBuiltinTest()`, which compares `Bitvec` operations against a linear bit-array reference and returns the first mismatch.

Practical validation for this chunk should cover Windows VFS open/read/write/truncate/sync/delete/access/full-path behavior, Windows WAL mode and shared-memory locking, WinCE/WinRT/Cygwin conditional builds where supported, memdb shared/private store lifecycle, serialization/deserialization flags and ownership, mmap fetch/unfetch behavior, and Bitvec sparse-to-recursive transition cases.

### subset-b-009019: lines 55195-62132

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 55195-62132

## Scope

This chunk covers four adjacent pieces of the SQLite amalgamation embedded under WiredTiger tests:

- The end of `pcache.c`, SQLite's pager-facing page-cache middleware over the pluggable `sqlite3_pcache_methods2` interface.
- All of `pcache1.c`, the built-in default page-cache implementation and the allocator support behind `SQLITE_CONFIG_PAGECACHE`, `sqlite3PageMalloc()`, and memory-pressure recycling.
- All of `rowset.c`, a transient rowid collection used by the virtual machine to insert, test, and later enumerate rowids.
- The opening and early implementation section of `pager.c`, including WAL declarations, pager state/type definitions, rollback-journal header handling, hot-journal playback, WAL wrappers, savepoint playback, cache/page-size settings, and the beginning of mmap page acquisition.

The final function in this slice, `pagerAcquireMapPage()`, is truncated at line 62132 and continues in the next chunk. Notes below describe only the portion visible here.

## Purpose

The page-cache code provides the in-memory database page lifecycle used by the pager and btree layers. `pcache.c` owns `PgHdr` state, dirty-list ordering, reference counts, cache spill decisions, and the public internal APIs such as `sqlite3PcacheFetch()`, `sqlite3PcacheMakeDirty()`, `sqlite3PcacheDirtyList()`, and cache-size tuning. `pcache1.c` supplies the default low-level cache implementation: page allocation, hash lookup by page number, LRU recycling of unpinned pages, cross-cache page-group accounting, and use of configured static page-cache memory.

`rowset.c` implements a memory-efficient rowid set. It accepts unordered inserts, can test membership by insert batch, or can switch to sorted extraction of the smallest rowid. It avoids per-entry malloc by allocating chunks of `RowSetEntry` objects and builds sorted lists or balanced trees as needed.

The pager section is the beginning of SQLite's durability and locking layer. It defines the `Pager` state machine, rollback-journal format, hot-journal recovery, savepoint rollback, WAL integration points, file locking helpers, page-size/cache/mmap configuration, and several test/debug hooks. This layer is responsible for making database page reads and writes atomic, durable according to synchronous settings, and safe across process locks.

## Important APIs, Types, and Data

### Page Cache Middleware (`pcache.c`)

- `struct PCache`: middleware cache object containing dirty-list heads/tails, `pSynced`, aggregate reference count `nRefSum`, cache/spill sizing, page and extra sizes, purgeability, stress callback, and lower-level `sqlite3_pcache *pCache`.
- `pcacheManageDirtyList(PgHdr *pPage, u8 addRemove)`: central dirty-list mutator. It removes, adds, or moves pages to the front while maintaining `pDirty`, `pDirtyTail`, `pDirtyPrev`, `pDirtyNext`, `pSynced`, and `eCreate`.
- `sqlite3PcacheInitialize()` / `sqlite3PcacheShutdown()`: initialize or tear down the configured pcache module, installing the default `pcache1` implementation when none is supplied.
- `sqlite3PcacheOpen()` / `sqlite3PcacheSetPageSize()` / `sqlite3PcacheClose()`: create middleware state, create or replace the underlying pluggable cache, and destroy it.
- `sqlite3PcacheFetch()`, `sqlite3PcacheFetchStress()`, and `sqlite3PcacheFetchFinish()`: fetch raw `sqlite3_pcache_page` entries, spill a dirty page under memory pressure if needed, then initialize or reference-count the owning `PgHdr`.
- `sqlite3PcacheRelease()`, `sqlite3PcacheRef()`, `sqlite3PcacheDrop()`: reference lifecycle. Clean unreferenced pages are unpinned to the lower cache; dirty unreferenced pages stay on the dirty LRU list.
- `sqlite3PcacheMakeDirty()`, `sqlite3PcacheMakeClean()`, `sqlite3PcacheCleanAll()`, `sqlite3PcacheClearWritable()`, `sqlite3PcacheClearSyncFlags()`: transitions among clean, dirty, writable, and journal-sync-needed states.
- `sqlite3PcacheMove()` and `sqlite3PcacheTruncate()`: rekey a cached page to a new page number or discard pages above a limit.
- `sqlite3PcacheDirtyList()`: returns dirty pages sorted by page number using `pDirty` links and a merge-sort helper, for journal/WAL write ordering.
- Cache instrumentation/tuning: `sqlite3PcacheRefCount()`, `sqlite3PcachePagecount()`, `sqlite3PcacheSetCachesize()`, `sqlite3PcacheSetSpillsize()`, `sqlite3PcacheShrink()`, `sqlite3PCachePercentDirty()`, `sqlite3PcacheIterateDirty()`, and debug-only `sqlite3PcachePageSanity()`.

### Default Page Cache (`pcache1.c`)

- `struct PgHdr1`: default-cache page header. It embeds `sqlite3_pcache_page` first, stores page key `iKey`, ownership, hash-chain link, and LRU links. The database page buffer is allocated immediately before the header to make small btree overreads harmless.
- `struct PGroup`: a page-cache group used for LRU recycling. Depending on configuration, every cache has its own `PGroup` or all purgeable caches share the global `pcache1.grp`.
- `struct PCache1`: low-level cache containing size configuration, purgeability, local free/bulk allocations, hash table, recyclable count, and group pointer.
- `struct PCacheGlobal pcache1`: process-global page-cache allocator state, including configured pagecache slot memory, free-slot list, reserve count, mutexes, and memory-pressure flag.
- `sqlite3PCacheBufferSetup()`: converts a configured static page-cache buffer into a free-list of `PgFreeslot` entries.
- `pcache1InitBulk()`: optional per-cache bulk allocation used for initial pages when `SQLITE_CONFIG_PAGECACHE` has requested local bulk memory.
- `pcache1Alloc()` / `pcache1Free()`: allocate from the configured pagecache slot pool when possible, otherwise fall back to `sqlite3Malloc()`, updating SQLite status counters and memory-debug tags.
- `pcache1AllocPage()` / `pcache1FreePage()`: allocate and free `PgHdr1` page records, using cache-local free pages, bulk memory, global slots, or heap.
- `pcache1ResizeHash()`, `pcache1FetchNoMutex()`, `pcache1FetchWithMutex()`, `pcache1FetchStage2()`: page lookup and allocation algorithm. Existing pages are found by hash; misses can fail cheaply, recycle LRU pages, or allocate new memory depending on `createFlag`.
- `pcache1Unpin()`, `pcache1PinPage()`, `pcache1RemoveFromHash()`, `pcache1TruncateUnsafe()`, `pcache1EnforceMaxPage()`: maintain pinned/unpinned state, LRU membership, hash membership, and configured page limits.
- `sqlite3PCacheSetDefault()`: installs the default `sqlite3_pcache_methods2` vtable with `xInit`, `xCreate`, `xCachesize`, `xFetch`, `xUnpin`, `xRekey`, `xTruncate`, `xDestroy`, and `xShrink`.
- Optional/testing APIs: `sqlite3PcacheReleaseMemory()` under `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `sqlite3PcacheStats()` under `SQLITE_TEST`, `sqlite3HeaderSizePcache1()`, and `sqlite3Pcache1Mutex()`.

### RowSet

- `struct RowSetEntry`: rowid node reused as list node, tree node, and forest-list node.
- `struct RowSetChunk`: chunk allocation containing many entries.
- `struct RowSet`: owns chunks, pending insertion list `pEntry`, last entry, fresh-entry pool, forest of trees for membership testing, sorted/next flags, and current batch id.
- `sqlite3RowSetInit()`, `sqlite3RowSetClear()`, `sqlite3RowSetDelete()`: lifecycle.
- `sqlite3RowSetInsert()`: append a rowid to the pending list, preserving a sorted flag when inserts are increasing.
- `sqlite3RowSetNext()`: sort once if needed, then emit rowids in ascending order; after extraction begins, no more inserts are allowed.
- `sqlite3RowSetTest()`: on each new batch, sorts pending inserts and merges them into a forest of balanced trees; then searches all trees for a prior-batch rowid.
- Helpers `rowSetEntryMerge()`, `rowSetEntrySort()`, `rowSetTreeToList()`, `rowSetNDeepTree()`, and `rowSetListToTree()` implement merge sorting, duplicate removal, and balanced-tree construction.

### Pager And WAL Interfaces

- WAL declarations: `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalBeginReadTransaction()`, `sqlite3WalFindFrame()`, `sqlite3WalReadFrame()`, `sqlite3WalFrames()`, `sqlite3WalCheckpoint()`, savepoint helpers, snapshot helpers, and lock helpers under feature macros. These are forward interfaces used by pager code when `journal_mode=WAL`.
- Pager states: `PAGER_OPEN`, `PAGER_READER`, `PAGER_WRITER_LOCKED`, `PAGER_WRITER_CACHEMOD`, `PAGER_WRITER_DBMOD`, `PAGER_WRITER_FINISHED`, `PAGER_ERROR`.
- `PagerSavepoint`: rollback-journal offsets, per-savepoint bitvec, original db size, sub-journal record index, release behavior, and WAL savepoint data.
- `struct Pager`: core state for VFS handles, locks, journal mode, sync options, dirty/spill controls, page counts, journal offsets, savepoints, cache pointer, backup pointer, mmap state, WAL pointer, and statistics.
- Journal constants/data: `aJournalMagic`, `JOURNAL_PG_SZ()`, `JOURNAL_HDR_SZ()`, `MAX_SECTOR_SIZE`, `UNKNOWN_LOCK`, and `SPILLFLAG_*`.
- Durability helpers: `read32bits()`, `write32bits()`, `journalHdrOffset()`, `writeJournalHdr()`, `readJournalHdr()`, `zeroJournalHdr()`, `readSuperJournal()`, `writeSuperJournal()`, `pager_cksum()`, `pagerSyncHotJournal()`, `pager_playback()`, and `pager_playback_one_page()`.
- Lock/state helpers: `assert_pager_state()`, `pagerLockDb()`, `pagerUnlockDb()`, `pager_wait_on_lock()`, `pager_unlock()`, `pager_error()`, `pager_end_transaction()`, `pagerUnlockAndRollback()`.
- WAL wrappers: `pagerRollbackWal()`, `pagerWalFrames()`, `pagerBeginReadTransaction()`, `pagerOpenWalIfPresent()`, and `pagerUndoCallback()`.
- Public internal pager APIs visible here: `sqlite3PagerDirectReadOk()`, `sqlite3PagerDataVersion()`, `sqlite3PagerSetCachesize()`, `sqlite3PagerSetSpillsize()`, `sqlite3PagerSetMmapLimit()`, `sqlite3PagerShrink()`, `sqlite3PagerSetFlags()`, `sqlite3PagerSetBusyHandler()`, `sqlite3PagerSetPagesize()`, `sqlite3PagerTempSpace()`, `sqlite3PagerMaxPageCount()`, `sqlite3PagerReadFileheader()`, `sqlite3PagerPagecount()`, `sqlite3PagerTruncateImage()`, and `sqlite3SectorSize()`.

## Control Flow

### Page Fetch, Dirtying, And Spill

`sqlite3PcacheFetch()` maps the caller's create request onto the underlying `xFetch()` create mode. A missing page can be fetched only if allowed by `createFlag` and by `PCache.eCreate`, which is optimized according to whether purgeable dirty pages exist. The caller then uses `sqlite3PcacheFetchFinish()` to convert the lower page into a `PgHdr`; first-use initialization zeroes page metadata, sets `pData`, `pExtra`, cache pointer, page number, and `PGHDR_CLEAN`, then re-enters the normal finish path to increment references.

If a cheap fetch fails because the cache is full of dirty pages, `sqlite3PcacheFetchStress()` searches for an unreferenced dirty page to spill. It prefers the oldest unreferenced page without `PGHDR_NEED_SYNC`, using `pSynced` as an approximate cursor, then falls back to the oldest unreferenced dirty page. The pager-provided stress callback writes or journals that page. Only after the stress attempt does it call lower `xFetch(..., 2)` to allocate aggressively.

Dirty-list transitions are centralized in `pcacheManageDirtyList()`. `sqlite3PcacheMakeDirty()` changes a clean page to dirty and adds it to the list. `sqlite3PcacheRelease()` moves an unreferenced dirty page to the front, preserving LRU order used for spill. `sqlite3PcacheMakeClean()` removes from the dirty list, clears write/sync flags, marks clean, and unpins if no references remain.

### Default Cache Lookup And Recycling

`pcache1Fetch()` dispatches to a mutex or no-mutex path depending on group configuration. Lookup first searches `PCache1.apHash[iKey % nHash]`. If found and unpinned, `pcache1PinPage()` removes it from the group LRU before returning it. If not found and creation is allowed, `pcache1FetchStage2()` applies the multi-step policy documented in the code: refuse cheap allocation when too many pages are pinned or memory is pressured, resize the hash if needed, recycle an LRU page when the cache/group is full or pressured, and otherwise allocate a fresh page.

Recycled pages are removed from their old cache's hash table and pinned. They are reused only if allocation sizes match; otherwise they are freed and a fresh page is allocated. New or recycled pages are inserted into the requesting cache's hash table, keyed by page number, marked pinned, and initialized by clearing the first pointer-sized field of `page.pExtra`, which lets the middleware detect uninitialized `PgHdr` state.

`pcache1Unpin()` either frees a page immediately when reuse is unlikely or the group is above its maximum, or links it at the front of the group LRU for later recycling. `pcache1EnforceMaxPage()` trims the oldest LRU pages until global purgeable allocation is within limits and releases cache-local bulk memory when a cache becomes empty.

### RowSet Modes

RowSet has two mutually exclusive read modes. `sqlite3RowSetNext()` is extraction mode: on first call it sorts the pending insertion list if needed, marks `ROWSET_NEXT`, and then advances through `pEntry` in ascending rowid order. When the list is exhausted it clears chunks immediately.

`sqlite3RowSetTest()` is membership mode. When the batch number changes, all pending entries become visible to future tests: the pending list is sorted if needed, then merged into a forest of balanced trees. A tree-list node with empty `pLeft` can accept a new tree directly; otherwise the existing tree is flattened and merged with the new list, carrying duplicate removal through `rowSetEntryMerge()`. The actual lookup is a binary search in each tree in the forest. Inserts between tests with the same batch remain invisible until the batch changes.

### Pager Rollback Journal Flow

The rollback-journal writer uses `writeJournalHdr()` to align to the next sector boundary, update active savepoint header offsets, write the magic, record count placeholder or `0xffffffff`, checksum initializer, original db size, sector size, and page size, then pad to the journal header sector size. `zeroJournalHdr()` finalizes persistent journals either by truncating to zero or zeroing the first 28 bytes, syncing unless `noSync` is set, and optionally enforcing `journalSizeLimit`.

`pager_playback()` is the hot-journal and rollback playback loop. It reads the journal size, checks for a super-journal reference, and skips playback if the referenced super-journal no longer exists. It then repeatedly calls `readJournalHdr()` and plays back `nRec` records with `pager_playback_one_page()`. The first valid header triggers truncation of the database file back to the original page count. `nRec==0xffffffff` means records are inferred from journal size; a zero `nRec` in the final unsynced chunk of a local rollback can also be inferred from remaining file size. Short reads or detected corruption stop playback without treating the database as worse than a partially written journal.

`pager_playback_one_page()` reads page number, page bytes, and optional checksum, rejects illegal page numbers, skips pages outside the rollback target size or already restored in `pDone`, restores page-1 reserve bytes, writes to the database file when the pager state and sync guarantees allow it, updates backups, updates cached copies if present, and reinvokes the page reinitializer. For savepoint rollback where the page is not in cache and cannot be safely written to disk, it temporarily disables spill, fetches the page into cache, and marks it dirty so future reads see the restored content.

`pager_end_transaction()` finalizes an active write transaction. It releases savepoints, finalizes or closes/deletes the journal according to mode (`MEMORY`, `TRUNCATE`, `PERSIST`, `DELETE`, or exclusive-mode behavior), cleans or clears writable cache pages depending on commit/temporary-file policy, truncates cache entries beyond `dbSize`, releases WAL write locks when in WAL mode, truncates the database file after rollback-mode commit when needed, calls `SQLITE_FCNTL_COMMIT_PHASETWO`, and downgrades locks to shared in non-exclusive mode.

### WAL And Savepoint Flow

When WAL is active, read transactions begin through `pagerBeginReadTransaction()`, which ends any previous WAL read transaction, starts a new snapshot, and resets the pager cache if the snapshot changed. Page reads in `readDbPage()` first ask WAL for a frame containing the page and read from the WAL frame if present; otherwise they read from the database file.

`pagerWalFrames()` writes sorted dirty pages to the WAL. On commit it drops pages above the truncate size, updates the change-counter if page 1 is present, calls `sqlite3WalFrames()` with the pager's WAL sync flags, and updates backup destinations. `pagerRollbackWal()` uses `sqlite3WalUndo()` plus a walk of dirty cache pages to discard or reload uncommitted pages via `pagerUndoCallback()`.

`pagerPlaybackSavepoint()` implements rollback to savepoints. For rollback-journal mode it may replay three ranges: main-journal records from the savepoint offset to the next header, later main-journal records after that header, and sub-journal records from the savepoint's sub-record index. A `Bitvec` ensures each page is restored once. For WAL savepoints it delegates WAL position restore to `sqlite3WalSavepointUndo()` and still replays sub-journal pages as needed.

## State And Persistence Behavior

Page-cache state is in-memory but directly affects persistence timing. Dirty pages are not durable until pager code writes them to a rollback journal, WAL, or database file. `PGHDR_NEED_SYNC` prevents unsafe database writes before the rollback journal is synced, and `pSynced` is an optimization for selecting pages that can be spilled without forcing a journal sync. `PCache.nRefSum` controls whether pages are in active use; unreferenced clean pages can be recycled, while unreferenced dirty pages remain tracked for writeback.

The default cache may persist page buffers only for the lifetime of a connection/cache. It can allocate from a process-static pagecache buffer, cache-local bulk allocation, or heap. The persistent database image is never stored in `pcache1`; it is only cached there. `PGroup` LRU behavior affects memory reuse across caches and therefore performance and spill pressure, but not database format.

RowSet state is also transient. It stores rowids in memory associated with a SQLite connection and does not write to disk. The batch semantics are logical state used by query execution: rowids inserted after a test for the same batch are intentionally invisible to that batch.

Pager state is durability-critical. `Pager.eState`, `eLock`, `journalMode`, `journalOff`, `journalHdr`, `dbSize`, `dbOrigSize`, `dbFileSize`, `pInJournal`, `aSavepoint`, `pWal`, sync flags, and spill flags collectively determine whether a transaction can be committed, rolled back, recovered as a hot journal, or left in `PAGER_ERROR`. Journal files encode page records with big-endian fields and checksums seeded by `cksumInit`; super-journal pointers coordinate multi-database atomic commit. Hot-journal rollback syncs the journal before playback so a crash during recovery leaves future recoverers seeing the same journal content.

Temporary and in-memory databases relax persistence. Temporary files default to no-sync and may keep dirty pages in memory on commit if the backing file is not present or dirty percentage is low. `MEMDB` disables normal file I/O and cannot enter persistent pager error paths. WAL mode moves durability decisions to WAL frame appends and checkpoint sync flags, while rollback-journal mode uses journal finalization and database truncation.

## Dependencies And Integration Points

- Pager and btree layers: `pcache.c` exposes `PgHdr` pages to the pager; btree uses the extra page storage immediately after pager/cache headers for `MemPage`.
- Pluggable cache API: `pcache.c` depends on `sqlite3GlobalConfig.pcache2`; `pcache1.c` installs the default implementation through `sqlite3_config(SQLITE_CONFIG_PCACHE2, ...)`.
- SQLite memory subsystem: page-cache allocation uses `sqlite3Malloc`, `sqlite3MallocZero`, `sqlite3_free`, `sqlite3DbMallocRawNN`, memory-debug tags, benign malloc sections, and status counters.
- Mutex and atomic primitives: global and group page-cache state uses `sqlite3_mutex_enter/leave`, `AtomicStore`, and `AtomicLoad`; no-mutex mode relies on single-cache groups.
- VFS and OS I/O: pager code depends on `sqlite3OsOpen`, `sqlite3OsRead`, `sqlite3OsWrite`, `sqlite3OsSync`, `sqlite3OsTruncate`, `sqlite3OsFileSize`, `sqlite3OsLock`, `sqlite3OsUnlock`, `sqlite3OsAccess`, `sqlite3OsDelete`, `sqlite3OsFileControl`, and device-characteristic flags such as `SQLITE_IOCAP_SAFE_APPEND`, `SQLITE_IOCAP_BATCH_ATOMIC`, `SQLITE_IOCAP_POWERSAFE_OVERWRITE`, and `SQLITE_IOCAP_SUBPAGE_READ`.
- WAL subsystem: pager uses the WAL API for snapshots, frame reads/writes, write-lock release, rollback undo, savepoints, database size, and mode switching.
- Backup subsystem: rollback and WAL writes notify or restart `sqlite3_backup` state through `sqlite3BackupUpdate()` and `sqlite3BackupRestart()`.
- Bitvec and savepoint infrastructure: rollback uses `Bitvec` to track journaled or restored pages and prevent duplicate savepoint playback.
- PRAGMA/configuration surfaces: cache size, cache spill, page size, mmap limit, synchronous flags, locking behavior, and busy handler settings are wired through these functions from higher-level SQL pragmas or connection configuration.
- Test/debug builds: `SQLITE_TEST`, `SQLITE_DEBUG`, `SQLITE_CHECK_PAGES`, `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_MAX_MMAP_SIZE`, and WAL feature macros alter available APIs, assertions, and code paths.

## Risks And Maintenance Notes

- Dirty-list invariants are fragile. A page must not be both clean and dirty; `WRITEABLE` implies dirty; `NEED_SYNC` must survive some transitions to avoid writing database pages before the rollback journal is durable.
- `PCache.eCreate` is a performance-sensitive mirror of whether purgeable dirty pages exist. Incorrect updates can cause unnecessary spill searches or overly aggressive allocation.
- `pSynced` is deliberately approximate. Bugs that assume it is exact could choose unsafe spill candidates; current code rechecks reference and `PGHDR_NEED_SYNC` flags before using it.
- `pcache1FetchStage2()` mixes cache-local and group-global limits, memory pressure, and recycling across caches. Incorrect `nPurgeable`, `nRecyclable`, `nPage`, or LRU updates can leak pages, double-free pages, or break cache limits.
- Configured static pagecache memory requires slot-size checks. Allocations larger than `pcache1.szSlot` must fall back to heap; returning too-small slots would corrupt memory because page buffers and headers are packed together.
- RowSet mode assertions matter. Inserts after `sqlite3RowSetNext()` or mixing `Next` with `Test` violate the intended lifecycle. The code relies on assertions rather than runtime error returns.
- RowSet batch semantics are subtle: same-batch tests intentionally ignore inserts performed since the last batch transition. Query logic must choose batch ids correctly.
- Pager error-state handling protects against further corruption after `SQLITE_FULL` or `SQLITE_IOERR`. Clearing `PAGER_ERROR` without discarding cache or leaving a hot journal recoverable would risk stale page data.
- Journal-header parsing treats many corrupt or partial states as `SQLITE_DONE` rather than fatal. This is intentional for crash recovery but makes boundary checks, checksum behavior, and sector-size/page-size validation critical.
- `UNKNOWN_LOCK` exists because failed unlocks can leave the process holding an exclusive lock unbeknownst to SQLite. Hot-journal detection must honor that state to avoid reading an unrolled-back database.
- Super-journal handling allocates and scans child journal names. If a child journal still references the super-journal, the super-journal must not be deleted; deleting too early would break multi-database atomic recovery.
- `pager_playback_one_page()` has an important savepoint path that fetches a page into cache rather than writing the database file. Removing or weakening this can corrupt rollback-to-savepoint behavior for moved or freelist pages.
- WAL and rollback journal paths share pager state but have different persistence guarantees. Code that assumes rollback journal files exist in WAL mode, or assumes WAL rollback rewrites the database file, will be wrong.
- Page-size changes require no outstanding page references and must reset the cache, allocate new temp space with overrun bytes, update lock-page number, and refresh mmap limits.
- This chunk ends inside `pagerAcquireMapPage()`. Any analysis of mmap page lifecycle is incomplete without the following lines, including release behavior and final field initialization.

## Test Signals

Useful validation signals for this chunk include:

- SQLite pager crash-recovery tests that simulate partial journal headers, short reads, checksum mismatches, hot journals, persistent journals, truncate journals, and super-journal multi-database recovery.
- Savepoint rollback tests involving pages moved by incremental vacuum, pages above the current db size, and duplicate records across main journal and sub-journal.
- WAL tests for read-snapshot changes, frame reads, transaction rollback via `sqlite3WalUndo()`, savepoint undo, commit truncation, backup update propagation, and synchronous flag combinations.
- Cache-spill tests that force `sqlite3PcacheFetchStress()` with dirty pages both with and without `PGHDR_NEED_SYNC`, including referenced dirty pages that should not be spilled.
- Page-cache memory tests for `SQLITE_CONFIG_PAGECACHE` slot allocation, heap fallback, local bulk allocation, memory-pressure behavior, `sqlite3_release_memory()` under memory-management builds, and `sqlite3_status()` pagecache counters.
- Cache invariant/debug runs with `SQLITE_DEBUG`, `SQLITE_ENABLE_EXPENSIVE_ASSERT`, and `SQLITE_CHECK_PAGES` to exercise `sqlite3PcachePageSanity()`, dirty-list membership, page hashes, and truncate constraints.
- RowSet tests that cover unordered insert sorting, duplicate elimination, sorted `sqlite3RowSetNext()` extraction, batch visibility in `sqlite3RowSetTest()`, OOM paths during chunk allocation, and lifecycle clearing.
- VFS-focused tests for lock transition busy-handler behavior, sector-size sanitization, powersafe-overwrite sector reduction, `SQLITE_IOCAP_SAFE_APPEND`, batch atomic write eligibility, and direct overflow-read gating.
- Page-size and mmap tests that verify cache reset, temp-space allocation, reserve-byte handling, mmap limit propagation, and page-1 header/version tracking.

### subset-b-009020: lines 62133-68993

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 62133-68993

## Scope and Purpose

This chunk covers the tail of SQLite's pager implementation and the opening half of the WAL implementation inside the amalgamated `sqlite3.c`. The pager portion owns page-cache lifetime, rollback-journal write safety, shared-lock acquisition, page fetch/release paths, transaction begin/commit/rollback, savepoint support, journal-mode transitions, and the bridge APIs that open, checkpoint, and close WAL mode. The WAL portion defines the on-disk WAL format, the transient shared-memory wal-index format, WAL lock layout, frame checksum/encoding rules, wal-index recovery, WAL connection open/close, checkpoint iteration, and the beginning of read-transaction startup.

This is a source chunk report only. The final per-file report for `sqlite3.c` should reconcile this with other chunks.

## Important APIs, Types, and Functions

Pager close and page-cache lifecycle:

- `sqlite3PagerClose(Pager *pPager, sqlite3 *db)` releases mapped-page headers, attempts WAL close/checkpoint when allowed, rolls back or unlocks any active pager state, closes journal and database file handles, closes pcache, frees temp space, and frees `Pager`.
- `pagerReleaseMapPage()` and `pagerFreeMapHdrs()` manage `PGHDR_MMAP` page header reuse and call `sqlite3OsUnfetch()` for memory-mapped pages.
- `sqlite3PagerRef()`, `sqlite3PagerUnrefNotNull()`, `sqlite3PagerUnref()`, and `sqlite3PagerUnrefPageOne()` wrap pcache reference counting with pager-specific rules. Page 1 has a dedicated release path because releasing the last page reference may unlock and rollback the pager.
- `sqlite3PagerLookup()` returns an already cached page without disk I/O.

Rollback journal, dirty-page flushing, and write safety:

- `syncJournal(Pager*, int newHdr)` upgrades to an exclusive lock, syncs and/or patches the rollback journal header depending on `SAFE_APPEND`, `SEQUENTIAL`, and full-sync settings, clears `PGHDR_NEED_SYNC`, and moves the pager to `PAGER_WRITER_DBMOD`.
- `pager_write_pagelist()` writes dirty pages to the database file, skipping pages beyond `dbSize` and pages marked `PGHDR_DONT_WRITE`; it updates `dbFileVers`, `dbFileSize`, write stats, backup state, and page hashes.
- `openSubJournal()`, `subjournalPage()`, and `subjournalPageIfRequired()` support savepoint rollback by writing page images to the sub-journal and setting savepoint bitvecs.
- `pagerStress()` is the pcache spill callback. It prevents unsafe spills under `doNotSpill` flags, writes single WAL frames in WAL mode, or syncs the rollback journal and writes pages in rollback mode.
- `sqlite3PagerFlush()` walks the dirty list and calls `pagerStress()` for unreferenced dirty pages.
- `pager_open_journal()`, `pagerAddPageToRollbackJournal()`, `pager_write()`, `pagerWriteLargeSector()`, and `sqlite3PagerWrite()` are the core "make this page writable" path. They open the rollback journal lazily, journal original content before modification, handle savepoints, mark pages dirty/writeable, and journal all co-resident pages when sectors are larger than pages.
- `sqlite3PagerDontWrite()` marks dirty pages as not worth writing back, primarily for freelist leaf pages during large deletes.

Pager open, locking, transactions, and metadata APIs:

- `sqlite3PagerOpen()` allocates a single memory block containing `Pager`, `PCache`, database/journal/sub-journal file handles, back-pointer metadata, filename strings, URI parameters, journal filename, and WAL filename. It resolves full paths, handles memory/temp/immutable modes, opens the database file when appropriate, selects default page size from VFS characteristics, initializes pcache, and sets pager flags and methods.
- `sqlite3_database_file_object()` relies on the special filename memory layout to recover the owning `Pager` and return the main database `sqlite3_file` for a journal/WAL filename.
- `hasHotJournal()` detects rollback journals needing recovery by checking file existence, reserved locks, database size, and the first journal byte.
- `sqlite3PagerSharedLock()` obtains a shared lock, rolls back hot journals under exclusive lock, validates change counters and cache contents, opens WAL if present, starts WAL read transactions, and computes `dbSize`.
- `sqlite3PagerBegin()` obtains rollback-mode reserved/exclusive locks or a WAL write lock, initializes transaction sizes and offsets, and moves to `PAGER_WRITER_LOCKED`.
- `pager_incr_changecounter()`, `sqlite3PagerSync()`, `sqlite3PagerExclusiveLock()`, `sqlite3PagerCommitPhaseOne()`, and `sqlite3PagerCommitPhaseTwo()` implement two-phase commit. Phase one updates the change counter, optionally uses atomic or batch atomic writes, syncs the journal, writes dirty pages, grows/truncates/syncs the database, and enters `PAGER_WRITER_FINISHED`. Phase two finalizes the journal or WAL transaction.
- `sqlite3PagerRollback()` rolls back active write transactions through savepoint playback/WAL cleanup, journal playback, or transaction end paths, then persists pager errors if rollback failed.
- `pagerOpenSavepoint()`, `sqlite3PagerOpenSavepoint()`, and `sqlite3PagerSavepoint()` allocate savepoint descriptors, bitvecs, WAL savepoint data, release or rollback savepoints, truncate in-memory sub-journals, and handle journal-mode-off error behavior for ZipVFS builds.
- Metadata and control helpers include `sqlite3PagerFilename()`, `sqlite3PagerVfs()`, `sqlite3PagerFile()`, `sqlite3PagerJrnlFile()`, `sqlite3PagerJournalname()`, `sqlite3PagerGetData()`, `sqlite3PagerGetExtra()`, `sqlite3PagerLockingMode()`, `sqlite3PagerSetJournalMode()`, `sqlite3PagerGetJournalMode()`, `sqlite3PagerOkToChangeJournalMode()`, `sqlite3PagerJournalSizeLimit()`, `sqlite3PagerBackupPtr()`, `sqlite3PagerClearCache()`, and stats/refcount helpers compiled for debug/test builds.
- `sqlite3PagerMovepage()` and `sqlite3PagerRekey()` support btree/autovacuum page relocation while preserving rollback and savepoint invariants.

Pager page fetch methods:

- `getPageNormal()` fetches a page through pcache, validates page numbers, initializes cache misses from disk via `readDbPage()` or zero-fill when beyond the database image or `PAGER_GET_NOCONTENT` is set, and sets journal/savepoint bits for no-content pages.
- `getPageMMap()` tries to satisfy eligible readonly page fetches with `sqlite3OsFetch()` and mapped `PGHDR_MMAP` headers, avoiding page 1 and WAL frames.
- `getPageError()` returns the persistent pager error code.
- `sqlite3PagerGet()` dispatches through `pPager->xGet`.

WAL pager bridge APIs:

- `sqlite3PagerCheckpoint()` invokes `sqlite3WalCheckpoint()` and includes a zero-byte WAL-mode bootstrap path through `PRAGMA table_list`.
- `sqlite3PagerWalCallback()`, `sqlite3PagerWalSupported()`, `sqlite3PagerOpenWal()`, `sqlite3PagerCloseWal()`, and optional snapshot/ZipVFS/SEH helpers wrap WAL-layer capabilities for pager callers.
- `pagerOpenWal()` opens the WAL handle, taking an exclusive database lock for heap-memory wal-index mode.

WAL structures and constants:

- `WalIndexHdr` is the replicated shared-memory wal-index header: version, change counter, initialization flag, checksum endianness, encoded page size, `mxFrame`, database page count, last-frame checksum, salt values, and header checksum.
- `WalCkptInfo` stores checkpoint coordination state: `nBackfill`, reader marks, lock byte padding, and `nBackfillAttempted`.
- `Wal` is the per-connection WAL handle, tracking VFS/database/WAL file handles, wal-index pages (`apWiData`), page size, read/write/checkpoint locks, readonly mode, sync/padding policy, unreliable-shm mode, cached header, snapshot state, SEH recovery state, and optional blocking-lock database handle.
- `WalIterator` merges wal-index segments in database page order for checkpointing.
- Format constants include `WAL_MAX_VERSION`, `WALINDEX_MAX_VERSION`, `WAL_WRITE_LOCK`, `WAL_CKPT_LOCK`, `WAL_RECOVER_LOCK`, `WAL_READ_LOCK(i)`, `WAL_NREADER`, `WAL_FRAME_HDRSIZE`, `WAL_HDRSIZE`, `WAL_MAGIC`, `HASHTABLE_NPAGE`, `HASHTABLE_NPAGE_ONE`, `HASHTABLE_NSLOT`, `HASHTABLE_HASH_1`, and `WALINDEX_PGSZ`.

WAL helpers in this chunk:

- `walIndexPageRealloc()` and `walIndexPage()` grow/map wal-index pages using heap memory for exclusive heap-memory mode or VFS `xShmMap()` for normal shared memory. Readonly SHM states set `WAL_SHM_RDONLY`.
- `walCkptInfo()` and `walIndexHdr()` compute typed pointers into wal-index page 0.
- `walChecksumBytes()`, `walEncodeFrame()`, and `walDecodeFrame()` implement WAL header/frame checksum mechanics, salt validation, page-number validation, and big/little-endian checksum selection.
- `walIndexWriteHdr()` writes two copies of `WalIndexHdr` with a barrier between them, intentionally ordering writes opposite of the read path.
- `walLockShared()`, `walUnlockShared()`, `walLockExclusive()`, and `walUnlockExclusive()` wrap VFS shared-memory locks, with exclusive-mode no-op behavior and SEH lock-mask tracking.
- `walHash()`, `walNextHash()`, `walHashGet()`, `walFramePage()`, `walFramePgno()`, `walCleanupHash()`, and `walIndexAppend()` maintain wal-index page-number arrays and linear-probed hash tables.
- `walIndexRecover()` rebuilds the transient wal-index by reading the WAL header and frames, validating checksums/version/page size, appending valid frame mappings, copying private scratch index pages into shared memory, writing a fresh header, and initializing checkpoint/read-mark state.
- `sqlite3WalOpen()` validates format-critical constants, allocates `Wal`, opens the WAL file, records readonly status, and sets sync/padding behavior from device capabilities.
- `sqlite3WalLimit()` changes reset truncation size.
- `walIteratorNext()`, `walMerge()`, `walMergesort()`, `walIteratorInit()`, and `walIteratorFree()` build and consume sorted per-page frame iteration for checkpointing.
- Optional `SQLITE_ENABLE_SETLK_TIMEOUT` helpers enable blocking locks and expose `sqlite3WalWriteLock()` and `sqlite3WalDb()`.
- `walBusyLock()` retries exclusive locks through the busy handler.
- `walPagesize()`, `walRestartHdr()`, `walCheckpoint()`, `walLimitSize()`, `sqlite3WalClose()`, `walIndexTryHdr()`, `walIndexReadHdr()`, `walBeginShmUnreliable()`, and the beginning of `walTryBeginRead()` implement checkpoint/reset/close and read-transaction setup.

## Control Flow and State Transitions

Pager read startup flows through `sqlite3PagerSharedLock()`. In rollback mode it waits for a shared database lock, checks `hasHotJournal()`, upgrades directly to exclusive lock if hot recovery is required, syncs and plays back the hot journal, then validates the cache by comparing the header change-counter bytes at offset 24. After this it probes for an existing WAL file and, if WAL is active, begins a WAL read transaction. On failure it unlocks and returns to `PAGER_OPEN`; on success it enters `PAGER_READER` and records that a shared lock has been held.

Page acquisition is state-dependent through `pPager->xGet`. Normal fetches first consult pcache, then either zero-fill or read from disk. Mmap fetches are used only for eligible readonly pages and fall back to normal fetches if the WAL contains the page, the page is page 1, the mapping fails, or the page must be tracked in pcache.

Write startup flows through `sqlite3PagerBegin()`. In rollback mode it obtains a reserved lock and optionally an exclusive lock; in WAL mode it obtains the WAL write lock and possibly upgrades exclusive locking mode. The first actual write to a page calls `pager_open_journal()` if still in `PAGER_WRITER_LOCKED`, writes the initial journal header, then `pager_write()` journals original page content, updates dirty/writeable flags, writes savepoint records if needed, and grows `dbSize`.

Rollback-mode commit phase one proceeds as a durability pipeline: update page-1 change counters, optionally create the journal file, write a super-journal name, `syncJournal()`, write the dirty list to the database, handle batch atomic-write fallback, ensure file growth/truncation matches the logical database image, and sync the database unless `noSync` delegates that to the caller. Commit phase two finalizes the journal using `pager_end_transaction()`, making the transaction irrevocable after rollback-journal invalidation.

Rollback paths split by mode and current state. WAL mode rolls back to savepoint `-1` then ends the WAL transaction. Rollback mode either ends a locked/no-journal transaction, enters error state for journal-mode-off cache uncertainty, or replays the rollback journal.

WAL recovery begins when `walIndexReadHdr()` cannot cleanly read the double wal-index header. It obtains the write lock, maps page 0, retries the header read, and if still bad calls `walIndexRecover()`. Recovery parses the WAL header, validates version and checksum, reads frames sequentially until invalid or EOF, updates `mxFrame` only on commit frames, writes wal-index mappings, and initializes `nBackfill`, `nBackfillAttempted`, and reader marks.

Checkpoint control in `walCheckpoint()` computes `mxSafeFrame` from reader marks, optionally adjusts read marks under exclusive read locks, builds a `WalIterator` over frames newer than `nBackfill`, syncs the WAL, copies safe frame payloads into database pages in page order, truncates/syncs the database if the whole WAL is checkpointed, advances `nBackfill`, and for restart/truncate modes waits for all non-zero readers before resetting or truncating the WAL.

The read-transaction path at the chunk boundary starts in `walTryBeginRead()`. It bounds retry loops with `WAL_RETRY_PROTOCOL_LIMIT`, sleeps with increasing delays after repeated transient races, optionally uses blocking locks, reads or recovers the wal-index header unless `useWal` is forced, handles unreliable readonly SHM by building/validating a heap-memory index, and then begins selecting a read-mark slot.

## State and Persistence Behavior

Pager persistent state spans database pages, rollback journals, sub-journals, WAL files, and transient/shared page cache state. `Pager` fields such as `eState`, `eLock`, `errCode`, `dbSize`, `dbOrigSize`, `dbFileSize`, `journalOff`, `journalHdr`, `nRec`, `pInJournal`, `aSavepoint`, `nSubRec`, `dbFileVers`, `changeCountDone`, `journalMode`, and `exclusiveMode` define whether page-cache content can be trusted and what must be persisted before database writes.

Rollback-journal safety is centered on writing original page images before setting `PGHDR_WRITEABLE`, syncing the journal before database writes when `PGHDR_NEED_SYNC` is present, and clearing stale persistent-journal headers that could otherwise be mistaken for hot-journal content after a crash. Savepoint state persists page images in the sub-journal plus bitvec membership in each `PagerSavepoint`.

WAL persistence uses a durable WAL file plus transient wal-index shared memory. The WAL file is cross-platform big-endian for headers and frame metadata. The wal-index is native-endian shared memory and is explicitly recoverable from the WAL file after crashes. `WalIndexHdr` is duplicated and checksummed to tolerate concurrent dirty reads. Checkpoint progress is persisted in shared memory through `nBackfill` and read marks, and durable database persistence only becomes complete after WAL sync, database writes, optional database truncate, and database sync.

Memory-mapped pager pages are reference-counted separately from pcache pages and are returned to `pMmapFreelist` after `sqlite3OsUnfetch()`. This means mapped pages are not normal dirty/writeable pages and are rejected by `sqlite3PagerWrite()`.

The pager filename allocation layout is intentionally persistent as an ABI compatibility detail for code that discovers database filenames from WAL/journal filenames. `sqlite3_database_file_object()` depends on the embedded back-pointer immediately before the filename region.

## Dependencies and Integration Points

This code depends heavily on SQLite's VFS and OS abstraction methods: `sqlite3OsOpen()`, `sqlite3OsClose()`, `sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsSync()`, `sqlite3OsTruncate()`, `sqlite3OsFileSize()`, `sqlite3OsFileControl()`, `sqlite3OsFileControlHint()`, `sqlite3OsAccess()`, `sqlite3OsDelete()`, `sqlite3OsFetch()`, `sqlite3OsUnfetch()`, `sqlite3OsShmMap()`, `sqlite3OsShmLock()`, `sqlite3OsShmBarrier()`, and `sqlite3OsShmUnmap()`.

The pager integrates with:

- `PCache` through fetch, stress, dirty-list, clean/drop/move/refcount/stat APIs.
- The btree layer through page data/extra APIs, transaction begin/commit/rollback, savepoints, page movement, locking mode, journal mode, and page writability.
- The backup subsystem through `sqlite3BackupUpdate()` and `sqlite3BackupRestart()`.
- The WAL subsystem through pager bridge calls for open/close/checkpoint/read/write/snapshot behavior.
- URI and filename APIs through preserved filename memory layout and `sqlite3_uri_boolean()`.
- Test/debug infrastructure through `testcase()`, `sqlite3FaultSim()`, counters, trace macros, and optional `SQLITE_TEST` stats.

The WAL layer integrates with:

- VFS shared-memory primitives and lock bytes compatible with unix/windows SHM base offsets.
- Pager via `sqlite3WalOpen()`, `sqlite3WalClose()`, `sqlite3WalCheckpoint()`, `sqlite3WalBeginWriteTransaction()` outside this chunk, read transactions, and frame lookup.
- Busy handlers for checkpoint and lock acquisition.
- Optional builds for SEH, snapshots, blocking locks, ZipVFS, mmap, atomic write, batch atomic write, debug, and test modes.

## Risks and Edge Cases

- Crash consistency depends on subtle ordering: journal header update after data sync, WAL sync before checkpoint database writes, database sync before WAL deletion/truncation, and barrier-separated wal-index header writes. Small reorderings can create corruption windows.
- Persistent rollback journals can contain old valid-looking headers beyond `journalOff`; `syncJournal()` deliberately zeros a following header to avoid hot-journal playback of stale transactions.
- `sqlite3PagerOpen()` embeds compatibility-sensitive filename ordering and a back-pointer. Changing this layout can break external consumers and SQLite filename helper APIs.
- Hot-journal detection intentionally tolerates races and false positives. Recovery code must continue to handle cases where another process rolled back or deleted a journal between existence checks and lock acquisition.
- Page 1 has special lifetime and mmap restrictions. Using normal unref paths for the final page-1 reference would violate pager unlock assumptions.
- `PAGER_GET_NOCONTENT` marks journal/savepoint bitvecs to skip later journaling; misuse can suppress rollback data for pages whose content actually matters.
- Large-sector handling must prevent journal-header insertion between co-resident pages. The `SPILLFLAG_NOSYNC` guard is critical during `pagerWriteLargeSector()`.
- WAL shared-memory reads are intentionally lock-free in places and rely on duplicated headers, checksums, atomic 32-bit loads/stores, and memory barriers. Thread sanitizers may flag benign races.
- Readonly or unreliable SHM mode is complex: heap-memory wal-index fallback must detect writers that checkpoint, truncate, or wrap the WAL between checks.
- WAL checkpointing must respect active reader marks; overwriting database pages newer than a reader's snapshot would break snapshot isolation.
- Retry logic in `walTryBeginRead()` assumes retry races are transient. Persistent protocol violations eventually surface as `SQLITE_PROTOCOL`.
- Build-option branches (`SQLITE_OMIT_WAL`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_USE_SEH`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_ENABLE_SNAPSHOT`) materially change control flow and need configuration-specific testing.

## Test Signals and Verification Hooks

Visible test/debug signals include:

- `sqlite3FaultSim(400)`, `sqlite3FaultSim(600)`, and `sqlite3FaultSim(650)` for commit I/O, wal-index page allocation, and SEH fault injection.
- `testcase()` coverage points around short reads, page-size boundaries, atomic-write paths, read marks, mmap behavior, and journal/sync flags.
- `assert_pager_state()`, `CHECK_PAGE()`, lock-state asserts, wal-index format-size asserts, and expensive hash-table reachability asserts.
- `PAGERTRACE`, `IOTRACE`, `WALTRACE`, and pager/WAL counters for tracing commits, page writes, journal writes, checkpoints, and lock activity.
- `sqlite3PagerStats()`, `sqlite3PagerCacheStat()`, `sqlite3PagerMemUsed()`, refcount helpers, and WAL recovery notices via `sqlite3_log(SQLITE_NOTICE_RECOVER_WAL, ...)`.

High-value behavioral tests for this chunk would exercise:

- Hot-journal recovery after simulated crash, including readonly rollback failure and persistent-journal stale-header handling.
- Commit phase one/two under normal rollback, full-sync, no-sync, journal-mode-off, WAL, atomic-write, and batch atomic-write configurations.
- Savepoint release/rollback with sub-journal truncation and page movement across savepoint boundaries.
- Page cache spill under `PGHDR_NEED_SYNC`, `doNotSpill`, WAL mode, and rollback mode.
- WAL recovery from missing/corrupt/stale `-shm`, partial WAL frames, invalid checksums, unsupported WAL versions, and readonly SHM fallback.
- Checkpoint behavior with active readers, passive/full/restart/truncate modes, busy handlers, interrupts, database growth, WAL truncation, and persistent-WAL file-control responses.

## Chunk Boundary Notes

The chunk begins in the middle of mmap page acquisition cleanup just before `pagerReleaseMapPage()` and ends inside `walTryBeginRead()` while it is selecting read marks. Cross-chunk reconciliation should connect this start to earlier pager mmap allocation logic and connect the end to the remainder of WAL read-transaction setup, frame lookup, writer/commit paths, snapshot APIs, and checkpoint public wrappers.

### subset-b-009021: lines 68994-76298

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 68994-76298

## Purpose

This chunk bridges two major SQLite subsystems in the amalgamated `sqlite3.c` vendored under WiredTiger tests:

- The end of the WAL implementation, covering read transaction snapshot selection, WAL frame lookup/read/write, savepoint undo, checkpoints, exclusive locking mode, snapshot APIs, and the WAL file accessor.
- The beginning of the btree implementation, including btree internal data structures, shared-cache mutex/table-lock logic, page/cell parsing and free-space management, pager-backed btree open/close/configuration, transaction begin/commit/rollback, auto-vacuum page relocation, and initial cursor creation.

The chunk ends in the middle of `sqlite3BtreeCursor()`: it shows the public wrapper through the `p->sharable` branch, but the non-sharable return path continues in the next chunk.

## Important APIs, Types, and Functions

### WAL APIs and helpers

- `walBeginReadTransaction()` and `sqlite3WalBeginReadTransaction()` establish a consistent WAL reader snapshot. They repeatedly call `walTryBeginRead()` until it stops returning `WAL_RETRY`, optionally validating `SQLITE_ENABLE_SNAPSHOT` snapshots under a shared checkpoint lock.
- `sqlite3WalEndReadTransaction()` releases the selected WAL read-lock and first ends any write transaction state held by the same `Wal`.
- `walFindFrame()` and `sqlite3WalFindFrame()` search WAL-index hash tables from newest relevant hash page down to `pWal->minFrame` for the latest frame for a page number not newer than the reader's `pWal->hdr.mxFrame`.
- `sqlite3WalReadFrame()` reads a page payload from the WAL file by deriving the WAL frame offset from `iRead` and page size.
- `sqlite3WalDbsize()` reports the database page count from the current WAL header snapshot.
- `sqlite3WalBeginWriteTransaction()` takes `WAL_WRITE_LOCK`, verifies the shared wal-index header has not changed, and marks `pWal->writeLock`.
- `sqlite3WalEndWriteTransaction()` releases write-lock state and clears redo-checksum state.
- `sqlite3WalUndo()`, `sqlite3WalSavepoint()`, and `sqlite3WalSavepointUndo()` roll back uncommitted WAL frames, recompute WAL-index headers, restore savepoint frame/checksum state, and truncate the WAL on savepoint rollback.
- `walRestartLog()`, `walWriteOneFrame()`, `walRewriteChecksums()`, and `walFrames()` implement log restart, frame serialization, checksum repair after in-transaction overwrites, transaction padding/sync, WAL-index append, and commit header publication.
- `sqlite3WalFrames()` is the SEH wrapper for `walFrames()`.
- `sqlite3WalCheckpoint()` implements the public checkpoint path: it takes the checkpoint lock, optionally takes the writer lock for FULL/RESTART/TRUNCATE, refreshes the wal-index header, calls `walCheckpoint()`, reports frame/backfill counts, and releases locks.
- `sqlite3WalCallback()` returns and clears `pWal->iCallback`, the frame count to pass to a WAL hook.
- `sqlite3WalExclusiveMode()` switches the WAL subsystem between normal and exclusive locking by acquiring or releasing the current read-lock.
- `sqlite3WalHeapMemory()` identifies heap-memory WAL-index mode.
- Under `SQLITE_ENABLE_SNAPSHOT`, `sqlite3WalSnapshotRecover()`, `sqlite3WalSnapshotGet()`, `sqlite3WalSnapshotOpen()`, `sqlite3_snapshot_cmp()`, `sqlite3WalSnapshotCheck()`, and `sqlite3WalSnapshotUnlock()` expose snapshot capture, comparison, opening, validation, recovery of checkpoint-attempt metadata, and checkpoint-lock release.
- `sqlite3WalFramesize()` exists for `SQLITE_ENABLE_ZIPVFS`.
- `sqlite3WalFile()` returns the underlying WAL `sqlite3_file`.

### Btree types and constants

- `MemPage` is the pager-extra structure for one database page. It caches decoded btree-page fields such as page number, page type, header offset, local payload limits, free bytes, cell count, cell pointers, overflow-cell arrays, and function pointers for cell parsing and cell sizing.
- `Btree` is a connection-owned handle. It references a shared `BtShared`, tracks this handle's transaction state, shared-cache linked-list membership, backup count, incremental blob state, and the schema-root `BtLock`.
- `BtShared` owns the underlying pager, page-1 reference, cursor list, schema pointer, mutex, page-size/usable-size, transaction counters, auto-vacuum state, shared-cache locks, writer pointer, temporary cell buffer, and flags such as `BTS_READ_ONLY`, `BTS_PAGESIZE_FIXED`, `BTS_SECURE_DELETE`, `BTS_NO_WAL`, `BTS_EXCLUSIVE`, and `BTS_PENDING`.
- `BtCursor` represents a btree cursor. It stores cursor state, flags, root page, key cache, current page stack, parsed `CellInfo`, page indexes, and optional index `KeyInfo`.
- `BtLock` represents shared-cache table-level locks (`READ_LOCK` or `WRITE_LOCK`) on root pages.
- `CellInfo` describes a parsed cell: key or payload size, payload pointer, local payload bytes, and total local cell size.
- Btree page flags `PTF_INTKEY`, `PTF_ZERODATA`, `PTF_LEAFDATA`, and `PTF_LEAF` encode on-disk page type combinations.
- Cursor states `CURSOR_VALID`, `CURSOR_INVALID`, `CURSOR_SKIPNEXT`, `CURSOR_REQUIRESEEK`, and `CURSOR_FAULT` encode whether a cursor is usable, needs repositioning, or is poisoned by an error.
- Pointer-map macros and constants (`PTRMAP_PAGENO`, `PTRMAP_PTROFFSET`, `PTRMAP_ISPAGE`, `PTRMAP_ROOTPAGE`, `PTRMAP_FREEPAGE`, `PTRMAP_OVERFLOW1`, `PTRMAP_OVERFLOW2`, `PTRMAP_BTREE`) support auto-vacuum page relocation.

### Btree mutex and shared-cache lock APIs

- `sqlite3BtreeEnter()`, `sqlite3BtreeLeave()`, `sqlite3BtreeEnterAll()`, and `sqlite3BtreeLeaveAll()` lock and unlock `BtShared` mutexes in a stable address order for shared-cache btrees. The careful path handles recursive enter attempts and out-of-order sibling locks.
- `sqlite3BtreeHoldsMutex()`, `sqlite3BtreeHoldsAllMutexes()`, and `sqlite3SchemaMutexHeld()` are assert helpers for mutex discipline.
- `sqlite3BtreeEnterCursor()` and `sqlite3BtreeLeaveCursor()` are incremental-blob cursor lock wrappers.
- `sqlite3_enable_shared_cache()` toggles the process-global default for future shared-cache opens.
- `querySharedCacheTableLock()`, `setSharedCacheTableLock()`, `clearAllSharedCacheTableLocks()`, and `downgradeAllSharedCacheTableLocks()` implement table-level shared-cache locking and writer-starvation prevention.
- Debug-only `hasSharedCacheTableLock()` and `hasReadConflicts()` verify callers hold the right table locks and that write cursors do not conflict with other read cursors.

### Btree page, cell, and cursor-position helpers

- `invalidateAllOverflowCache()` and `invalidateIncrblobCursors()` clear cached overflow paths or invalidate incremental blob cursors when rows/pages may change.
- `btreeSetHasContent()`, `btreeGetHasContent()`, and `btreeClearHasContent()` manage the per-transaction bitvec used to preserve rollback correctness for pages moved to and reused from the freelist.
- `saveCursorKey()`, `saveCursorPosition()`, `saveAllCursors()`, `saveCursorsOnList()`, `btreeRestoreCursorPosition()`, `sqlite3BtreeCursorHasMoved()`, `sqlite3BtreeFakeValidCursor()`, and `sqlite3BtreeCursorRestore()` preserve and restore cursor positions across btree modifications or rollback.
- `btreeMoveto()` dispatches to table or index seek after unpacking index records.
- `btreePayloadToLocal()`, `btreeParseCellPtrNoPayload()`, `btreeParseCellPtr()`, `btreeParseCellPtrIndex()`, `btreeParseCell()`, `cellSizePtr()`, `cellSizePtrIdxLeaf()`, `cellSizePtrNoPayload()`, and `cellSizePtrTableLeaf()` decode btree cells and compute local cell sizes. They implement SQLite's overflow payload distribution formula and contain optimized varint scanning for high-frequency paths.
- `ptrmapPageno()`, `ptrmapPut()`, `ptrmapGet()`, and `ptrmapPutOvflPtr()` read and write auto-vacuum pointer-map entries.
- `defragmentPage()`, `pageFindSlot()`, `allocateSpace()`, and `freeSpace()` manage in-page cell-content storage, freeblock chains, fragmentation counts, coalescing, and secure-delete zeroing.
- `decodeFlags()`, `btreeComputeFreeSpace()`, `btreeCellSizeCheck()`, `btreeInitPage()`, and `zeroPage()` initialize and validate `MemPage` metadata from on-disk page bytes.

### Pager-backed btree APIs and transaction functions

- `btreePageFromDbPage()`, `btreeGetPage()`, `btreePageLookup()`, `getAndInitPage()`, `releasePage*()`, and `btreeGetUnusedPage()` bridge pager `DbPage` objects to btree `MemPage` metadata.
- `pageReinit()` is the pager rollback callback that clears and optionally reinitializes btree page metadata after page content is restored.
- `sqlite3BtreeOpen()` opens or reuses a `BtShared`, opens the pager, reads the file header, initializes page size/reserve/autovacuum state, links shared-cache structures, installs busy handlers, and returns a `Btree` handle.
- `sqlite3BtreeClose()` rolls back active work, removes shared-cache references, closes the pager, frees schema and temporary storage, and unlinks the connection handle.
- `sqlite3BtreeSetCacheSize()`, `sqlite3BtreeSetSpillSize()`, `sqlite3BtreeSetMmapLimit()`, `sqlite3BtreeSetPagerFlags()`, `sqlite3BtreeSetPageSize()`, `sqlite3BtreeGetPageSize()`, `sqlite3BtreeGetReserveNoMutex()`, `sqlite3BtreeGetRequestedReserve()`, `sqlite3BtreeMaxPageCount()`, `sqlite3BtreeSecureDelete()`, `sqlite3BtreeSetAutoVacuum()`, and `sqlite3BtreeGetAutoVacuum()` expose pager and btree tuning/configuration.
- `lockBtree()` obtains the pager shared lock, reads and validates page 1, opens WAL if the file header demands WAL mode, adapts page size, computes payload thresholds, and sets `pBt->pPage1`.
- `newDatabase()` and `sqlite3BtreeNewDb()` initialize an empty file as a valid SQLite database page 1.
- `btreeBeginTrans()` and `sqlite3BtreeBeginTrans()` start read/write/exclusive transactions, resolve shared-cache conflicts, invoke busy handling, coordinate WAL writer locks when configured, open pager savepoints, and update transaction state.
- Auto-vacuum functions `setChildPtrmaps()`, `modifyPagePointer()`, `relocatePage()`, `incrVacuumStep()`, `finalDbSize()`, `sqlite3BtreeIncrVacuum()`, and `autoVacuumCommit()` maintain pointer maps and move pages so free pages at the end of the file can be truncated.
- `sqlite3BtreeCommitPhaseOne()`, `btreeEndTransaction()`, `sqlite3BtreeCommitPhaseTwo()`, and `sqlite3BtreeCommit()` implement the two-phase btree commit path over the pager.
- `sqlite3BtreeTripAllCursors()`, `btreeSetNPage()`, `sqlite3BtreeRollback()`, `sqlite3BtreeBeginStmt()`, and `sqlite3BtreeSavepoint()` handle rollback, cursor invalidation or preservation, statement savepoints, and nested savepoint release/rollback.
- `btreeCursor()`, `btreeCursorWithLock()`, and the beginning of `sqlite3BtreeCursor()` initialize cursor structures, assert transaction/lock preconditions, link cursors into `BtShared.pCursor`, mark multiple cursors on the same root, and allocate write-cursor temp space.

## Control Flow

### WAL read/write/checkpoint flow

WAL readers begin by loading a wal-index header and attempting to choose a stable read mark. If the WAL is fully checkpointed or empty, the reader tries read-lock 0 and verifies the live wal-index header still matches the cached header; otherwise it selects the highest suitable read mark not exceeding the current `mxFrame` or requested snapshot frame. If lock acquisition or validation races a writer/checkpointer, `WAL_RETRY` drives the caller loop. Snapshot mode adds a shared checkpoint lock and checks salts plus `nBackfillAttempted` to reject snapshots invalidated by WAL reset or checkpoint progress.

WAL frame lookup is hash-table based. `walFindFrame()` searches hash pages backward from the reader's last frame to `minFrame`, ignores entries newer than the reader snapshot, verifies page-number matches, and stops on the newest match. Reads use the found frame number to compute the WAL frame payload offset.

Writers take `WAL_WRITE_LOCK`, verify the wal-index header is unchanged, optionally restart the log if no readers need old frames, write a WAL header for a new log, serialize dirty pages as frames, pad/sync commit frames as required by synchronous settings, append frame/page mappings to the wal-index, and publish the updated header on commit. If a page is overwritten within the same transaction, the code writes into the earlier frame and later rewrites checksums from `pWal->iReCksum`.

Checkpointing takes the checkpoint lock, optionally takes the writer lock for non-passive modes, refreshes the wal-index header, backfills frames to the database through `walCheckpoint()`, reports log and checkpoint counts, clears the cached header if the pager cache is stale, and releases all locks. Passive checkpoints explicitly disable blocking behavior before reading the header to preserve passive semantics.

### Btree open and transaction flow

`sqlite3BtreeOpen()` allocates a connection-level `Btree`. In shared-cache mode it canonicalizes the filename and looks for an existing `BtShared` with the same VFS and path; otherwise it allocates a new `BtShared`, opens the pager, reads the first 100 bytes of the file, initializes page-size/reserve/autovacuum guesses, and links the shared object into the global shared-cache list. The pager owns page cache and journaling; btree owns page interpretation, schema association, and cursor/transaction state.

`lockBtree()` is the first-page gate. It obtains the pager shared lock, reads page 1, validates the SQLite header, file-format versions, payload fractions, page size, reserve size, and page count. If the file is WAL-mode, it opens WAL and may return with `pPage1` unset so the caller can retry after the pager has access to the latest page-1 image. Once valid, it computes local payload thresholds and pins `pBt->pPage1`.

`btreeBeginTrans()` is the main transaction state machine. It rejects illegal shared-cache conflicts, checks read-only write attempts, queries schema-root shared-cache locks, loops through `lockBtree()` and pager begin while invoking the busy handler only for safe cases, updates `pBt->nTransaction`, table locks, `p->inTrans`, `pBt->inTransaction`, writer ownership, and page-1 database-size metadata, then opens pager savepoints for active SQL savepoints.

Commit phase one runs auto-vacuum if enabled, applies a pending truncate image, and delegates durable journal/database flushing to `sqlite3PagerCommitPhaseOne()`. Commit phase two finalizes the pager journal, downgrades shared state to read, clears `pHasContent`, then `btreeEndTransaction()` releases table locks or downgrades them if other VDBE readers still need a read transaction. Rollback saves or trips cursors, rolls back the pager, reloads page-1 metadata, clears write-transaction state, and ends the btree transaction.

### Btree page and cursor flow

Pager pages are converted into `MemPage` objects stored in pager extra memory. `btreeInitPage()` decodes the page type, initializes offsets and function pointers, records the cell count, and optionally performs cell-size checks. Cell parsing distinguishes table leaf cells, table interior cells without payload, and index cells; overflow sizing follows SQLite's fixed local/overflow distribution formula.

Page allocation inside a btree page uses the freeblock chain first, then defragments if needed, then allocates by lowering the cell-content top pointer. Freeing coalesces adjacent freeblocks, updates fragment counts, optionally zeroes deleted bytes under secure-delete flags, and maintains `nFree`.

Before modifying pages, the code saves cursor positions. Table cursors save rowid only; index cursors copy the full packed key with padding to tolerate later unpacking. Saved cursors release page references and move to `CURSOR_REQUIRESEEK`; restoration later seeks back and may become `CURSOR_SKIPNEXT` if the exact row moved or disappeared.

`btreeCursor()` validates transaction and write preconditions, handles empty database root cases, initializes the caller-provided cursor memory, marks cursors as `BTCF_Multiple` when another cursor uses the same root, links into `BtShared.pCursor`, chooses pager readonly flags for read cursors, and allocates temporary cell space for the first write cursor.

## State and Persistence Behavior

- WAL state is split between the persistent WAL file, the shared-memory wal-index, lock bytes, and private `Wal` fields. Important private fields in this chunk include `hdr`, `readLock`, `writeLock`, `ckptLock`, `minFrame`, `iCallback`, `iReCksum`, `truncateOnCommit`, and snapshot pointers/flags.
- WAL persistence is guarded by frame checksums, salts, sync policy, checkpoint backfill counters, and header comparison after locks are obtained. The code is careful to retry instead of trusting a snapshot if a writer or checkpointer may have changed the log between observing and locking.
- Btree persistent state is the SQLite database file page format: page 1 file header, btree page headers, cell pointer arrays, cell content/freeblock areas, overflow chains, freelist trunk/leaf pages, and optional pointer-map pages.
- `BtShared` holds process-local interpretation of a database file: page size, usable size, payload limits, transaction counters, read-only/fixed-page-size/secure-delete flags, and the page-1 reference. These fields are guarded by `BtShared.mutex`.
- Shared-cache table locks are in-memory only (`BtShared.pLock`, `pWriter`, `BTS_PENDING`, `BTS_EXCLUSIVE`) and are cleared/downgraded on transaction end.
- `pHasContent` is a transient transaction bitvec used so rollback journaling remains correct when a page is freed and then reused in the same write transaction.
- Auto-vacuum pointer maps are persistent pages. Relocation updates both child/overflow pointer maps and the parent page pointer before shrinking the database image.
- Pager integration is responsible for durable journaling, rollback, savepoint storage, WAL opening, page reference counts, syncing, file-size/page-count discovery, mmap/cache/spill settings, and busy-handler invocation.

## Dependencies and Integration Points

- The WAL code depends on SQLite VFS and pager-adjacent primitives: `sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsSync()`, `sqlite3OsFileSize()`, `sqlite3OsUnfetch()`, WAL lock helpers, wal-index hash/page helpers, atomic shared-memory access, and `SEH_TRY` wrappers.
- The btree layer depends heavily on the pager API: `sqlite3PagerOpen()`, `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerBegin()`, `sqlite3PagerRollback()`, `sqlite3PagerCommitPhaseOne/Two()`, `sqlite3PagerOpenSavepoint()`, `sqlite3PagerSavepoint()`, `sqlite3PagerMovepage()`, cache/mmap/spill setters, WAL open/write-lock helpers, page refcount/unref functions, and the `pageReinit()` callback.
- Shared-cache behavior integrates with `sqlite3` connection mutexes, `sqlite3ConnectionBlocked()`, `sqlite3GlobalConfig.sharedCacheEnabled`, `SQLITE_MUTEX_STATIC_OPEN`, `SQLITE_MUTEX_STATIC_MAIN`, and database handle lists.
- Cursor movement integrates with VDBE record handling through `sqlite3VdbeAllocUnpackedRecord()`, `sqlite3VdbeRecordUnpack()`, `sqlite3BtreeIndexMoveto()`, and `sqlite3BtreeTableMoveto()`.
- Database file interpretation depends on endian helpers (`get2byte`, `get4byte`, `put2byte`, `put4byte`), varint decoders, corruption reporting macros, and compile-time options such as `SQLITE_OMIT_WAL`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_ENABLE_SETLK_TIMEOUT`, `SQLITE_ENABLE_SNAPSHOT`, `SQLITE_ENABLE_CURSOR_HINTS`, and `SQLITE_SECURE_DELETE`.
- WiredTiger uses this SQLite amalgamation as third-party test code, so integration risk is mostly inherited SQLite behavior and compile-option compatibility rather than direct WiredTiger storage-engine code.

## Risks and Edge Cases

- WAL reader correctness depends on rechecking read marks and wal-index headers after locks. Missing those retries could let a reader combine database pages and WAL frames from incompatible snapshots.
- Snapshot mode is sensitive to races with checkpointers. The code takes a shared checkpoint lock and uses `nBackfillAttempted`, but older snapshot availability still depends on checkpoint progress and WAL salts.
- WAL checksum repair after overwriting frames in the current transaction is subtle: `pWal->iReCksum` must cover the earliest overwritten frame before commit.
- Passive checkpoint semantics are fragile: it must not invoke busy handlers or block on locks except as allowed, while FULL/RESTART/TRUNCATE may downgrade to passive behavior if writer-lock acquisition fails.
- Btree page parsing is security- and corruption-sensitive. The code checks freeblock order, cell offsets, usable-size bounds, max cell count, valid page flags, overflow pointer bounds, and 65536-byte page special cases.
- Free-space management must maintain exact fragment counts and ordered freeblock chains. Incorrect coalescing or allocation can corrupt page layout or break later integrity checks.
- Cursor preservation is memory-sensitive for index keys: the code allocates padding because later record unpacking may overread corrupt keys by a bounded amount.
- Shared-cache locking has deadlock and starvation risks. `BTS_PENDING` prevents new transactions while a writer waits, and `btreeBeginTrans()` deliberately avoids busy-handler invocation for read-to-write upgrade deadlock cases.
- Auto-vacuum relocation must update parent pointers, overflow pointers, and pointer-map entries consistently. A missed pointer-map update can make subsequent vacuum or integrity checks fail.
- Page-size and WAL-mode negotiation in `lockBtree()` may require retrying with `pBt->pPage1==0`; callers must preserve that loop.
- The chunk ends mid-function, so any analysis of `sqlite3BtreeCursor()` must be reconciled with the next chunk before producing a final per-file report.

## Test Signals

- WAL evidence/test macros in this chunk include `testcase()` branches for busy, IO, protocol, page-size bounds, WAL sync padding, and checkpoint return cases; `WALTRACE()` emits frame/checkpoint/read/write tracing in debug/test builds.
- `SQLITE_ENABLE_EXPENSIVE_ASSERT` in `walFindFrame()` linearly scans WAL frames to assert that hash-table lookup found the same result.
- Many Btree paths use `testcase()` and TH3 references around corrupt database page layouts, such as corrupt page flags, bad freeblock chains, cell offsets, page size, and WAL/database page-size mismatches.
- Debug-only functions and asserts check mutex ownership, shared-cache table locks, read conflicts, cursor ownership, cell-size parse equivalence, transaction-state integrity, and open cursor counts.
- Fault-injection hooks include `SEH_TRY`/`SEH_EXCEPT`, `SEH_INJECT_FAULT`, `sqlite3FaultSim(410)`, and malloc failure branches.
- Runtime validation signals include return codes `SQLITE_CORRUPT_BKPT`, `SQLITE_CORRUPT_PAGE`, `SQLITE_NOTADB`, `SQLITE_BUSY`, `SQLITE_BUSY_SNAPSHOT`, `SQLITE_LOCKED_SHAREDCACHE`, `SQLITE_READONLY`, `SQLITE_NOMEM_BKPT`, `SQLITE_DONE`, and `SQLITE_ERROR_SNAPSHOT`.
- User-visible SQL exercises that would traverse this chunk include WAL-mode reads/writes/checkpoints/snapshots, shared-cache reads and write conflicts, `PRAGMA page_size`, `PRAGMA secure_delete`, `PRAGMA auto_vacuum`, `VACUUM`/incremental vacuum, transaction commit/rollback/savepoint behavior, incremental blob invalidation, and opening cursors on tables/indexes.

### subset-b-009022: lines 76299-83658

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 76299-83658

## Scope

This chunk is the main middle of SQLite's btree implementation in the WiredTiger vendored SQLite amalgamation. It starts with cursor lifecycle and payload access helpers, then covers cursor navigation, table/index search, page allocation and free-list management, cell construction, page editing, btree balancing, insert/delete/table lifecycle operations, btree metadata access, integrity checking, and the beginning of the online backup implementation.

The preceding chunk sets up the lower-level btree page parsing, cursor opening, shared-cache/transaction context, and helper types used here. The following chunk continues from the middle of `sqlite3_backup_finish()` into the rest of backup, pager integration, and later SQLite subsystems.

## Purpose

This range turns parsed btree pages into the core row/index operations used by the VDBE and schema layer. Its responsibilities are:

- Maintain `BtCursor` state while reading, seeking, and walking table or index btrees.
- Read and write payload bytes that may be split between a local cell body and linked overflow pages.
- Allocate, free, and recycle database pages through the file-header freelist and autovacuum pointer maps.
- Construct and remove cells, including overflow chains.
- Rebalance btree pages after inserts and deletes, including special root-height changes.
- Create, clear, and drop table/index root pages while preserving autovacuum root-page layout.
- Expose btree metadata, row counts, transaction/checkpoint helpers, and incremental-blob writes.
- Verify btree, freelist, overflow-chain, pointer-map, and page-coverage integrity for `PRAGMA integrity_check`.
- Begin implementing `sqlite3_backup_*` by wiring source/destination btrees and copying pages through the pager.

## Important APIs, Types, and Functions

- Cursor lifecycle and cached cell information:
  - `sqlite3BtreeCursorSize()` exposes the rounded `BtCursor` storage size to callers that preallocate opaque cursors.
  - `sqlite3BtreeCursorZero()` initializes a cursor while intentionally skipping large page/index stack arrays.
  - `sqlite3BtreeCloseCursor()` unlinks a cursor from `BtShared.pCursor`, releases held pages, clears overflow/key caches, and closes single-use btrees when appropriate.
  - `getCellInfo()` lazily fills `BtCursor.info` using `btreeParseCell()` and marks `BTCF_ValidNKey`.
  - `sqlite3BtreeCursorIsValidNN()`, `sqlite3BtreeIntegerKey()`, `sqlite3BtreeOffset()`, `sqlite3BtreePayloadSize()`, `sqlite3BtreeMaxRecordSize()`, `sqlite3BtreeCursorPin()`, and `sqlite3BtreeCursorUnpin()` expose cursor status, rowid/payload metadata, file offsets, and pin state.

- Payload and overflow access:
  - `getOverflowPage()` follows an overflow chain, using autovacuum pointer-map entries as a fast path when possible.
  - `copyPayload()` centralizes page-cache write barriers for payload copy operations.
  - `accessPayload()` reads or writes a byte range from a cursor's current payload, spanning local cell bytes and overflow pages, maintaining `BtCursor.aOverflow` as a lazy page-number cache.
  - `sqlite3BtreePayload()` and `sqlite3BtreePayloadChecked()` expose payload reads; the checked variant restores cursor position for incremental blob reads.
  - `fetchPayload()` and `sqlite3BtreePayloadFetch()` return a direct ephemeral pointer to local payload bytes for the common no-overflow case.
  - `sqlite3BtreePutData()` writes fixed-size incremental blob data through `accessPayload()` after restoring/saving cursors and validating write locks.

- Cursor movement and search:
  - `moveToChild()`, `moveToParent()`, `moveToRoot()`, `moveToLeftmost()`, and `moveToRightmost()` maintain the cursor page stack (`apPage[]`, `aiIdx[]`, `iPage`, `ix`) and validate page type consistency.
  - `sqlite3BtreeFirst()` and `sqlite3BtreeLast()` position cursors at the first/last entry, with `BTCF_AtLast` optimization for repeated last-entry checks.
  - `sqlite3BtreeTableMoveto()` performs integer-key table search with binary search per page and a fast adjacent-key/append path.
  - `sqlite3BtreeIndexMoveto()` performs index-key search using `UnpackedRecord`, `RecordCompare`, direct local-cell comparison where possible, and `accessPayload()` for overflow index keys.
  - `sqlite3BtreeNext()` and `sqlite3BtreePrevious()` implement forward/backward cursor stepping, including restoration from `CURSOR_REQUIRESEEK`/`CURSOR_SKIPNEXT`.
  - `sqlite3BtreeEof()` and `sqlite3BtreeRowCountEst()` provide EOF and approximate row-count signals.

- Page allocation, freelist, overflow clearing:
  - `allocateBtreePage()` obtains a page from the freelist or extends the database image. It supports `BTALLOC_ANY`, exact-page allocation, and less-than-or-equal allocation for autovacuum relocation.
  - `freePage2()` and `freePage()` put a page on the freelist, zeroing content under `BTS_SECURE_DELETE` and updating autovacuum pointer maps.
  - `clearCellOverflow()` walks and frees overflow pages for a cell, rejecting impossible page numbers and unexpected extra references.
  - `BTREE_CLEAR_CELL` parses a cell and clears overflow only when payload spills off-page.

- Cell creation and page editing:
  - `fillInCell()` serializes a `BtreePayload` into SQLite cell format, including local payload sizing, overflow-page allocation, zero-fill for zeroblobs, and pointer-map entries.
  - `dropCell()` removes a cell pointer from a page and returns its content area to the in-page freeblock list.
  - `insertCell()` and `insertCellFast()` insert local cells or stage overflow cells in `MemPage.apOvfl[]` when a page is temporarily overfull.
  - `CellArray`, `populateCellCache()`, `cachedCellSize()`, `rebuildPage()`, `pageInsertArray()`, `pageFreeArray()`, and `editPage()` are the balancing workbench: they cache ordered cell pointers/sizes and rewrite pages while avoiding overlap/corruption hazards.

- Balancing and mutation:
  - `balance_quick()` handles the append-heavy case by allocating a new right sibling for a single rightmost overflow cell.
  - `copyNodeContent()`, `balance_nonroot()`, and `balance_deeper()` handle page redistribution, root growth, root shrinking, pointer-map repair, page-number reordering, and old-page freeing.
  - `balance()` chooses among quick, deeper, and non-root balancing and walks upward until parent pages are also fixed.
  - `btreeOverwriteContent()`, `btreeOverwriteOverflowCell()`, and `btreeOverwriteCell()` optimize same-size replacements by writing only changed bytes in local and overflow storage.
  - `sqlite3BtreeInsert()` inserts or replaces table/index entries, saves other cursors, invalidates incremental blobs, builds cells or consumes preformatted transfer cells, clears replaced overflow, and rebalances.
  - `sqlite3BtreeTransferRow()` preformats a row from one btree cursor into another btree's temp cell buffer, allocating destination overflow pages as needed.
  - `sqlite3BtreeDelete()` deletes the current entry, optionally preserves cursor position, replaces internal-node separators from the predecessor leaf, frees overflow, and rebalances.

- Table, metadata, and count APIs:
  - `btreeCreateTable()` / `sqlite3BtreeCreateTable()` allocate and initialize new root pages. In autovacuum databases they keep root pages dense near the front by relocating pages and updating `BTREE_LARGEST_ROOT_PAGE`.
  - `clearDatabasePage()`, `sqlite3BtreeClearTable()`, and `sqlite3BtreeClearTableOfCursor()` recursively clear table content and optionally count deleted cells.
  - `btreeDropTable()` / `sqlite3BtreeDropTable()` clear and free a root page, relocating the maximum root page into the gap under autovacuum.
  - `sqlite3BtreeGetMeta()` and `sqlite3BtreeUpdateMeta()` read/write database header meta slots, with `BTREE_DATA_VERSION` sourced from the pager and `BTREE_INCR_VACUUM` mirrored into `BtShared.incrVacuum`.
  - `sqlite3BtreeCount()` traverses all non-overflow btree pages and counts leaf entries, with interrupt checks.
  - `sqlite3BtreePager()`, `sqlite3BtreeGetFilename()`, `sqlite3BtreeGetJournalname()`, `sqlite3BtreeTxnState()`, `sqlite3BtreeCheckpoint()`, `sqlite3BtreeIsInBackup()`, `sqlite3BtreeSchema()`, `sqlite3BtreeSchemaLocked()`, `sqlite3BtreeLockTable()`, `sqlite3BtreeSetVersion()`, `sqlite3BtreeCursorHasHint()`, `sqlite3BtreeIsReadonly()`, `sqlite3HeaderSizeBtree()`, `sqlite3BtreeClearCache()`, `sqlite3BtreeSharable()`, and `sqlite3BtreeConnectionCount()` are support APIs used by pager, WAL, schema, shared-cache, backup, tests, and higher layers.

- Integrity checking:
  - `checkOom()`, `checkProgress()`, `checkAppendMsg()`, `getPageReferenced()`, `setPageReferenced()`, `checkRef()`, `checkPtrmap()`, `checkList()`, `btreeHeapInsert()`, `btreeHeapPull()`, `checkTreePage()`, and `sqlite3BtreeIntegrityCheck()` implement btree integrity validation.
  - The checker tracks page references in a bitmap, verifies freelist and overflow chains, checks autovacuum pointer maps, enforces rowid ordering and balanced tree depth, and uses a min-heap of byte ranges to detect overlapping cell/freeblock storage and fragmentation-count mismatches.

- Backup API beginning:
  - `struct sqlite3_backup` stores source/destination handles, current page number, error state, page counts, and pager-callback linkage.
  - `findBtree()`, `setDestPgsz()`, `checkReadTransaction()`, `sqlite3_backup_init()`, `isFatalError()`, `backupOnePage()`, `backupTruncateFile()`, `attachBackupObject()`, and the opening of `sqlite3_backup_step()` begin the online backup implementation.

## Control Flow

Cursor reads start by ensuring the cursor is valid and that its page and cell index are coherent. `getCellInfo()` parses the cell only once per cursor position. Local payload bytes are copied directly from the current page. If the requested range extends past `nLocal`, `accessPayload()` follows the overflow chain, optionally jumping through `aOverflow[]` when prior calls have cached page numbers. Reads may use direct file I/O for full overflow pages when `SQLITE_DIRECT_OVERFLOW_READ` is enabled and pager conditions permit. Writes always go through `sqlite3PagerWrite()` before modifying page bytes.

Search and traversal are layered. `moveToRoot()` restores or obtains the root page, handles virtual root page 1, validates table-vs-index page type, and sets `CURSOR_VALID` or `CURSOR_INVALID`. Table seeks (`sqlite3BtreeTableMoveto()`) binary-search integer keys on each page and descend through child pointers until a leaf. Index seeks (`sqlite3BtreeIndexMoveto()`) compare serialized records against `UnpackedRecord`; small local keys avoid extra allocation, while overflow keys are copied into a padded heap buffer before record comparison. `Next` and `Previous` use fast leaf-local index increments/decrements when possible and fall back to parent/child stack navigation otherwise.

Page allocation first tries the freelist recorded in page 1 header fields at offsets 32 and 36. It can extract a trunk page, a leaf page from a trunk, or search for a requested page in autovacuum modes. If no freelist page is available, it extends `BtShared.nPage`, skips the pending-byte page, creates pointer-map pages when needed, updates the database size in page 1, obtains the new page from the pager, and marks it writable. Freeing a page increments the freelist count, optionally zeroes content for secure delete, writes pointer-map state, and either appends the page as a freelist leaf or turns it into a new trunk.

Insertion builds a new cell in `BtShared.pTmpSpace` unless `BTREE_PREFORMAT` is supplied. Same-key, same-size replacements can use in-place overwrite, including overflow pages. Otherwise old overflow is cleared, the old cell is dropped, and the new cell is inserted into the leaf or temporarily staged in `apOvfl[]` if the page does not have room. If a page overflows, `balance()` repairs the tree, possibly growing the root first with `balance_deeper()`, using `balance_quick()` for rightmost append patterns, or redistributing siblings with `balance_nonroot()`.

`balance_nonroot()` is the densest control-flow block in this range. It selects up to three old sibling pages plus divider cells from the parent, removes relevant parent divider cells, creates a `CellArray` containing all sibling/divider/overflow cells in sort order, computes how many pages are needed, adjusts cell packing from right to left so pages are legal and reasonably balanced, allocates or reuses pages, optionally reorders page numbers for scan locality, repairs pointer maps, reinserts divider cells into the parent, rewrites sibling pages in an order that avoids overwriting source cells before they are copied, handles root-shrink when a root has a single child, and frees old pages that are no longer reused.

Deletion restores the cursor if needed, may save the current key to preserve position, and for internal-node cells first moves to the predecessor leaf. It writes the target page, frees overflow, drops the cell, then for internal-node deletes copies the predecessor cell into the internal page and removes it from the leaf. It balances the leaf first and then, when necessary, climbs back to balance the original internal page. Depending on `BTREE_SAVEPOSITION`, it leaves the cursor invalid, in `CURSOR_REQUIRESEEK`, or in `CURSOR_SKIPNEXT`.

Table creation and drop are autovacuum-aware. Creation chooses a root page after the current largest root page, avoiding pointer-map and pending-byte pages. If the allocated page differs from the desired root page, it relocates the current page at the root slot elsewhere, updates pointer maps, then zeroes the new root with table or index page flags. Drop clears all descendants first, then either frees the root directly or moves the highest-numbered root page into the dropped root slot and decrements the header's largest-root-page metadata.

The integrity-check path starts by allocating a page-reference bitmap and a page-sized heap, marks the pending-byte page as referenced, optionally scans the freelist, then recursively checks each requested root. `checkTreePage()` reinitializes each page to exercise corruption detection, verifies rowid ordering from right to left, validates overflow-chain lengths, checks child depths, and uses heap-sorted byte spans to ensure page header/cell-pointer area, cells, and freeblocks do not overlap and that untracked fragmented bytes match the page header.

The backup path begins by validating source/destination handles, rejecting same-connection source/destination pairs, resolving database names to btrees, ensuring the destination has no open transaction, and incrementing the source btree's backup count. `sqlite3_backup_step()` locks source and destination, opens a source read transaction if needed, starts a destination write transaction, enforces WAL/memory page-size constraints, copies source pages through `backupOnePage()`, attaches the backup object to the source pager when incomplete, and on completion updates the destination schema cookie and begins page-size-sensitive truncation/commit handling. This chunk ends inside `sqlite3_backup_finish()`.

## State and Persistence Behavior

`BtCursor` state is highly transient but correctness-critical. Movement invalidates `BtCursor.info.nSize`, `BTCF_ValidNKey`, and `BTCF_ValidOvfl`. `apPage[]` and `aiIdx[]` retain the ancestry stack for navigation and balancing. `BTCF_AtLast` is an optimization flag that must be cleared on movement except when explicitly set by last-entry positioning. `CURSOR_REQUIRESEEK`, `CURSOR_SKIPNEXT`, and `CURSOR_INVALID` encode deferred restoration after writes or deletes.

Payload persistence is split between page-local cell bytes and overflow pages. Overflow pages store a 4-byte next-page number followed by payload bytes. `BtCursor.aOverflow` is only a cache; it must be invalidated after cursor movement, writes by other cursors, table changes, and autovacuum page moves. The durable state is the cell body plus overflow-chain pages and, in autovacuum databases, pointer-map entries for `PTRMAP_OVERFLOW1` and `PTRMAP_OVERFLOW2`.

Free-space and page-allocation state is durable in page 1 and freelist trunk/leaf pages. Header offset 32 stores the first freelist trunk, offset 36 stores the free-page count, offset 28 stores the database page count, and metadata slot 4 stores the largest root page. Allocation and free operations journal/write page 1 and affected trunk pages through the pager before mutation.

Balancing persists changes across multiple sibling pages, parent divider cells, right-child pointers, pointer maps, and freed pages. Because an error during balancing can leave pages partially modified, callers rely on the surrounding write transaction and pager rollback to restore consistency. This code therefore returns errors promptly but does not try to manually undo every partial page edit.

Table lifecycle operations mutate persistent btree shape and schema-facing metadata. `sqlite3BtreeClearTable()` leaves the root page allocated but empty. `sqlite3BtreeDropTable()` frees or relocates root pages. `sqlite3BtreeUpdateMeta()` writes header metadata and mirrors incremental-vacuum state into memory. `sqlite3BtreeSetVersion()` writes the database header read/write version bytes at offsets 18 and 19, opening a write transaction only if values need changing.

Integrity-check state is in-memory only except for temporary pager page references. It intentionally restores `db->flags` after temporarily disabling `SQLITE_CellSizeCk`, frees `aPgRef` and heap buffers, and asserts that pager reference counts match their entry value.

Backup state persists in `sqlite3_backup` across calls. The destination btree may remain locked after partial backup progress, `iNext` records the next page to copy, `nRemaining` and `nPagecount` report progress, `isAttached` indicates pager callback registration, and `pSrc->nBackup` prevents unsafe source lifecycle changes.

## Dependencies and Integration Points

This code is tightly integrated with SQLite's pager layer: `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerUnref()`, `sqlite3PagerGetData()`, `sqlite3PagerDirectReadOk()`, `sqlite3PagerRekey()`, `sqlite3PagerPageRefcount()`, `sqlite3PagerDontWrite()`, `sqlite3PagerCheckpoint()`, `sqlite3PagerClearCache()`, `sqlite3PagerFilename()`, `sqlite3PagerJournalname()`, `sqlite3PagerDataVersion()`, `sqlite3PagerTempSpace()`, `sqlite3PagerCommitPhaseOne()`, `sqlite3PagerTruncateImage()`, and related file APIs (`sqlite3OsRead()`, `sqlite3OsWrite()`, `sqlite3OsTruncate()`, `sqlite3OsFileSize()`, `sqlite3PagerSync()`) enforce journaling, rollback, direct reads, and file-size changes.

Autovacuum support depends on pointer-map helpers (`ptrmapGet()`, `ptrmapPut()`, `ptrmapPutOvflPtr()`, `setChildPtrmaps()`, `relocatePage()`, `PTRMAP_ISPAGE()`, `PTRMAP_PAGENO()`, `PTRMAP_BTREE`, `PTRMAP_ROOTPAGE`, `PTRMAP_FREEPAGE`, `PTRMAP_OVERFLOW1`, `PTRMAP_OVERFLOW2`). These links are updated whenever cells, child pages, overflow pages, or root pages move.

The VDBE and SQL layers consume table/index cursor APIs for opcodes such as seek, next/prev, insert, delete, count, rowid, payload read, incremental blob, and schema/table creation. Index comparison depends on `UnpackedRecord`, `RecordCompare`, `sqlite3VdbeFindCompare()`, `sqlite3VdbeRecordCompare()`, `KeyInfo`, and record-encoding assumptions.

Shared-cache and transaction correctness use mutexes and locks: `sqlite3BtreeEnter()/Leave()`, `cursorOwnsBtShared()`, `cursorHoldsMutex()`, `hasSharedCacheTableLock()`, `querySharedCacheTableLock()`, `setSharedCacheTableLock()`, `hasReadConflicts()`, transaction states (`TRANS_NONE`, `TRANS_READ`, `TRANS_WRITE`), and read-only flags (`BTS_READ_ONLY`).

Memory allocation uses SQLite allocators and stack/page allocators (`sqlite3Malloc()`, `sqlite3MallocZero()`, `sqlite3Realloc()`, `sqlite3_free()`, `sqlite3StackAllocRaw()`, `sqlite3StackFree()`, `sqlite3PageMalloc()`, `sqlite3PageFree()`, `sqlite3DbMallocZero()`). Fault-simulation hooks (`sqlite3FaultSim(412/413)`) intentionally exercise rare corruption/OOM paths.

Integrity check integrates with connection progress and interrupt hooks (`db->xProgress`, `db->nProgressOps`, `AtomicLoad(&db->u1.isInterrupted)`), `sqlite3_str` accumulation, `Mem` counters for per-root row counts, and compile-time gates such as `SQLITE_OMIT_INTEGRITY_CHECK` and `SQLITE_OMIT_AUTOVACUUM`.

Backup integrates with public SQLite handles and parser/database lookup helpers (`sqlite3FindDbName()`, `sqlite3OpenTempDatabase()`, `sqlite3ParseObjectInit()`, `sqlite3ParseObjectReset()`, `sqlite3ErrorWithMsg()`), btree transaction APIs, pager backup callback lists, WAL mode, schema cookie updates, and destination schema reset.

## Risks and Edge Cases

- Cursor cache invalidation is subtle. Reusing `BtCursor.info` or `aOverflow` after movement, writes, balancing, autovacuum relocation, or table creation can read stale page numbers or payload sizes.
- Overflow-chain code must guard integer overflow and corrupt page numbers. This chunk checks payload bounds, premature chain termination, page numbers greater than `nPage`, page 0/1 misuse for overflow, and reference counts before freeing overflow pages.
- Direct overflow reads bypass the page cache only under strict pager conditions. Incorrect conditions could return stale WAL content or miss dirty cache pages.
- `balance_nonroot()` has a large blast radius: it mutates parent cells, sibling pages, pointer maps, page numbers, and freelist state. Any bug can corrupt btree ordering or orphan pages. Its read-before-write ordering and `CellArray.apEnd[]` checks exist to avoid overwriting source cells before they are copied.
- Secure-delete and fast-secure-delete modes affect whether divider cells can be referenced in-place after `dropCell()`. This code copies divider cells to temporary space when zeroing would destroy bytes needed later.
- Autovacuum root-page movement is fragile. Creating or dropping tables can relocate arbitrary pages, including pages that open cursors may have fetched. The code saves all cursors and invalidates overflow caches to avoid stale xFetch references.
- Same-size overwrite optimizations avoid full drop/insert and balancing. They must only be used when pointer-map and overflow invariants remain valid; autovacuum cases with new overflow pages are excluded from the simple overwrite path.
- Incremental blob writes cannot change payload length. They rely on the cursor still pointing to an intkey row and on `accessPayload()` returning corruption instead of partial writes for out-of-range offsets.
- Integrity checking is intentionally tolerant of partial checks. When `aRoot[0]==0`, it skips global freelist/all-pages coverage except for the special root-1 case, so partial integrity checks cannot prove every page is reachable.
- Backup page-size conversion has special pending-byte and WAL/memory-database restrictions. The destination cannot be WAL or in-memory with mismatched page sizes, and final truncation must journal trailing destination pages before destructive file truncation.
- Many branches are compile-time gated (`SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_INCRBLOB`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_OMIT_WAL`, `SQLITE_DIRECT_OVERFLOW_READ`, `SQLITE_OMIT_QUICKBALANCE`), so behavior and test coverage vary by build.

## Test Signals

- Cursor tests should cover first/last, forward/backward iteration over leaf and interior pages, empty tables, virtual root page 1, cursor restoration after writes, `CURSOR_SKIPNEXT`, `CURSOR_REQUIRESEEK`, and repeated `sqlite3BtreeLast()` using `BTCF_AtLast`.
- Payload tests should exercise local-only payloads, single and multi-page overflow chains, partial reads/writes at local/overflow boundaries, direct-overflow-read builds, corrupted overflow next pointers, premature chains, and invalid cell payload offsets.
- Table/index seek tests should cover exact and inexact rowid searches, append-biased inserts, adjacent-key optimization, index keys with local and overflow storage, custom collations/record compares, and OOM while copying overflow index keys.
- Allocation/free tests should cover empty freelists, trunk extraction, leaf extraction, exact-page autovacuum allocation, `BTALLOC_LE`, pending-byte skips, pointer-map pages at file extension, secure-delete zeroing, and invalid freelist counts or leaf counts.
- Balancing tests should force quick balance, root growth, root shrink, sibling redistribution with one/two/three pages, overflow parent cells, page-number reordering, autovacuum pointer-map updates, and rollback after injected pager/OOM errors.
- Insert/delete tests should cover in-place same-size overwrite, replacement with different payload size, index overwrite, rowid table insert with incremental blob invalidation, delete from leaf and internal pages, delete with position preservation, and schema-corrupt duplicate-root cursor cases.
- Table lifecycle tests should cover create/drop under normal and autovacuum modes, max-root-page metadata updates, relocation of highest root page, clearing tables with row-count output, and rejection of out-of-range page numbers.
- Integrity-check tests should detect double page references, invalid child/overflow/freelist page numbers, bad pointer-map entries, rowid ordering errors, child-depth mismatches, overlapping cell/freeblock byte ranges, fragmentation-count mismatches, max-root-page header disagreement, and interrupt/progress-handler cancellation.
- Backup tests should cover same-source/destination rejection, missing database names, opening temp database on demand, destination-in-use rejection, partial step/resume progress, source busy during write transaction, page-size mismatch behavior under WAL/memory destinations, final schema-cookie bump, truncation when source pages are smaller than destination pages, and error persistence through `sqlite3_backup` state.

### subset-b-009023: lines 83659-91725

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 83659-91725

## Scope

This chunk covers the tail of SQLite `backup.c`, the full amalgamated `vdbemem.c`, most of `vdbeaux.c`, and the opening of `vdbeapi.c`. It starts while `sqlite3_backup_finish()` is unwinding a backup object and ends inside `sqlite3_value_type()`'s type lookup table.

The main covered subsystems are:

- Backup progress helpers, source-page invalidation handling, backup restart, and `sqlite3BtreeCopyFile()` for VACUUM-style whole-file copies.
- VDBE `Mem` and `sqlite3_value` storage management, type conversion, string/blob ownership, aggregate finalization, rowset storage, expression-to-value extraction, STAT4 probe values, btree payload loading, and value byte/text APIs.
- VDBE program construction, opcode array growth, labels, P4 payload ownership, EXPLAIN/EQP/scanstatus support, btree usage masks, shared-cache entry/leave, register/cursor/frame allocation, VM ready/rewind/reset/finalize/delete paths, statement metadata, transaction commit/halt handling, and auxiliary-data cleanup.
- Record serialization/deserialization helpers, unpacked-record allocation, record comparison fast paths, index rowid/key comparison, change counters, statement expiration, bound-value extraction, pure-function checks, virtual-table error import, and pre-update hook dispatch.
- Public VDBE APIs at the start of `vdbeapi.c`: `sqlite3_expired()`, `sqlite3_finalize()`, `sqlite3_reset()`, `sqlite3_clear_bindings()`, and the beginning of the `sqlite3_value_*()` accessors.

## Purpose

The purpose of this range is to bridge SQLite's high-level prepared-statement API and SQL value semantics to the low-level VDBE execution engine, btree payload format, pager transaction model, and extension callbacks. It defines how an individual SQL value is represented and converted, how bytecode programs are assembled and made executable, how VM resources are owned and released, and how statement completion commits or rolls back database state.

Within WiredTiger this file is third-party SQLite test code under `test/3rdparty/sqlite3`. The implementation is not WiredTiger storage-engine logic, but it is still relevant to repository behavior because test tooling that embeds this amalgamation inherits SQLite's exact memory, transaction, and API semantics.

## Important APIs, Types, and Functions

### Backup Tail

The backup section exposes `sqlite3_backup_remaining()` and `sqlite3_backup_pagecount()` for progress reporting. `backupUpdate()` and `sqlite3BackupUpdate()` keep active backup destinations synchronized when a source page already copied by the backup is modified. `sqlite3BackupRestart()` rewinds active backup objects to page 1 when external changes make prior copied pages unreliable.

`sqlite3BtreeCopyFile()` builds a stack `sqlite3_backup` object with `pDestDb == 0` to distinguish internal use from public backup API use. It copies all pages from one btree to another in a single `sqlite3_backup_step()` call, issues an overwrite file-control hint when possible, clears the destination page-size-fixed flag on success, and clears the destination pager cache on failure.

### `Mem` and `sqlite3_value`

The `vdbemem.c` block is centered on `Mem`, SQLite's internal representation for SQL values and the implementation backing `sqlite3_value`.

Important invariant and allocation helpers include:

- `sqlite3VdbeCheckMemInvariants()` verifies dynamic ownership, type-bit exclusivity, pointer-null encoding, `zMalloc` size consistency, and string/blob ownership flags in debug builds.
- `sqlite3VdbeMemGrow()`, `sqlite3VdbeMemClearAndResize()`, `sqlite3VdbeMemMakeWriteable()`, `sqlite3VdbeMemNulTerminate()`, and `vdbeMemAddTerminator()` manage writable allocations and null terminators.
- `sqlite3VdbeMemRelease()`, `sqlite3VdbeMemReleaseMalloc()`, `sqlite3VdbeMemSetNull()`, and `vdbeMemClearExternAndSetNull()` release external destructors, aggregate contexts, dynamic strings, and owned allocation buffers.
- `sqlite3VdbeMemSetStr()`, `sqlite3VdbeMemSetZeroBlob()`, `sqlite3VdbeMemSetPointer()`, `sqlite3VdbeMemSetInt64()`, and `sqlite3VdbeMemSetDouble()` populate `Mem` cells using SQLite's destructor conventions (`SQLITE_STATIC`, `SQLITE_TRANSIENT`, `SQLITE_DYNAMIC`, or a custom destructor).

Type conversion is handled by `sqlite3VdbeIntValue()`, `sqlite3VdbeRealValue()`, `sqlite3VdbeBooleanValue()`, `sqlite3VdbeIntegerAffinity()`, `sqlite3VdbeMemIntegerify()`, `sqlite3VdbeMemRealify()`, `sqlite3VdbeMemNumerify()`, `sqlite3VdbeMemCast()`, `sqlite3VdbeMemStringify()`, `sqlite3VdbeChangeEncoding()`, and `sqlite3ValueText()`. These functions preserve SQLite's dynamic typing rules, including `MEM_IntReal`, NaN-as-NULL behavior, integer/real round-trip safeguards, UTF-8/UTF-16 conversion, and forced `CAST` semantics.

Aggregate and window function values are finalized by `sqlite3VdbeMemFinalize()` and `sqlite3VdbeMemAggValue()`, which construct a `sqlite3_context`, invoke `xFinalize` or `xValue`, and replace or populate result `Mem` cells.

Copy and movement APIs include `sqlite3VdbeMemShallowCopy()`, `sqlite3VdbeMemCopy()`, and `sqlite3VdbeMemMove()`. Shallow copies deliberately convert dynamic source storage into ephemeral/static references, while full copies call `sqlite3VdbeMemMakeWriteable()` when a string/blob needs independent storage.

`sqlite3VdbeMemFromBtree()` and `sqlite3VdbeMemFromBtreeZeroOffset()` load btree payload bytes into `Mem` objects, either by copying or by using an ephemeral pointer returned by the btree cursor when enough bytes are locally available.

Expression and STAT4 helpers (`valueFromExpr()`, `sqlite3ValueFromExpr()`, `stat4ValueFromExpr()`, `sqlite3Stat4ProbeSetValue()`, `sqlite3Stat4ValueFromExpr()`, `sqlite3Stat4Column()`, and `sqlite3Stat4ProbeFree()`) convert literal, bound-variable, vector, and limited deterministic-function expressions into `sqlite3_value` or `UnpackedRecord` probe values for planning.

### VDBE Program Construction and Metadata

`sqlite3VdbeCreate()` allocates and links a new VM into `sqlite3.pVdbe`, initializes it in `VDBE_INIT_STATE`, and emits the initial `OP_Init`. `sqlite3VdbeSetSql()` stores SQL text and prepare flags. Optional normalization helpers track double-quoted strings.

Opcode construction is handled by `growOpArray()`, `sqlite3VdbeAddOp0/1/2/3()`, `sqlite3VdbeAddOp4()`, `sqlite3VdbeAddOp4Int()`, `sqlite3VdbeAddOp4Dup8()`, `sqlite3VdbeAddOpList()`, `sqlite3VdbeGoto()`, `sqlite3VdbeLoadString()`, `sqlite3VdbeMultiLoad()`, and `sqlite3VdbeAddFunctionCall()`. These functions allocate opcode slots, initialize profiling/coverage/comment fields, and attach P4 payloads such as function contexts, strings, integers, reals, key info, tables, subprograms, and virtual tables.

Label and jump resolution is split across `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `resolveP2Values()`, `sqlite3VdbeJumpHere()`, and `sqlite3VdbeJumpHereOrPopInst()`. `resolveP2Values()` also computes read-only and reader flags and maximum virtual-table argument counts, making it a critical finalization pass before a VM is packaged.

`freeP4()`, `vdbeFreeOpArray()`, `sqlite3VdbeChangeP4()`, `sqlite3VdbeAppendP4()`, and `sqlite3VdbeChangeToNoop()` define opcode P4 ownership. P4 payloads can own memory, references, function definitions, `KeyInfo`, `Mem`, virtual tables, table references, subprogram signatures, or function contexts, and each P4 type has distinct destructor rules.

Metadata and diagnostics include `sqlite3VdbeExplain()`, `sqlite3VdbeExplainPop()`, `sqlite3VdbeDisplayP4()`, `sqlite3VdbeDisplayComment()`, `sqlite3VdbeList()`, `sqlite3VdbeNextOpcode()`, `sqlite3VdbeScanStatus*()`, `sqlite3VdbePrintOp()`, `sqlite3VdbePrintSql()`, and `sqlite3VdbeIOTraceSql()`.

### VM Runtime State, Cleanup, and Transactions

`sqlite3VdbeMakeReady()` packages a constructed VM by resolving labels, computing statement-journal needs, allocating `aMem`, `aVar`, `apArg`, and `apCsr`, initializing memory arrays, and rewinding the VM. It reuses unused opcode-array tail space before allocating a separate `pFree` block.

Cursor and frame cleanup is centralized in `sqlite3VdbeFreeCursorNN()`, `closeCursorsInFrame()`, `sqlite3VdbeFrameRestore()`, `closeAllCursors()`, `sqlite3VdbeFrameDelete()`, and `sqlite3VdbeFrameMemDel()`. Cursors may own btree cursors, sorter state, virtual-table cursors, or text/blob cache objects. Trigger subprogram frames restore the parent VM's opcodes, registers, cursors, rowid/change counters, and auxdata.

`vdbeCommit()` is the main transaction commit helper. It syncs virtual tables, invokes commit hooks, detects multi-file write transactions, performs simple one-phase/two-phase btree commits when possible, and uses a super-journal for atomic multi-database rollback-journal commits when required. WAL, in-memory, temporary, OFF, and MEMORY journal modes bypass super-journal use.

`sqlite3VdbeHalt()` is the high-risk state machine that moves a VM from run state to halt state. It closes cursors, handles special errors (`NOMEM`, `IOERR`, `FULL`, `INTERRUPT`), rolls back statements or whole transactions as needed, checks immediate and deferred foreign keys, commits autocommit transactions when legal, updates change counters, releases btree locks, adjusts active VM counters, and triggers unlock-notify callbacks.

`sqlite3VdbeReset()`, `sqlite3VdbeFinalize()`, `sqlite3VdbeClearObject()`, and `sqlite3VdbeDelete()` reset or destroy VM state. They transfer VM errors to the database handle, invoke SQL log/profile hooks where enabled, release registers, variables, subprograms, column names, scanstatus data, normalized SQL state, opcode arrays, and unlink the VM from the connection list.

### Record Serialization and Comparison

The record-format section defines serial type lengths and deserialization helpers. `sqlite3SmallTypeSizes[]`, `sqlite3VdbeSerialTypeLen()`, `sqlite3VdbeOneByteSerialTypeLen()`, `serialGet()`, `serialGet7()`, and `sqlite3VdbeSerialGet()` decode SQLite record fields into `Mem` values. Integers are big-endian two's-complement encodings, serial type 7 is IEEE 754 double, serial types 8 and 9 are integer constants 0 and 1, and serial types >=12 encode blob/text lengths.

`sqlite3VdbeAllocUnpackedRecord()` and `sqlite3VdbeRecordUnpack()` allocate and populate `UnpackedRecord` objects used by btree comparisons. Corrupt records that overrun the key buffer are detected and sanitized to avoid using uninitialized memory.

Comparison helpers include `sqlite3MemCompare()`, `sqlite3BlobCompare()`, `sqlite3IntFloatCompare()`, `vdbeCompareMemString()`, `sqlite3VdbeRecordCompareWithSkip()`, `sqlite3VdbeRecordCompare()`, `vdbeRecordCompareInt()`, `vdbeRecordCompareString()`, and `sqlite3VdbeFindCompare()`. The optimized integer and binary-string comparators are selected only for safe header-size and key-shape cases; otherwise the generic comparator handles null, numeric, text collation, blob, sort-order, and big-null rules.

`sqlite3VdbeIdxRowid()` extracts the rowid stored at the end of an index record with corruption checks, and `sqlite3VdbeIdxKeyCompare()` compares an index cursor's key payload against an unpacked key.

### Public API Entry Points in This Chunk

The beginning of `vdbeapi.c` defines statement safety checks and public APIs:

- `sqlite3_expired()` reports whether a statement needs recompilation.
- `sqlite3_finalize()` resets and deletes a statement under the database mutex, then closes zombie connections if needed.
- `sqlite3_reset()` resets a statement, rewinds it for reuse, and returns the prior execution result.
- `sqlite3_clear_bindings()` releases all bound parameter values, sets them to NULL, and marks statements expired when binding-sensitive query planning is enabled.
- `sqlite3_value_blob()`, `sqlite3_value_bytes()`, `sqlite3_value_bytes16()`, `sqlite3_value_double()`, `sqlite3_value_int()`, `sqlite3_value_int64()`, `sqlite3_value_subtype()`, `sqlite3_value_pointer()`, `sqlite3_value_text()`, and UTF-16 variants expose `Mem` contents through the extension API.

The chunk ends before `sqlite3_value_type()` completes.

## Control Flow and State Behavior

The value-management control flow is mostly defensive and flag-driven. `Mem.flags` determines the active representations and ownership model. Functions often fast-path existing representations, then fall back to allocation, encoding conversion, blob expansion, or destructor invocation. On allocation failure, many helpers reset the value to NULL or propagate `SQLITE_NOMEM_BKPT`, and callers rely on `db->mallocFailed` to make subsequent operations safe.

VDBE construction flows from `sqlite3VdbeCreate()` through repeated opcode additions, label creation/resolution, P4 attachment, explain/comment/scanstatus metadata, and then `sqlite3VdbeMakeReady()`. After `MakeReady`, the VM leaves `VDBE_INIT_STATE`; opcode additions are no longer valid. `sqlite3VdbeRewind()` prepares a ready or halted VM for execution by resetting program counter, result code, change counters, cache counters, statement id, and foreign-key counters.

VDBE halt/reset/finalize flow is transaction-sensitive. `sqlite3VdbeHalt()` first closes execution resources, then decides whether to roll back a statement savepoint, roll back the whole transaction, commit an autocommit transaction, or leave surrounding transaction state open. It distinguishes ordinary constraint failures from special errors that may leave pager or journal state inconsistent. `sqlite3VdbeReset()` can call `sqlite3VdbeHalt()` if the VM is still running, transfers errors to the connection after any real execution, and leaves the VM reusable.

Persistent state affected by this range includes:

- `Mem` cell content, flags, encoding, subtype, destructor, aggregate context, rowset pointer, zero-blob tail, and owned allocation.
- Prepared statement fields such as opcode arrays, register arrays, cursor arrays, variable bindings, SQL text, explain state, scanstatus data, VM state, expiration masks, result-column names, auxdata, subprograms, and active-frame stacks.
- Connection state such as active VM counters, write/read VM counters, deferred foreign-key counters, change counters, error objects, commit hooks, virtual-table sync/commit state, auto-commit state, savepoint counts, and unlock-notify state.
- Btree/pager transaction state, including statement savepoints, phase-one/phase-two commit state, exclusive locks, rollback journals, and super-journals.

Record comparison is deliberately allocation-free in hot paths. Serialized record bytes are decoded only as far as needed, corruption checks guard buffer overreads, and optimized comparators avoid generic `Mem` comparison where the first field is an integer or binary-collated string with a small header.

## Dependencies and Integration Points

This code depends on core SQLite internals defined elsewhere in the amalgamation:

- `sqliteInt.h`, `vdbeInt.h`, and `opcodes.h` definitions for `sqlite3`, `Vdbe`, `VdbeOp`, `Mem`, `FuncDef`, `Parse`, `Btree`, `BtCursor`, `Pager`, `KeyInfo`, `UnpackedRecord`, `VdbeCursor`, `VdbeFrame`, `AuxData`, `PreUpdate`, opcodes, flags, limits, and mutex macros.
- Btree and pager APIs such as `sqlite3BtreePayload()`, `sqlite3BtreePayloadFetch()`, `sqlite3BtreeTxnState()`, `sqlite3BtreeCommitPhaseOne/Two()`, `sqlite3BtreeSavepoint()`, `sqlite3BtreeCloseCursor()`, and pager journal-mode/file-control helpers.
- Memory and string APIs including `sqlite3DbMalloc*`, `sqlite3DbFree*`, `sqlite3DbRealloc*`, `sqlite3VdbeMemTranslate()`, `sqlite3Atoi64()`, `sqlite3AtoF()`, `sqlite3Int64ToText()`, `sqlite3StrAccum*`, and encoding/BOM helpers.
- Function, collation, virtual-table, rowset, STAT4, pre-update hook, scanstatus, tracing, and normalize subsystems.
- OS and VFS APIs used by commit logic: file open/write/sync/delete, randomness, file suffixing, device characteristics, and current-time/profile calls.

External integration points are the public SQLite C APIs touched by this range (`sqlite3_backup_*`, `sqlite3_finalize`, `sqlite3_reset`, `sqlite3_clear_bindings`, `sqlite3_value_*`) and extension callbacks (`xFinalize`, `xValue`, scalar `xSFunc`, collation `xCmp`, virtual-table `xClose`/sync/commit, pre-update callback, commit hook, profile/trace callbacks).

For WiredTiger, the direct integration is via any tests or utilities that compile or execute this third-party SQLite amalgamation. Behavior changes here would affect embedded SQLite statement execution, extension compatibility, record comparisons, and transaction semantics within those tests rather than the WiredTiger data path itself.

## Risks

- `Mem` ownership flags are subtle. Incorrect transitions between `MEM_Dyn`, `MEM_Static`, `MEM_Ephem`, `zMalloc`, and `xDel` can cause leaks, double frees, stale pointers, or use-after-free in SQL functions and result accessors.
- Type conversion semantics are compatibility-sensitive. Integer/real/text/blob conversion, NaN handling, `MEM_IntReal`, zero-blob expansion, pointer subtypes, and UTF-16 termination all affect public SQLite API behavior and SQL comparison results.
- Destructor paths can re-enter extension code through aggregate finalizers, custom value destructors, virtual-table close methods, auxdata destructors, and pre-update callbacks. Resource cleanup order must remain stable.
- VDBE P4 payload ownership is type-specific. Mislabeling P4 types or changing `freeP4()` rules can leak `KeyInfo`, free static memory, drop virtual-table locks, or lose function contexts.
- Transaction halt logic is high blast radius. Errors in `sqlite3VdbeHalt()`, `vdbeCommit()`, or statement savepoint handling can corrupt rollback semantics, break autocommit behavior, lose change-counter updates, or mishandle foreign-key constraints.
- Super-journal handling is filesystem-sensitive. Name collisions, sync ordering, delete errors, and phase-one failures are carefully sequenced to preserve atomic multi-database commits.
- Record decoding and comparison are corruption-facing. Bounds checks around headers, serial types, rowid extraction, string/blob lengths, and optimized overread assumptions are essential for safe handling of malformed database pages.
- Debug-only invariants and coverage helpers mask many assumptions. Builds without `SQLITE_DEBUG`, STAT4, UTF16, virtual tables, pre-update hooks, or scanstatus compile different paths.
- This is an amalgamated third-party file. Local edits are hard to maintain unless they are test-only or mirrored from the upstream SQLite source used by this repository.

## Test and Validation Signals

Useful validation signals for this chunk include:

- SQLite API tests covering `sqlite3_finalize(NULL)`, reset after success/error, clearing bindings, statement expiration after parameter-sensitive planning, and `sqlite3_value_*()` conversions for NULL, integer, real, text, blob, zero-blob, pointer subtype, and UTF-16 text.
- VDBE memory tests that exercise transient/static/dynamic string destructors, aggregate finalization, window `xValue`, rowset cells, shallow/full copy behavior, blob expansion, out-of-memory injection, and API armor paths.
- SQL semantic tests for `CAST`, numeric affinity, integer/real comparison boundaries, NaN treatment, boolean conversion, UTF-8/UTF-16 conversion, and blob/text byte counts.
- STAT4 planner tests with literal expressions, bound variables during reprepare, vector probes, deterministic constant functions, corrupt stat records, and `sqlite3Stat4Column()` extraction.
- EXPLAIN, EXPLAIN QUERY PLAN, bytecode virtual table, scanstatus, trace/profile, and normalized-SQL tests to cover opcode display, comments, P4 rendering, subprogram iteration, and profiling callbacks.
- Transaction tests for autocommit writes, `OR FAIL`, immediate and deferred foreign keys, statement rollback vs release, nested savepoints, virtual-table commit/sync failures, commit hooks, lock contention, `SQLITE_BUSY`, `SQLITE_INTERRUPT`, `SQLITE_FULL`, `SQLITE_IOERR`, and OOM.
- Multi-database rollback-journal tests that force super-journal creation, sync failures, name collisions, phase-one failures, and cleanup of cold journals.
- Record-format tests for every serial type, corrupt record headers, truncated payloads, index rowid extraction, collated text comparison, zero-blob comparison, DESC and big-null sort flags, optimized integer/string record comparators, and fallback generic comparator behavior.
- Pre-update hook tests for rowid tables and WITHOUT ROWID tables, INSERT/UPDATE/DELETE operations, blob writes, default values, old/new unpacked records, and cleanup after callback invocation.

### subset-b-009024: lines 91726-99549

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 91726-99549

## Purpose

This chunk spans the end of SQLite's value API, most of `vdbeapi.c`, all of `vdbetrace.c`, and the opening portion of `vdbe.c` in the amalgamated SQLite source vendored under WiredTiger tests. It is the bridge between public `sqlite3_*` statement/function APIs and the VDBE interpreter that executes prepared-statement bytecode.

The code covers:

- `sqlite3_value_*`, `sqlite3_result_*`, `sqlite3_column_*`, and `sqlite3_bind_*` entry points backed by internal `Mem` cells.
- Top-level stepping/reprepare control around `sqlite3VdbeExec()`.
- User-defined-function support: context lookup, aggregate contexts, auxdata, result subtype/pointer handling, virtual-table `IN` iteration, and preupdate callbacks.
- Statement metadata/status APIs, expanded SQL trace rendering, and scan-status counters.
- The first interpreter opcodes for control flow, register movement, expression evaluation, record encoding/decoding, transaction/savepoint handling, cursor opening, and btree seeking.

## Important APIs, Types, and Functions

- `sqlite3_value_encoding()`, `sqlite3_value_nochange()`, `sqlite3_value_frombind()`, `sqlite3_value_dup()`, `sqlite3_value_free()` expose value metadata and safe duplication/freeing of `sqlite3_value`/`Mem` instances.
- `sqlite3_result_blob*()`, `sqlite3_result_text*()`, `sqlite3_result_int*()`, `sqlite3_result_double()`, `sqlite3_result_null()`, `sqlite3_result_value()`, `sqlite3_result_pointer()`, `sqlite3_result_subtype()`, `sqlite3_result_zeroblob*()`, `sqlite3_result_error*()` populate `sqlite3_context.pOut` for SQL functions and signal function-level errors.
- `sqlite3Step()` and `sqlite3_step()` drive VDBE execution, manage state transitions (`VDBE_READY_STATE`, `VDBE_RUN_STATE`, `VDBE_HALT_STATE`), auto-reset behavior, schema-change reprepare, tracing/profile callbacks, WAL callbacks, and API error masking.
- `sqlite3_user_data()`, `sqlite3_context_db_handle()`, `sqlite3_vtab_nochange()`, `sqlite3_aggregate_context()`, `sqlite3_get_auxdata()`, `sqlite3_set_auxdata()` provide function-context side channels and persistent per-aggregate/per-argument storage.
- `valueFromValueList()`, `sqlite3_vtab_in_first()`, and `sqlite3_vtab_in_next()` iterate a protected internal `ValueList` object for virtual-table `IN` RHS processing.
- `sqlite3_column_count()`, `sqlite3_data_count()`, `columnMem()`, `columnMallocFailure()`, `sqlite3_column_*()`, and `columnName()` expose result row values, names, decltypes, and optional metadata from the current `Vdbe`.
- `vdbeUnbind()`, `bindText()`, `sqlite3_bind_*()`, `sqlite3_bind_parameter_*()`, `sqlite3TransferBindings()`, and deprecated `sqlite3_transfer_bindings()` manage host parameters in `Vdbe.aVar`.
- Statement utility APIs include `sqlite3_db_handle()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, `sqlite3_next_stmt()`, `sqlite3_stmt_status()`, `sqlite3_sql()`, `sqlite3_expanded_sql()`, and optional `sqlite3_normalized_sql()`.
- Optional hooks/status APIs include `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, `sqlite3_preupdate_blobwrite()`, `sqlite3_stmt_scanstatus_v2()`, `sqlite3_stmt_scanstatus()`, and `sqlite3_stmt_scanstatus_reset()`.
- `sqlite3VdbeExpandSql()` tokenizes SQL and substitutes bound parameter renderings for trace output, respecting `SQLITE_TRACE_SIZE_LIMIT`.
- VDBE helpers in this chunk include `allocateCursor()`, `applyNumericAffinity()`, `applyAffinity()`, `sqlite3_value_numeric_type()`, `sqlite3ValueApplyAffinity()`, `numericType()`, `out2Prerelease()`, `filterHash()`, `vdbeColumnFromOverflow()`, and debug trace/coverage helpers.
- `sqlite3VdbeExec()` begins in this range and handles opcodes through `OP_IfNotOpen`; `OP_Found` starts at the chunk boundary and continues in the next chunk.

## Control Flow

`sqlite3_step()` validates the statement, enters the database mutex, then repeatedly calls `sqlite3Step()` while schema errors can be repaired by `sqlite3Reprepare()`. `sqlite3Step()` initializes a ready VM by clearing stale interrupts, bumping active/read/write VM counters, setting `pc=0`, optionally starting profile timers, then calls either `sqlite3VdbeList()` for explain output or `sqlite3VdbeExec()` for normal execution. `SQLITE_ROW` returns immediately with `pResultRow` set by `OP_ResultRow`; completion invokes profile callbacks and WAL callbacks for autocommit transactions. Errors may be transferred from the VDBE to the database handle when saved SQL is available.

`sqlite3VdbeExec()` is a large opcode dispatch loop. The portion in this chunk initializes interpreter-local state, checks progress callbacks/interrupts, maintains profiling counters, and then implements early opcodes:

- Control-transfer opcodes (`OP_Goto`, `OP_Gosub`, `OP_Return`, `OP_InitCoroutine`, `OP_EndCoroutine`, `OP_Yield`, `OP_Once`, `OP_If`, `OP_IfNot`, `OP_IsNull`, `OP_NotNull`, `OP_IfNullRow`, `OP_IfNotOpen`) mutate `pOp`/program counter and use `VdbeBranchTaken()` for coverage.
- Halt opcodes (`OP_HaltIfNull`, `OP_Halt`) set `p->rc`, build constraint/error messages, unwind subprogram frames, invoke `sqlite3VdbeHalt()`, and return `SQLITE_DONE`, `SQLITE_ERROR`, or `SQLITE_BUSY`.
- Register/value opcodes (`OP_Integer`, `OP_Int64`, `OP_Real`, `OP_String8`, `OP_String`, `OP_Null`, `OP_SoftNull`, `OP_Blob`, `OP_Variable`, `OP_Move`, `OP_Copy`, `OP_SCopy`, `OP_IntCopy`) update `Mem` flags, ownership, and shallow-copy invariants.
- Expression opcodes (`OP_Concat`, arithmetic ops, bit ops, `OP_AddImm`, `OP_MustBeInt`, `OP_RealAffinity`, `OP_Cast`, comparisons, `OP_And`, `OP_Or`, `OP_IsTrue`, `OP_Not`, `OP_BitNot`) enforce SQLite's dynamic typing, NULL propagation, affinity rules, and collation-aware comparison behavior.
- Row-format opcodes (`OP_Column`, `OP_TypeCheck`, `OP_Affinity`, `OP_MakeRecord`) decode and encode SQLite record format, apply strict table type checks, and update register/cache state.
- Transaction and cursor opcodes (`OP_Count`, `OP_Savepoint`, `OP_AutoCommit`, `OP_Transaction`, `OP_ReadCookie`, `OP_SetCookie`, `OP_OpenRead`, `OP_ReopenIdx`, `OP_OpenWrite`, `OP_OpenDup`, `OP_OpenEphemeral`, `OP_OpenAutoindex`, `OP_SorterOpen`, `OP_SequenceTest`, `OP_OpenPseudo`, `OP_Close`, optional `OP_ColumnsUsed`, seek opcodes, `OP_SeekScan`, `OP_SeekHit`) interact with btrees, pagers, schemas, savepoint lists, transient btrees, sorter state, and cursor caches.

## State and Persistence Behavior

The dominant mutable state is `Mem` cell state: flags (`MEM_Null`, `MEM_Int`, `MEM_Real`, `MEM_Str`, `MEM_Blob`, `MEM_Zero`, `MEM_Ephem`, `MEM_Static`, `MEM_Dyn`, `MEM_IntReal`, `MEM_Subtype`, `MEM_FromBind`), text encoding, destructor ownership, subtype, cached integer/real values, and buffer allocation. Result, column, bind, and opcode paths all depend on preserving these flags exactly to avoid leaks, dangling shallow copies, wrong affinity, or incorrect public API types.

`Vdbe` state includes execution state, program counter, statement return code, saved SQL, result row pointer, active frame stack, registers, host parameters, cursors, auxdata, scan counters, profiling counters, current time cache, expired/reprepare flags, and statement-journal bookkeeping. `sqlite3_step()` and opcodes update database connection counters (`nVdbeActive`, `nVdbeWrite`, `nVdbeRead`, `nVdbeExec`), error codes, interrupt state, schema flags, deferred-constraint counts, savepoint lists, and autocommit state.

Persistent database behavior appears in btree/pager-facing opcodes:

- `OP_Transaction` starts read/write/exclusive btree transactions, opens statement transactions when rollback granularity is needed, checks schema cookies/generation, and can expire statements on schema mismatch.
- `OP_Savepoint` creates, releases, or rolls back savepoints across all attached btrees and virtual tables, restoring deferred-constraint counters on rollback.
- `OP_AutoCommit` commits or rolls back the current transaction and halts the VM.
- `OP_SetCookie` writes database header metadata, updates in-memory schema cookie/file-format state, clears FK trigger cache, and expires TEMP-schema statements.
- `OP_OpenRead`/`OP_OpenWrite` open persistent btree cursors; `OP_OpenEphemeral`/`OP_OpenAutoindex`/`OP_SorterOpen` create transient btrees/sorters with delete-on-close or sorter-managed storage.
- `OP_Column` lazily reads record payloads from btree pages and overflow pages. Large overflow text/blob values may be cached in a cursor-local `VdbeTxtBlbCache` using reference-counted strings.

## Dependencies and Integration Points

This code depends heavily on internal SQLite subsystems:

- VDBE memory helpers: `sqlite3VdbeMemSetStr()`, `sqlite3VdbeMemSetInt64()`, `sqlite3VdbeMemSetDouble()`, `sqlite3VdbeMemCopy()`, `sqlite3VdbeMemMove()`, `sqlite3VdbeMemShallowCopy()`, `sqlite3VdbeMemMakeWriteable()`, `sqlite3VdbeMemGrow()`, `sqlite3VdbeMemClearAndResize()`, `sqlite3VdbeMemRelease()`, `ExpandBlob()`, and serial-type helpers.
- Btree/pager APIs: `sqlite3BtreeBeginTrans()`, `sqlite3BtreeBeginStmt()`, `sqlite3BtreeCursor()`, `sqlite3BtreePayload*()`, `sqlite3BtreePayloadFetch()`, `sqlite3BtreeTableMoveto()`, `sqlite3BtreeIndexMoveto()`, `sqlite3BtreeNext()`, `sqlite3BtreePrevious()`, `sqlite3BtreeSavepoint()`, `sqlite3BtreeUpdateMeta()`, `sqlite3PagerWalCallback()`.
- Schema/parser/query-plan objects: `Table`, `Column`, `KeyInfo`, `CollSeq`, `UnpackedRecord`, `VList`, schema cookies, column metadata, and explain metadata.
- Connection-level features: mutexes, lookaside accounting, error APIs, VFS current-time calls, WAL hooks, trace/profile callbacks, preupdate/update hooks, virtual-table savepoint hooks, and optional scanstatus/normalize/UTF16/test/debug builds.
- Public API contracts: many comments are tagged `IMPLEMENTATION-OF` or `EVIDENCE-OF`, indicating that SQLite's Tcl/TH3-style test suites likely verify exact behavior.

For WiredTiger, this vendored file is not part of WiredTiger's storage engine implementation; it is a bundled SQLite amalgamation under test third-party sources. Integration risk is mostly in keeping the vendored SQLite behavior intact for tests or tools that build against this copy.

## Risks and Edge Cases

- Memory ownership is subtle. `SQLITE_STATIC`, `SQLITE_TRANSIENT`, custom destructors, `MEM_Ephem`, `MEM_Static`, `MEM_Dyn`, RCStr caches, and shallow `OP_SCopy` all have different lifetimes. Incorrect flag transitions can cause leaks, double frees, or use-after-free.
- Mutex discipline matters. Public APIs often assert the database mutex is held; column APIs enter it via `columnMem()` and must release through `columnMallocFailure()`.
- `sqlite3_bind_zeroblob64()` enters the DB mutex and then calls `sqlite3_bind_zeroblob()`, which uses `vdbeUnbind()` and also enters/leaves the mutex. SQLite mutexes are recursive in normal builds, but this pattern is sensitive to mutex configuration.
- `sqlite3_stmt_status(SQLITE_STMTSTATUS_MEMUSED)` computes memory by temporarily arranging for `sqlite3VdbeDelete()` to count freed bytes. Misuse after finalization or against an invalid statement is guarded only by API armor/build assumptions.
- `OP_Column` tolerates some historically accepted corrupt record shapes, but still performs explicit header-length/payload-size checks. The parser intentionally avoids loading overflow payload for `typeof()` and some `length()` cases; changes here can alter I/O and corruption behavior.
- Numeric conversion and comparison preserve or temporarily restore flags in several places. Affinity can persist in registers for some opcodes but is undone for comparison inputs after `applyAffinity()`. This distinction is observable through later opcode behavior.
- `OP_MakeRecord` encodes virtual-table no-change values with internal serial type 10 and trims trailing NULLs only under compile-time conditions. This affects `sqlite3_value_nochange()` and virtual-table `xUpdate`.
- Transaction/savepoint opcodes are tightly coupled to active VM counts, statement journals, virtual table callbacks, schema invalidation, and deferred FK counters. Early returns on `SQLITE_BUSY` preserve `pc` for retry.
- Optional compilation flags (`SQLITE_OMIT_UTF16`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_OMIT_TRACE`, `SQLITE_ENABLE_NULL_TRIM`, debug/test flags) significantly alter available APIs and control paths.
- The assigned chunk ends at the opening comment for `OP_Found`; its implementation is unresolved in this chunk and belongs to the following source slice.

## Test Signals

Important test signals visible in this range include:

- Debug assertions for `Mem` type masks, shallow-copy validity, cursor types, opcode adjacency, savepoint counts, schema mutex ownership, and valid program-counter targets.
- `testcase()` calls around boundary values: varint/header sizes, integer packing thresholds, affinity conversions, schema-cookie outcomes, busy result variants, and opcode flag combinations.
- `VdbeBranchTaken()` and optional `SQLITE_VDBE_COVERAGE` instrumentation for branch coverage of comparisons, jumps, NULL behavior, seek/seekscan outcomes, and control-flow opcodes.
- `SQLITE_TEST` counters such as `sqlite3_search_count`, `sqlite3_interrupt_count`, `sqlite3_sort_count`, `sqlite3_max_blobsize`, and `sqlite3_found_count`.
- Trace/profile hooks: `SQLITE_TRACE_ROW`, profile callbacks, expanded SQL output, and VDBE register dump helpers under debug builds.
- API armor paths returning `SQLITE_MISUSE_BKPT`, `SQLITE_RANGE`, `SQLITE_TOOBIG`, or NULL instead of asserting on invalid public API inputs.
- Error propagation tests should exercise OOM in string conversion, too-large blob/text paths, schema-change reprepare, WAL callback failures after autocommit, preupdate default-value loading, strict type-check failures, savepoint rollback/release edge cases, and btree seek behavior for integer/real/string/NULL keys.

### subset-b-009025: lines 99550-107363

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 99550-107363

## Scope

This chunk starts in the late body of SQLite's VDBE execution loop, continues through the full incremental BLOB implementation in `vdbeblob.c`, then covers most of `vdbesort.c` and the optional bytecode/tables-used virtual table in `vdbevtab.c`. It ends just after the `memjournal.c` file header and forward type declarations, before the in-memory journal implementation begins.

The VDBE opcode section in this chunk handles btree lookup, rowid allocation, row insert/delete, sorter iteration, schema mutation, integrity checks, rowsets, trigger subprograms, foreign-key counters, aggregate/window function dispatch, WAL/journal/vacuum opcodes, virtual table opcodes, function invocation, bloom filters, tracing, and the final VDBE error/return paths.

## Purpose

The VDBE portion is the execution engine's storage-facing and callback-heavy tail. It bridges bytecode opcodes to the btree, pager, schema, virtual table, function, trigger, rowset, and statement-status subsystems while preserving cursor state and translating low-level return codes into VDBE statement outcomes.

The incremental BLOB portion exposes `sqlite3_blob_*()` API support. It opens a row/column blob through a small generated VDBE program, borrows the resulting btree cursor, and performs range-checked payload reads/writes without rewriting the whole row.

The sorter portion implements SQLite's external merge sorter for `ORDER BY`, `CREATE INDEX`, and uniqueness checks. It starts with in-memory record accumulation, spills sorted Packed Memory Arrays (PMAs) to temporary files when needed, and builds single-threaded or worker-threaded merge trees for sorted iteration.

The bytecode virtual table portion exposes `bytecode()` and `tables_used()` table-valued modules, allowing SQL-level inspection of a prepared statement's opcodes or table/index accesses when `SQLITE_ENABLE_BYTECODE_VTAB` is enabled.

## Important APIs, Types, and Functions

- VDBE opcode cases:
  - `OP_IfNoHope`, `OP_Found`, `OP_NotFound`, `OP_NoConflict`: index key probes using `sqlite3BtreeIndexMoveto()` and cursor `seekHit`/`seekResult` state.
  - `OP_SeekRowid`, `OP_NotExists`, `OP_Rowid`, `OP_RowData`, `OP_IdxRowid`, `OP_DeferredSeek`, `OP_FinishSeek`: rowid and cursor-positioning operations over table/index cursors.
  - `OP_NewRowid`, `OP_Insert`, `OP_RowCell`, `OP_Delete`, `OP_IdxInsert`, `OP_IdxDelete`: table/index mutation paths, update/preupdate hooks, change counters, and cursor cache invalidation.
  - `OP_SorterSort`, `OP_Rewind`, `OP_Next`, `OP_Prev`, `OP_SorterNext`, `OP_SorterData`, `OP_SorterCompare`: sorter and btree scan control.
  - `OP_Destroy`, `OP_Clear`, `OP_CreateBtree`, `OP_ParseSchema`, `OP_LoadAnalysis`, `OP_DropTable`, `OP_DropIndex`, `OP_DropTrigger`: schema and btree object lifecycle.
  - `OP_IntegrityCk`, `OP_Checkpoint`, `OP_JournalMode`, `OP_Vacuum`, `OP_IncrVacuum`, `OP_Pagecount`, `OP_MaxPgcnt`: database maintenance and pragma support.
  - `OP_Program`, `OP_Param`, `OP_AggStep`, `OP_AggInverse`, `OP_AggFinal`, `OP_AggValue`, `OP_Function`, `OP_PureFunc`: trigger frames, aggregate/window contexts, and scalar function callbacks.
  - `OP_VBegin`, `OP_VCreate`, `OP_VDestroy`, `OP_VOpen`, `OP_VFilter`, `OP_VColumn`, `OP_VNext`, `OP_VRename`, `OP_VUpdate`, `OP_VCheck`, `OP_VInitIn`: virtual table integration.
  - `OP_FilterAdd`, `OP_Filter`, `OP_Init`, `OP_Trace`, debug-only `OP_Abortable` and `OP_ReleaseReg`: optimizer bloom filters, tracing, and validation aids.
- `Incrblob`: private handle behind public `sqlite3_blob*`, storing blob size, payload offset, target column, borrowed `BtCursor`, owning statement, database handle, database name, and table metadata.
- `blobSeekToRow()`: binds the target rowid into the generated statement, seeks the cursor, verifies the selected column is TEXT/BLOB, caches payload offset/length, and invalidates the handle on error.
- Public incremental blob API: `sqlite3_blob_open()`, `sqlite3_blob_close()`, `sqlite3_blob_read()`, `sqlite3_blob_write()`, `sqlite3_blob_bytes()`, `sqlite3_blob_reopen()`.
- Sorter core types: `VdbeSorter`, `SortSubtask`, `SorterList`, `SorterRecord`, `SorterFile`, `PmaReader`, `PmaWriter`, `MergeEngine`, and `IncrMerger`.
- Sorter APIs exported to VDBE: `sqlite3VdbeSorterInit()`, `sqlite3VdbeSorterWrite()`, `sqlite3VdbeSorterRewind()`, `sqlite3VdbeSorterNext()`, `sqlite3VdbeSorterRowkey()`, `sqlite3VdbeSorterCompare()`, `sqlite3VdbeSorterReset()`, and `sqlite3VdbeSorterClose()`.
- Sorter internal helpers include `vdbePmaReadBlob()`, `vdbePmaReadVarint()`, `vdbePmaReaderInit()`, `vdbeSorterSort()`, `vdbeSorterListToPMA()`, `vdbeSorterFlushPMA()`, `vdbeMergeEngineStep()`, `vdbeSorterMergeTreeBuild()`, and `vdbeSorterSetupMerge()`.
- Bytecode virtual table types and methods: `bytecodevtab`, `bytecodevtab_cursor`, `bytecodevtabConnect()`, `bytecodevtabBestIndex()`, `bytecodevtabFilter()`, `bytecodevtabNext()`, `bytecodevtabColumn()`, and `sqlite3VdbeBytecodeVtabInit()`.

## Control Flow

The VDBE opcode switch uses direct fallthrough to share work between related opcodes. `OP_IfNoHope` falls into `OP_NotFound` when `seekHit` cannot prove a prefix match is possible. `OP_SeekRowid` converts compatible non-integer values before falling into `OP_NotExists`. `OP_SorterSort` and `OP_Sort` increment sort counters before falling into `OP_Rewind`.

Cursor-moving opcodes update `nullRow`, `deferredMoveto`, `cacheStatus`, `seekResult`, and debug `seekOp` fields before branching. Scans use `jump_to_p2`, `jump_to_p2_and_check_for_interrupt`, or `check_for_interrupt` to centralize control transfer and progress interruption checks.

Mutation opcodes increment write counters with `sqlite3VdbeIncrWriteCounter()`, call btree operations, invalidate column caches with `CACHE_STALE` and `colCacheCtr`, and invoke hooks only after the underlying btree operation succeeds. `OP_Delete` also supports pre-update-only no-op deletes used before overwriting a row.

Schema opcodes route through btree and schema helpers. `OP_Destroy` prevents unsafe root-page movement while other reader VMs are active and records moved root pages for schema reset. `OP_ParseSchema` reparses schema entries by running SQL reentrantly through `sqlite3_exec()` under initialization state.

Trigger execution via `OP_Program` allocates or reuses a `VdbeFrame`, saves the parent register/cursor/opcode state, swaps in the subprogram's memory and cursor arrays, clears `Once` bits, and restarts the execution loop at the subprogram. `OP_Param` reads parent-frame registers for `old.*` and `new.*` values.

Incremental blob open validates the target table and column, rejects virtual tables, views, WITHOUT ROWID tables, generated-column tables, and unsafe writable columns, then emits a short VDBE program with transaction, table lock, open cursor, row seek, column decode, result row, and halt. `blobSeekToRow()` runs or rewinds that statement to position the cursor. Read/write calls enter the cursor mutex, perform a bounded payload operation at `iOffset + p->iOffset`, and finalize the statement if the cursor is aborted.

Sorter write flow begins in memory. `sqlite3VdbeSorterWrite()` records the serialized key, tracks first-field type for optimized comparisons, grows either a bulk allocation or separate records, and flushes to a PMA when memory thresholds or heap pressure dictate. PMA flushing sorts the list, writes a PMA length varint, then writes each key as length varint plus blob to a temp file.

Sorter rewind either sorts the in-memory list directly or flushes the final list, joins worker threads, and constructs a merge tree. Single-threaded sorters use `VdbeSorter.pMerger`. Threaded sorters use `VdbeSorter.pReader` backed by `IncrMerger` objects that prepopulate alternating temp files so the main VDBE thread can read one segment while workers prepare the next.

Bytecode virtual table filtering requires a hidden `stmt` argument, either SQL text that is prepared and owned by the cursor or a `"stmt-pointer"` value borrowed from the caller. `bytecodevtabNext()` advances through main opcodes and optional subprograms using `sqlite3VdbeNextOpcode()`. `bytecodevtabColumn()` renders opcode fields, P4 display text, explain comments, scan-status counters, subprogram names, or table/index usage metadata depending on module mode.

## State and Persistence Behavior

The VDBE section mutates both in-memory execution state and database state. Persistent database effects include row/table/index inserts and deletes, btree creation/destruction/clearing, schema reparsing side effects, journal-mode transitions, checkpoints, vacuum operations, page-count changes, and virtual table `xCreate`/`xDestroy`/`xUpdate`/`xRename` effects.

Cursor state is central. Many opcodes deliberately mark cursor caches stale, maintain `movetoTarget` for deletes and deferred seeks, use `seekResult` as an optimization hint, and set `nullRow` when scans exhaust. Incorrect maintenance of those fields would surface later as wrong `OP_Column`, `OP_Rowid`, `OP_Next`, or update-hook behavior.

Incremental blob handles persist a prepared statement and borrowed btree cursor for the lifetime of the blob handle. The blob length is fixed in `Incrblob.nByte`; writes cannot resize the value. On seek/read/write failures that invalidate the cursor, `pStmt` is finalized and later blob API calls return `SQLITE_ABORT` except close. `sqlite3_blob_close()` finalizes the statement, which may commit or roll back statement/transaction state according to normal VDBE behavior.

Sorter state is transient but may use temporary files. `VdbeSorter.list` owns in-memory records until flushed or consumed. Each `SortSubtask` owns temp files and per-thread unpacked record state. `PmaReader` key pointers may point into an mmap, read buffer, or owned allocation and are only stable until the next read. `sqlite3VdbeSorterReset()` joins workers, frees readers/mergers/temp files/records, and returns the sorter to an empty state; close additionally frees the sorter and its bulk memory.

Bytecode virtual table state is cursor-local. It may own a prepared statement when SQL text was supplied, and it owns rendered P4 strings and a `Mem` object used to enumerate subprograms. It does not persist database content; `tables_used()` reads schema hashes to label root pages as tables or indexes.

## Dependencies and Integration Points

This chunk is tightly integrated with SQLite's btree, pager, VDBE memory, schema, parser, virtual table, function, rowset, WAL, and VFS layers. Important dependencies include `sqlite3Btree*` cursor/table/index APIs, `sqlite3Pager*` journal/WAL APIs, `sqlite3VdbeMem*` register helpers, `sqlite3VdbeRecordCompare*`, `sqlite3_exec()`, `sqlite3InitCallback()`, `sqlite3Vtab*`, `sqlite3Thread*`, `sqlite3Os*`, and fault-simulation hooks.

Compile-time options change major behavior: `SQLITE_OMIT_INCRBLOB`, `SQLITE_MAX_WORKER_THREADS`, `SQLITE_MAX_MMAP_SIZE`, `SQLITE_OMIT_AUTOINCREMENT`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_WAL`, `SQLITE_OMIT_PRAGMA`, `SQLITE_OMIT_VACUUM`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_ENABLE_BYTECODE_VTAB`, `SQLITE_ENABLE_STMT_SCANSTATUS`, and debug/test macros all include, exclude, or instrument pieces of this range.

In the WiredTiger repository context, this is vendored SQLite test/support code under `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3`. It is not WiredTiger's own storage engine implementation, but it can affect test binaries or tooling that embed this SQLite amalgamation.

## Risks and Edge Cases

- VDBE opcode fallthrough is intentional and fragile. Adding a `break`, changing opcode ordering, or altering assertions around shared cases can change semantics.
- Cursor state bugs are high risk because later opcodes rely on `nullRow`, `deferredMoveto`, `movetoTarget`, `seekResult`, `seekHit`, and cache invalidation rather than always re-seeking.
- `OP_NewRowid` has separate sequential, random, and AUTOINCREMENT paths. Boundary handling at `MAX_ROWID`, 100 random attempts, and root-frame autoincrement registers can produce `SQLITE_FULL`.
- Hook behavior is subtle. Insert/delete/preupdate hooks are conditional on table metadata, no-op flags, update flags, rowid availability, and compile-time features. The incremental blob write path intentionally reports a preupdate delete-like event for session-module convenience.
- `OP_JournalMode` must reject WAL transitions inside transactions or with active readers and must handle temporary files, VFS shared-memory support, and MEMORY-to-WAL transitions carefully.
- `OP_ParseSchema` runs SQL reentrantly while initialization flags are set; error paths reset schema state and need to preserve malloc failure handling.
- Incremental blob writes reject indexed/FK child columns but conservatively reject expression indexes too. Generated-column tables are entirely rejected. `blobSeekToRow()` invalidates the handle on type mismatch or missing row.
- `blobReadWrite()` range checks `n`, `iOffset`, and `iOffset+n` against the fixed blob size; integer overflow is avoided by casting the sum to `sqlite3_int64`.
- Sorter code mixes bulk-memory offsets, linked pointers, mmap pointers, temp-file buffers, and worker-owned task state. Ownership bugs can cause use-after-free, double-free, leaked temp files, or stale pointer comparisons.
- PMA format depends on exact varint sizes and file offsets. Corrupt offsets or size accounting would cascade into bad reads during merge-tree construction.
- Threaded sorter paths rely on `bDone`, `pThread`, task assignment, and join ordering. There are comments noting intentionally weak synchronization for `bDone`; correctness relies on always joining before consuming worker results.
- Optimized integer/text comparators assume specific record encoding and only activate under constrained `KeyInfo` conditions. Any change to record layout, collation assumptions, or sort flags would need careful validation.
- Bytecode virtual table accepts raw statement pointers via `sqlite3_value_pointer()`. It must not finalize borrowed statements, and callers must ensure pointer lifetime and connection compatibility.
- The final `memjournal.c` lines in this chunk are only introductory comments and type forward declarations; behavior for the in-memory rollback journal begins in a later chunk.

## Test Signals

Useful tests for this chunk include:

- VDBE lookup tests for `Found`, `NotFound`, `NoConflict`, `IfNoHope`, rowid seeks, and `IdxGE`/`IdxGT`/`IdxLT`/`IdxLE`, including NULL key fields and multi-column IN optimizations.
- Rowid allocation tests at empty table, normal append, explicit AUTOINCREMENT high-water mark, `MAX_ROWID`, and random-rowid exhaustion boundaries.
- Insert/delete/update-hook and preupdate-hook tests covering normal rowid tables, no-op delete-before-insert, auxiliary index deletes, and change counter behavior.
- Sorter tests for all-memory sorting, PMA spill, multi-PMA merge, unique-index duplicate detection through `OP_SorterCompare`, stable CREATE INDEX sorting in single-threaded mode, and worker-threaded sorting when `PRAGMA threads` is enabled.
- Fault injection for sorter temp-file open/read/write, mmap fetch, PMA reader allocation, merge-engine allocation, and background thread return codes.
- Incremental blob tests for read-only and read/write handles, reopen to another row, out-of-range reads/writes, missing rowid, NULL/integer/real column rejection, indexed/FK/generated/WITHOUT ROWID/virtual/view table rejection, and invalidation after abort.
- Schema and maintenance tests for `DROP`, `CREATE`, `VACUUM`, `incremental_vacuum`, `integrity_check`, WAL checkpoints, and journal-mode transitions inside and outside transactions.
- Virtual table opcode tests for `xOpen`, `xFilter`, `xColumn`, `xNext`, `xUpdate`, constraint handling, `xIntegrity`, and error-message import from modules.
- Bytecode virtual table tests with SQL text and `stmt-pointer` inputs, hidden `stmt` constraint enforcement, subprogram inclusion/exclusion, scan-status columns with and without `SQLITE_ENABLE_STMT_SCANSTATUS`, and `tables_used()` root-page labeling.

### subset-b-009026: lines 107364-114787

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 107364-114787

Chunk id: `subset-b-009026`

## Purpose

This chunk covers four adjacent SQLite amalgamation modules:

- The tail of `memjournal.c`, implementing SQLite's rollback journal handle that can start in memory and optionally spill to the real VFS.
- `walker.c`, the generic parse-tree walker for expressions, SELECT statements, FROM-subqueries, and window definitions.
- `resolve.c`, the name resolver that turns SQL identifiers into resolved column/register/trigger/UPSERT references and validates aggregate, window, function, ORDER BY, GROUP BY, and self-reference rules.
- The beginning of `expr.c`, expression metadata, allocation, duplication, deletion, constant analysis, vector/subquery/IN handling, and early VDBE code generation helpers.

Within WiredTiger this is vendored SQLite test code, but the chunk is core SQLite compiler/runtime support. It bridges parsed SQL ASTs into semantically resolved expression trees and early VDBE bytecode.

## Important APIs, Types, and Functions

### Memory journal

- `FileChunk`, `FilePoint`, and `MemJournal` implement a `sqlite3_file` subclass backed by a linked list of fixed-size heap chunks until spill.
- `sqlite3JournalOpen()` initializes a journal handle. `nSpill==0` opens the real VFS immediately, `nSpill<0` keeps all content in memory, and `nSpill>0` buffers until the threshold or explicit creation.
- `sqlite3MemJournalOpen()` opens a permanent in-memory journal.
- `sqlite3JournalCreate()` forces a memory-backed journal onto disk for atomic or batch-atomic write paths when enabled.
- `sqlite3JournalIsInMemory()` and `sqlite3JournalSize()` expose journal storage mode and required handle size.
- Internal methods `memjrnlRead()`, `memjrnlWrite()`, `memjrnlTruncate()`, `memjrnlCreateFile()`, `memjrnlClose()`, and `memjrnlFileSize()` populate `MemJournalMethods`.

### Tree walking

- `sqlite3WalkExprNN()`, `sqlite3WalkExpr()`, and `sqlite3WalkExprList()` traverse expression trees/lists using `Walker.xExprCallback`, pruning or aborting according to `WRC_*` return values.
- `sqlite3WalkSelectExpr()`, `sqlite3WalkSelectFrom()`, and `sqlite3WalkSelect()` traverse SELECT result/WHERE/GROUP/HAVING/ORDER/LIMIT expressions, FROM-clause subqueries/table-valued function args, compound SELECT chains, and optional post callbacks.
- `walkWindowList()` and `sqlite3WalkWinDefnDummyCallback()` support window-function expression traversal when window functions are compiled in.
- `sqlite3WalkerDepthIncrease()` / `sqlite3WalkerDepthDecrease()` adjust `Walker.walkerDepth`; `sqlite3ExprWalkNoop()` and `sqlite3SelectWalkNoop()` are reusable no-op callbacks.

### Name resolution

- `lookupName()` is the central identifier resolver for `Z`, `Y.Z`, and `X.Y.Z`. It searches nested `NameContext` scopes, FROM terms, nested-from result columns, rowid aliases, triggers, UPSERT `excluded`, RETURNING rows, and SELECT aliases.
- `resolveExprStep()` is the expression-walker callback that handles identifier resolution, function lookup/validation, aggregate/window classification, subquery correlation marking, parameter restrictions, truth tests, vector-size checks, and NOT NULL strength reduction in WHERE clauses.
- `resolveSelectStep()` resolves expanded SELECT trees, including LIMIT, FROM subqueries, result expressions, HAVING/WHERE, table-valued function arguments, ORDER BY, GROUP BY, compounds, aggregate flags, and correlated-subquery state.
- `sqlite3ResolveExprNames()`, `sqlite3ResolveExprListNames()`, `sqlite3ResolveSelectNames()`, and `sqlite3ResolveSelfReference()` are the public resolver entry points used by parser/codegen paths.
- Helpers include `resolveAlias()`, `sqlite3MatchEName()`, `sqlite3ExprColUsed()`, `extendFJMatch()`, `isValidSchemaTableName()`, `resolveAsName()`, `resolveOrderByTermToExprList()`, `resolveCompoundOrderBy()`, `sqlite3ResolveOrderGroupBy()`, and `resolveOrderGroupBy()`.

### Expression analysis, allocation, copying, and deletion

- Affinity/collation APIs: `sqlite3TableColumnAffinity()`, `sqlite3ExprAffinity()`, `sqlite3ExprDataType()`, `sqlite3ExprAddCollateToken()`, `sqlite3ExprAddCollateString()`, `sqlite3ExprSkipCollate()`, `sqlite3ExprSkipCollateAndLikely()`, `sqlite3ExprCollSeq()`, `sqlite3ExprNNCollSeq()`, `sqlite3ExprCollSeqMatch()`, `sqlite3CompareAffinity()`, `sqlite3IndexAffinityOk()`, `sqlite3BinaryCompareCollSeq()`, and `sqlite3ExprCompareCollSeq()`.
- Vector and comparison helpers: `sqlite3ExprVectorSize()`, `sqlite3ExprIsVector()`, `sqlite3VectorFieldSubexpr()`, `sqlite3ExprForVectorField()`, `exprVectorRegister()`, `codeVectorCompare()`, and `codeCompare()`.
- Allocation/build APIs: `sqlite3ExprAlloc()`, `sqlite3Expr()`, `sqlite3ExprAttachSubtrees()`, `sqlite3PExpr()`, `sqlite3PExprAddSelect()`, `sqlite3ExprListToValues()`, `sqlite3ExprAnd()`, `sqlite3ExprFunction()`, `sqlite3ExprAddFunctionOrderBy()`, and `sqlite3ExprAssignVarNumber()`.
- Destruction/copy APIs: `sqlite3ExprDelete()`, `sqlite3ExprDeleteGeneric()`, `sqlite3ClearOnOrUsing()`, `sqlite3ExprDeferredDelete()`, `sqlite3ExprUnmapAndDelete()`, `sqlite3ExprDup()`, `sqlite3ExprListDup()`, `sqlite3SrcListDup()`, `sqlite3IdListDup()`, `sqlite3SelectDup()`, and `sqlite3WithDup()`.
- Expression-list APIs: `sqlite3ExprListAppend*()`, `sqlite3ExprListAppendVector()`, `sqlite3ExprListSetSortOrder()`, `sqlite3ExprListSetName()`, `sqlite3ExprListSetSpan()`, `sqlite3ExprListCheckLength()`, `sqlite3ExprListDelete()`, and `sqlite3ExprListFlags()`.
- Constant/nullability APIs: `sqlite3IsTrueOrFalse()`, `sqlite3ExprIdToTrueFalse()`, `sqlite3ExprTruthValue()`, `sqlite3ExprSimplifiedAndOr()`, `sqlite3ExprIsConstant()`, `sqlite3ExprIsConstantOrFunction()`, `sqlite3ExprIsConstantOrGroupBy()`, `sqlite3ExprContainsSubquery()`, `sqlite3ExprIsInteger()`, `sqlite3ExprCanBeNull()`, `sqlite3ExprNeedsNoAffinityChange()`, `sqlite3ExprIsSingleTableConstraint()`, `sqlite3IsRowid()`, and `sqlite3RowidAlias()`.

### IN/subquery and early codegen helpers

- `sqlite3FindInIndex()` chooses the RHS storage strategy for `IN`: direct rowid lookup, existing index, ephemeral b-tree, or comparison sequence (`IN_INDEX_NOOP`).
- `sqlite3CodeRhsOfIN()` materializes or reuses the RHS of `IN`, using `OP_BeginSubrtn`, `OP_Once`, `OP_OpenEphemeral`, `OP_OpenDup`, and optional Bloom filter wiring.
- `sqlite3ExprCodeIN()` emits the optimized seven-step IN-operator membership algorithm, including LHS vector coding, RHS probing, NULL handling, and fallbacks.
- `sqlite3CodeSubselect()` emits scalar subquery/EXISTS subroutines with implicit `LIMIT 1` and result-register initialization.
- `sqlite3ExprCheckIN()`, `sqlite3SubselectError()`, and `sqlite3VectorErrorMsg()` validate vector/subquery arity.
- `codeReal()`, `codeInteger()`, `sqlite3ExprCodeLoadIndexColumn()`, `sqlite3ExprCodeGeneratedColumn()`, `sqlite3ExprCodeGetColumnOfTable()`, `sqlite3ExprCodeGetColumn()`, `sqlite3ExprCodeMove()`, `sqlite3ExprToRegister()`, `exprCodeVector()`, and `setDoNotMergeFlagOnCopy()` start the general expression-to-VDBE codegen section.

## Control Flow

The memory journal code first attempts to satisfy reads and writes from `FileChunk` linked-list storage. Writes append to `endpoint`; a non-append write truncates back to the write offset except for the special atomic-write header rewrite at offset zero. If a write crosses `nSpill`, `memjrnlCreateFile()` opens the real VFS journal, writes all chunks in order, frees memory only after all writes succeed, and restores the copied in-memory state on error.

The walker layer provides the generic traversal engine used by later modules. `sqlite3WalkExprNN()` invokes the expression callback pre-order, then recurses into left/right children, subselects, expression lists, or window definitions. `sqlite3WalkSelect()` invokes the SELECT callback, walks expressions/FROM sources, invokes the optional post callback, and follows compound chains through `pPrior`.

Name resolution is a layered pass over already-expanded SELECT trees. `sqlite3ResolveSelectNames()` configures a `Walker` with `resolveExprStep()` and `resolveSelectStep()`. For each SELECT, the resolver handles subqueries first so correlation can be detected via `NameContext.nRef`. It then resolves result-set expressions, records aggregate/window flags, adds result aliases to the local `NameContext`, resolves HAVING/WHERE/table-valued function arguments/window definitions, and resolves ORDER BY/GROUP BY. Compound SELECT ORDER BY terms are resolved after all terms have compatible result-column counts.

`lookupName()` is the most branch-heavy path. It searches FROM sources in the innermost `NameContext`, with special treatment for nested FROM items, schema-table aliases, JOIN USING semantics, RIGHT/FULL JOIN precedence, rowid fallback, trigger `old`/`new`, UPSERT `excluded`, RETURNING base-register references, SELECT-list aliases, double-quoted string compatibility, and `true`/`false` identifiers. On success it mutates the AST node into a `TK_COLUMN`, `TK_REGISTER`, `TK_TRIGGER`, `TK_FUNCTION`/`coalesce` for FULL JOIN USING, `TK_NULL`, or related operator, then updates auth checks and scope reference counts.

Function resolution in `resolveExprStep()` looks up a `FuncDef`, enforces authorization and direct/unsafe/internal-function restrictions, propagates subtype requirements to arguments, marks constant/slow-changing functions, blocks non-deterministic functions in index/generated/partial-index contexts, rejects aggregate/window misuse, walks arguments with aggregate/window allowances temporarily narrowed, and converts aggregate calls to `TK_AGG_FUNCTION` with `op2` depth information.

Expression construction/deletion code follows SQLite's compact AST ownership rules. `Expr.x` may be a list or SELECT; `Expr.y` may hold a table, window, subquery data, etc. Deletion is recursive but optimized to avoid unnecessary recursion on unary left-deep chains. Duplication can allocate full-size or reduced/token-only expression nodes, and `TK_SELECT_COLUMN` copies preserve shared subquery ownership by using `pRight` for the one owner.

IN-code generation first validates vector arity, picks RHS representation with `sqlite3FindInIndex()`, codes/reorders the LHS vector, then either emits direct comparisons for small/non-constant lists or probes a b-tree/index. The generated bytecode distinguishes true, false, and NULL outcomes using separate false/null destinations. If an RHS b-tree exists, code checks LHS NULLs, performs rowid/index lookup, optionally checks RHS NULL status, and only scans RHS rows when needed to distinguish NULL from false.

## State and Persistence Behavior

- `MemJournal` persists journal bytes in heap chunks until forced to disk. Its durable state changes only when `memjrnlCreateFile()` successfully opens and writes through the underlying VFS. On failure it restores the original in-memory copy to preserve rollback capability.
- Resolver state is held in mutable AST nodes (`Expr`, `ExprList`, `Select`, `SrcItem`) and `NameContext` flags/counters. Important persisted semantic annotations include `Expr.op`, `iTable`, `iColumn`, `y.pTab`, `affExpr`, `op2`, `EP_*` flags, `Select.selFlags`, `SrcItem.colUsed`, `rowidUsed`, `isCorrelated`, and trigger masks `oldmask`/`newmask`.
- Expression allocator/copy/delete routines own heap memory through SQLite database allocators (`sqlite3DbMalloc*`, `sqlite3DbFree`, `sqlite3_free`) and parser cleanup registration (`sqlite3ParserAddCleanup`) for deferred deletes.
- Subquery and IN codegen persists reusable bytecode subroutines in `Expr.y.sub` plus `EP_Subrtn`, with result cursor/register locations in `Expr.iTable`. Compatible IN RHS subroutines are detected by scanning prior VDBE ops for `P4_SUBRTNSIG`.
- VDBE codegen state mutates `Parse` counters such as `nMem`, `nTab`, `nErr`, `nQueryLoop`, `okConstFactor`, `iSelfTab`, and scan-status/explain annotations.

## Dependencies and Integration Points

- The memory journal depends on the SQLite VFS abstraction (`sqlite3_vfs`, `sqlite3_file`, `sqlite3_io_methods`, `sqlite3OsOpen`, `sqlite3OsWrite`, `sqlite3OsClose`) and memory allocation APIs.
- Walker and resolver code depend on parser AST structures (`Expr`, `ExprList`, `Select`, `SrcList`, `SrcItem`, `NameContext`, `Window`, `Table`, `Index`, `Column`, `Parse`) and flags/macros from `sqliteInt.h`.
- Name resolution integrates with ALTER TABLE rename-token tracking (`IN_RENAME_OBJECT`, `sqlite3RenameTokenRemap`, `sqlite3RenameExprUnmap`), authorization (`sqlite3AuthRead`, `sqlite3AuthCheck`), trigger/upsert handling, generated columns, partial indexes, CHECK constraints, trusted schema/direct-only function policy, and window-function linking.
- Expression codegen integrates with the VDBE API (`sqlite3VdbeAddOp*`, `OP_*`, labels, P4 encodings, coverage macros), query planner/index metadata (`Index`, `KeyInfo`, collation and affinity), SELECT codegen (`sqlite3Select`, `SelectDest`), and optimizer features such as Bloom filters and constant factoring.
- Compile-time feature switches heavily shape behavior: `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_UPSERT`, `SQLITE_OMIT_GENERATED_COLUMNS`, `SQLITE_ENABLE_ATOMIC_WRITE`, `SQLITE_ENABLE_BATCH_ATOMIC_WRITE`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_COLUMN_USED_MASK`, and floating-point/hex integer options.

## Risks and Edge Cases

- `memjrnlRead()` assumes requested bytes are within `endpoint` and relies on chunk traversal/readpoint caching; off-by-one errors around chunk boundaries would cause short reads or stale chunk access. The function intentionally returns `SQLITE_IOERR_SHORT_READ` if asked past EOF.
- `memjrnlCreateFile()` zeroes the live `MemJournal` before opening the real file. Its restore-on-error path is critical: losing the copied chunk list would break rollback after spill failure.
- The resolver mutates AST nodes in place. Incorrect ownership handling when replacing aliases or FULL JOIN `coalesce()` expressions can leak or double-free subtrees.
- Double-quoted string fallback preserves legacy behavior but can silently turn misspelled identifiers into strings when DQS is enabled; the code logs warnings and normalizes when enabled.
- JOIN USING/FULL JOIN resolution is subtle. `pFJMatch`, `JT_RIGHT`, `JT_LEFT`, and `JT_LTORJ` handling control whether duplicate names are ambiguous, left/right-preferred, or converted to `coalesce()`.
- Column-use masks saturate at `BMS-1` and generated columns mark all table columns used. These are conservative by design; false negatives in covering-index analysis would be correctness bugs, while extra bits are acceptable but may reduce optimization.
- Aggregate/window resolution must maintain `NC_AllowAgg`, `NC_AllowWin`, `NC_HasAgg`, `NC_HasWin`, and aggregate-depth `op2` correctly across nested SELECTs. Misclassification can allow illegal SQL or generate wrong aggregate scope.
- Constant/nullability predicates are deliberately conservative. Several comments call out that false positives are dangerous, especially in `sqlite3ExprCanBeNull()`, affinity-elision checks, single-table constraint tests, and WHERE-only NOT NULL strength reduction.
- IN-operator optimization depends on matching affinity, collation, uniqueness, vector arity, and NULL semantics. Existing index reuse must not be chosen if comparison semantics differ from the SQL expression.
- Subroutine reuse for IN RHS/subqueries depends on signatures, SELECT ids, affinity strings, and completed `OP_BeginSubrtn` metadata. Incorrect reuse could bind a later expression to incompatible ephemeral data.
- Generated-column code uses `COLFLAG_BUSY` to detect loops and temporarily changes `Parse.iSelfTab`; missing restoration would corrupt later column-codegen context.

## Test Signals

Relevant test coverage should exercise:

- Journal modes: pure in-memory journal, immediate VFS journal (`nSpill==0`), spill threshold crossing, explicit `sqlite3JournalCreate()`, write/truncate/read across chunk boundaries, offset-zero atomic header rewrite, OOM during chunk allocation, and disk-open/write failure recovery.
- Walker behavior: callback abort/prune/continue paths, right-recursive expression trees, subqueries in expressions and FROM, compound SELECT traversal, and window definitions.
- Name resolution: unqualified/qualified/fully-qualified columns, aliases in WHERE/ORDER/GROUP/HAVING, schema table legacy names, rowid aliases, hidden/generated columns, nested FROM items, natural/USING/LEFT/RIGHT/FULL joins, trigger `old`/`new`, RETURNING references, UPSERT `excluded`, DQS fallback, true/false identifiers, and authorization failures.
- Function validation: no-such/wrong-arity functions, aggregate misuse, window misuse, FILTER on non-aggregate, ORDER BY inside non-aggregate functions, direct-only/unsafe functions in schema objects, internal functions, subtype-sensitive functions, `likely`/`unlikely` probability argument validation, and non-deterministic functions in partial indexes/generated columns/index expressions.
- SELECT resolution: correlated subqueries, aggregate detection, HAVING on non-aggregate queries, GROUP BY aggregate rejection, compound SELECT term count mismatch, compound ORDER BY integer/alias/expression matching, converted compound subquery ORDER BY handling, and table-valued function arguments.
- Expression utilities: affinity/collation precedence, reduced/full/token-only expression duplication, `TK_SELECT_COLUMN` ownership, expression-list vector assignment, constant-expression detection, default-expression parameter handling, row-value misuse diagnostics, integer literal bounds, NULLability inference, and generated-column loop detection.
- IN/subquery codegen: scalar and vector `IN`, RHS lists of one/two/many values, constant versus non-constant lists, rowid/index/ephemeral/noop RHS selection, affinity/collation mismatch blocking index reuse, NULL on LHS/RHS, correlated RHS, subquery reuse, Bloom-filter path, EXISTS/scalar subquery `LIMIT 1`, and arity mismatch errors.

## Chunk Boundaries and Cross-Chunk Notes

- The chunk begins inside the `memjournal.c` module after preceding declarations/comments and ends in the middle of `expr.c` at the start of `exprCodeInlineFunction()`. Later expression codegen behavior is outside this chunk.
- Types, flags, opcodes, and many helper routines used here are declared or implemented elsewhere in the amalgamation, including parser structures, VDBE APIs, SELECT expansion/codegen, window functions, authorization, rename support, table/index metadata, and memory allocation internals.
- This chunk does not define public SQLite C API entry points. Most symbols are `SQLITE_PRIVATE` or `static` internal compiler/runtime helpers consumed by surrounding SQLite modules.

### subset-b-009027: lines 114788-122462

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 114788-122462

## Work Item

- Chunk id: `subset-b-009027`
- Source range: `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c` lines 114788-122462
- Scope: tail of SQLite `expr.c`, full visible `alter.c`, and the opening/major body of `analyze.c` through `sqlite3AnalysisLoad()`, ending at the start of `attach.c`.

## Purpose

This chunk covers three high-impact SQLite subsystems inside the amalgamated SQLite copy used by WiredTiger tests:

1. Expression bytecode generation and expression reasoning helpers. These routines translate parsed `Expr` trees into VDBE instructions, support indexed-expression substitution, constant factoring, boolean jump generation, aggregate analysis, and temporary register management.
2. ALTER TABLE implementation. This code rewrites `sqlite_schema` SQL text for table rename, column rename, add column, and drop column operations, validates rewritten schema objects, and registers internal SQL helper functions used only by nested ALTER TABLE statements.
3. ANALYZE statistics generation and loading. This code creates and populates `sqlite_stat1` and optionally `sqlite_stat4`, accumulates index samples, emits VDBE programs for ANALYZE, and reloads planner statistics into `Table` and `Index` objects.

The chunk is storage-relevant indirectly: it does not implement WiredTiger storage, but it governs SQL semantics, schema mutation, planner statistics, and generated VDBE programs for the SQLite test dependency embedded under `wiredtiger/test/3rdparty`.

## Important APIs, Types, And Functions

### Expression Code Generation

- `exprCodeInlineFunction(Parse*, ExprList*, int, int)` handles inline SQL functions. It short-circuits `coalesce()`/`ifnull()`, lowers `iif()` to `TK_CASE`, emits `OP_Offset` for `sqlite_offset()` when enabled, and exposes test-only inline functions such as `expr_compare`, `expr_implies_expr`, `implies_nonnull_row`, and `affinity`.
- `sqlite3ExprCanReturnSubtype(Parse*, Expr*)` and `exprNodeCanReturnSubtype()` walk expression trees to conservatively decide whether a function expression might produce a SQLite subtype. This blocks expression-index substitution where subtype loss could change behavior.
- `sqlite3IndexedExprLookup(Parse*, Expr*, int)` tries to satisfy expression evaluation from an expression index rather than recomputing the expression. It checks cursor availability, self-table contexts, expression equality, affinity compatibility, NULL-row handling for outer joins, and subtype-sensitive function calls.
- `exprPartidxExprLookup(Parse*, Expr*, int)` substitutes constants from partial-index expressions for matching column references, including affinity application and `OP_IfNullRow` handling.
- `sqlite3ExprCodeTarget(Parse*, Expr*, int)` is the central expression-to-VDBE compiler. It covers literals, columns, aggregate columns/functions, function calls, comparisons, arithmetic, boolean operators, casts, subqueries, `IN`, `BETWEEN`, `CASE`, triggers, `RAISE()`, vectors, and outer-join null-row wrappers.
- `sqlite3ExprCodeRunJustOnce()`, `sqlite3ExprCodeTemp()`, `sqlite3ExprCode()`, `sqlite3ExprCodeCopy()`, `sqlite3ExprCodeFactorable()`, and `sqlite3ExprCodeExprList()` are layered helpers for constant factoring, temporary-register selection, guaranteed target-register writes, copy-preserving evaluation, and expression-list evaluation.
- `exprCodeBetween()`, `sqlite3ExprIfTrue()`, `sqlite3ExprIfFalse()`, and `sqlite3ExprIfFalseDup()` generate control-flow jumps for boolean expressions and preserve SQL NULL truth semantics.
- `sqlite3ExprCompare()`, `sqlite3ExprListCompare()`, and `sqlite3ExprCompareSkip()` implement conservative structural expression comparison used by optimizer rewrites, expression indexes, aggregate duplicate detection, and implication tests.
- `sqlite3ExprImpliesExpr()`, `sqlite3ExprImpliesNonNullRow()`, and helper walkers (`exprImpliesNotNull()`, `impliesNotNullRow()`) prove limited logical relationships used by optimizations such as LEFT JOIN to ordinary JOIN conversion.
- `sqlite3ExprCoveredByIndex()` uses `IdxCover` and a walker to determine whether an expression can be evaluated from an index alone.
- `sqlite3ReferencesSrcList()` checks whether an aggregate function expression references a particular source list, while excluding references from nested subqueries.
- Aggregate helpers include `sqlite3AggInfoPersistWalkerInit()`, `findOrCreateAggInfoColumn()`, `analyzeAggregate()`, `sqlite3ExprAnalyzeAggregates()`, and `sqlite3ExprAnalyzeAggList()`.
- Temporary register helpers include `sqlite3GetTempReg()`, `sqlite3ReleaseTempReg()`, `sqlite3GetTempRange()`, `sqlite3ReleaseTempRange()`, `sqlite3ClearTempRegCache()`, `sqlite3TouchRegister()`, and debug/stat4 helper `sqlite3FirstAvailableRegister()`.

### ALTER TABLE

- `isAlterableTable()` rejects system tables, eponymous virtual tables, and read-only shadow tables.
- `renameTestSchema()`, `renameFixQuotes()`, and `renameReloadSchema()` are reusable ALTER TABLE support routines. They validate parseability, normalize double-quoted strings in schema SQL, change schema cookies, and reparse schemas.
- `sqlite3AlterRenameTable()` implements `ALTER TABLE ... RENAME TO`, including object-name conflict checks, authorization, nested `sqlite_schema` updates, temp-schema trigger/view rewrites, virtual-table `xRename`, schema reload, and post-rename validation.
- `sqlite3AlterBeginAddColumn()` clones the target `Table` into `Parse.pNewTable` under an `sqlite_altertab_` name so the parser can append the new column definition to a temporary table model.
- `sqlite3AlterFinishAddColumn()` validates constraints for `ADD COLUMN`, updates the stored `CREATE TABLE` SQL with the new column text, upgrades the file format to at least 3 when necessary, reloads schema, and runs `pragma_quick_check()` for CHECK, generated NOT NULL, and STRICT-table validation.
- `sqlite3AlterRenameColumn()` implements parser-facing `ALTER TABLE ... RENAME COLUMN`, then delegates SQL text edits to internal `sqlite_rename_column()`.
- `RenameToken` maps parse-tree nodes or column-name storage locations back to token spans in the original SQL. `RenameCtx` collects matching tokens for a specific rename operation.
- Rename-token utilities include `sqlite3RenameTokenMap()`, `sqlite3RenameTokenRemap()`, `sqlite3RenameExprUnmap()`, `sqlite3RenameExprlistUnmap()`, `renameTokenFind()`, `renameColumnTokenNext()`, and `renameTokenFree()`.
- `renameParseSql()` reparses stored DDL in `PARSE_MODE_RENAME` while preserving token mappings and optionally marking temp schema context.
- `renameEditSql()` edits the original SQL by replacing collected token spans with the new identifier, or by converting double-quoted strings to single-quoted strings for quote-fix mode.
- `renameResolveTrigger()` resolves trigger WHEN clauses, trigger SELECTs, UPDATE target expressions, FROM clauses, and UPSERT expressions so column/table token searches can walk semantically resolved trees.
- Internal SQL functions registered by `sqlite3AlterFunctions()` are `sqlite_rename_column`, `sqlite_rename_table`, `sqlite_rename_test`, `sqlite_drop_column`, and `sqlite_rename_quotefix`.
- `dropColumnFunc()` edits a `CREATE TABLE` statement text to remove one column definition.
- `sqlite3AlterDropColumn()` validates `DROP COLUMN`, rewrites schema SQL, reloads and validates schema, then rewrites on-disk table records for non-virtual dropped columns.

### ANALYZE

- `openStatTable()` creates or clears `sqlite_stat1` and, when STAT4 is enabled, `sqlite_stat4`, then opens them for writing.
- `StatSample` stores one STAT4 sample's `nEq`, `nLt`, `nDLt`, rowid/key blob, sample classification, and tie-break hash.
- `StatAccum` is the heap state shared by internal SQL functions `stat_init()`, `stat_push()`, and `stat_get()`. It tracks row counts, distinct counts, skip-ahead state for limited analysis, current sample state, and STAT4 sample arrays.
- `statInit()`, `statPush()`, and `statGet()` implement the internal SQL functions used by generated ANALYZE bytecode.
- STAT4 helpers include `sampleClear()`, `sampleSetRowid()`, `sampleSetRowidInt64()`, `sampleCopy()`, `sampleIsBetterPost()`, `sampleIsBetter()`, `sampleInsert()`, and `samplePushPrevious()`.
- `analyzeOneTable()` emits the VDBE program that scans each index, detects key-prefix changes, calls `stat_push()`, writes `sqlite_stat1`, and optionally writes `sqlite_stat4` samples.
- `analyzeDatabase()`, `analyzeTable()`, and `sqlite3Analyze()` implement the public ANALYZE command forms for all databases, one schema, one table, or one index.
- `decodeIntArray()` parses integer lists and trailing planner flags from `sqlite_stat1`/`sqlite_stat4` text, including `unordered`, `sz=`, `noskipscan`, and optional `costmult=`.
- `analysisLoader()` loads `sqlite_stat1` rows into `Index.aiRowLogEst`, optional `Index.aiRowEst`, table row estimates, and planner flags.
- `sqlite3DeleteIndexSamples()`, `initAvgEq()`, `findIndexOrPrimaryKey()`, `loadStatTbl()`, `loadStat4()`, and `sqlite3AnalysisLoad()` clear and reload planner statistics and STAT4 samples from persistent stat tables.

## Control Flow

Expression evaluation generally enters through `sqlite3ExprCode()` or `sqlite3ExprCodeTarget()`. `sqlite3ExprCode()` guarantees the value lands in the requested register by adding `OP_Copy` or `OP_SCopy` if `sqlite3ExprCodeTarget()` returns a different register. `sqlite3ExprCodeTarget()` starts by checking for indexed-expression replacement via `sqlite3IndexedExprLookup()`, then dispatches on `Expr.op`. Simple constants become direct VDBE loads. Column references flow through self-table/generator handling, partial-index constant substitution, or `sqlite3ExprCodeGetColumn()`. Operators allocate temporary registers, emit opcode-aligned VDBE operations, and release temporaries at the shared exit.

Function calls resolve a `FuncDef`, perform constant factoring when legal, lower inline functions, enforce direct/unsafe function usability, determine collation dependencies, code arguments, optionally allow virtual-table function overloads, and finally call `sqlite3VdbeAddFunctionCall()`. Subqueries route to `sqlite3CodeSubselect()`. `CASE` and `BETWEEN` synthesize temporary expression trees and labels so SQL short-circuiting and NULL handling are preserved.

Boolean jumps use `sqlite3ExprIfTrue()` and `sqlite3ExprIfFalse()` rather than always materializing booleans. These routines recursively short-circuit `AND`/`OR`, invert `NOT`, handle `IS TRUE`/`IS FALSE`, translate comparison tokens to aligned VDBE comparison opcodes, and emit `OP_If`/`OP_IfNot` as the default path.

Aggregate analysis uses a walker. `analyzeAggregate()` turns column references in the aggregate query's source list into `TK_AGG_COLUMN` entries in `AggInfo.aCol[]`, detects duplicate aggregate functions for reuse in `AggInfo.aFunc[]`, handles expression-index references inside aggregate functions, and prunes nested aggregate functions at the appropriate walker depth.

ALTER TABLE commands follow a schema-text rewrite model. Parser-facing functions validate the target object and then use `sqlite3NestedParse()` to run internal UPDATE statements against `sqlite_schema` or `sqlite_temp_schema`. Those nested statements invoke internal SQL functions such as `sqlite_rename_table()` or `sqlite_rename_column()` to reparse each stored DDL statement, find token spans tied to the target table/column, edit the SQL text, and return the new definition. After rewrite, `renameReloadSchema()` invalidates/reloads schemas and `renameTestSchema()` validates that dependent schema objects still parse and resolve.

`DROP COLUMN` has an additional physical-record rewrite path. After schema SQL is edited and validated, `sqlite3AlterDropColumn()` opens the table for write, scans every row, constructs a new record omitting the dropped non-virtual column, preserves rowid or WITHOUT ROWID primary-key fields, and reinserts with `OPFLAG_SAVEPOSITION`.

ANALYZE generation starts at `sqlite3Analyze()`. It reads schema, chooses all databases, one database, one table, or one index, then calls `analyzeDatabase()` or `analyzeTable()`. `openStatTable()` prepares the stat tables. `analyzeOneTable()` scans each index with a generated VDBE loop, compares current index columns against previous column registers to compute the first changed prefix, calls `stat_push()`, and finally extracts stat rows with `stat_get()`. With STAT4 and no analysis limit, it then iterates samples and writes `sqlite_stat4`.

Statistics loading starts with `sqlite3AnalysisLoad()`. It clears prior in-memory statistics, reads `sqlite_stat1` through `sqlite3_exec()` and `analysisLoader()`, applies defaults to indexes without stat1 rows, and then optionally disables lookaside and loads STAT4 data via `loadStat4()`/`loadStatTbl()`.

## State And Persistence Behavior

- Expression code generation mutates `Parse` state heavily: `nMem`, `nTab`, temp-register caches, `pConstExpr`, `pIdxEpr`, `pIdxPartExpr`, `okConstFactor`, aggregate metadata, error state, and generated VDBE instruction streams.
- Constant factoring persists expressions in `Parse.pConstExpr` so repeated constant expressions can be initialized once per prepared statement. Function-containing constants are guarded by `OP_Once`.
- Expression-index lookup deliberately avoids replacement when function subtype propagation could be semantically visible or when outer-join NULL rows require original expression evaluation.
- ALTER TABLE persists schema mutations by updating rows in `sqlite_schema`, `sqlite_temp_schema`, and `sqlite_sequence` where applicable. It also changes schema cookies and reparses schema definitions.
- ALTER TABLE stores transient rename state in `Parse.pRename` as linked `RenameToken` nodes. These must be remapped or unmapped as parse trees are transformed to avoid stale token references.
- `ADD COLUMN` updates only schema SQL for most columns but may run `pragma_quick_check()` to validate existing rows. `DROP COLUMN` can rewrite actual table records.
- ANALYZE persists planner statistics in `sqlite_stat1` and `sqlite_stat4`. `sqlite_stat1` holds text row/cardinality estimates and flags. `sqlite_stat4` holds sampled key blobs plus text-encoded `neq`, `nlt`, and `ndlt` arrays.
- `sqlite3AnalysisLoad()` converts persisted stat tables back into in-memory `Table` and `Index` estimates used by the planner; STAT4 sample buffers are allocated under the database connection and freed by `sqlite3DeleteIndexSamples()`.

## Dependencies And Integration Points

- All three subsystems are tightly integrated with SQLite core types: `Parse`, `Expr`, `ExprList`, `Select`, `SrcList`, `Table`, `Index`, `AggInfo`, `NameContext`, `Walker`, `Vdbe`, `FuncDef`, `sqlite3`, `Schema`, `HashElem`, and `sqlite3_value`.
- Expression code generation depends on VDBE opcodes (`OP_Column`, `OP_Function`, `OP_If`, `OP_IfNullRow`, `OP_Once`, `OP_Param`, `OP_MakeRecord`, etc.), collation lookup, virtual-table function overloading, generated-column support, aggregate/window state, subquery code generation, and optimizer metadata.
- ALTER TABLE depends on nested SQL execution, parser modes, schema tables, name resolution, trigger/view/index parsing, virtual-table callbacks, foreign-key metadata, authorization callbacks, writable-schema behavior, schema cookies, and Btree mutex discipline.
- ANALYZE depends on Btree/table/index cursors, stat-table schemas, VDBE program construction, internal SQL functions, planner flags, preupdate hooks, schema hash tables, optional STAT4 compilation, and lookaside-memory disablement while loading samples.
- The `#ifndef SQLITE_OMIT_*` and `#ifdef SQLITE_ENABLE_*` gates are major integration boundaries. Behavior changes substantially when ALTER TABLE, ANALYZE, STAT4, virtual tables, generated columns, foreign keys, window functions, floating point, trigger support, preupdate hooks, or authorization are omitted/enabled.

## Risks And Edge Cases

- Expression comparison routines are intentionally conservative. Incorrect false equality can cause wrong query results, while false inequality generally only disables optimizations.
- Indexed-expression substitution is risky around generated-column affinity, outer joins, and function subtypes. The code includes explicit guards for these cases because replacing expression evaluation with index reads can otherwise change visible SQL values.
- Boolean and comparison code relies on token values matching VDBE opcode values. The assertions protect debug builds, but changes to opcode/token definitions are high risk.
- Constant factoring must be disabled in contexts where an opcode such as `OP_IfNullRow` can overwrite a supposedly constant target register.
- Rename-token mapping uses pointers into parse tree nodes and original SQL text. The debug-only `renameTokenCheckAll()` exists because stale pointer comparisons are undefined behavior after objects are freed or transformed.
- ALTER TABLE schema rewriting is fragile by design: it reparses stored SQL text, edits token spans, then validates the full schema. `PRAGMA writable_schema=ON` weakens error handling by allowing some malformed schema SQL to pass through unchanged.
- `ADD COLUMN` constraints have compatibility restrictions: cannot add PRIMARY KEY or UNIQUE columns, cannot add NOT NULL without non-NULL default to non-empty tables, cannot add REFERENCES with non-NULL default under foreign keys, cannot add STORED generated columns to non-empty tables.
- `DROP COLUMN` must reject primary-key, unique, last-column, view, virtual-table, and system-table cases. The physical rewrite path must preserve WITHOUT ROWID primary keys and virtual/generated column semantics.
- ANALYZE sample memory layout is manually packed. Miscomputed sizes or alignment would corrupt sample arrays; the code uses `ROUND8`, `EIGHT_BYTE_ALIGNMENT`, and asserts to control this.
- Loading STAT4 sample blobs intentionally allocates 8 extra zero bytes to avoid overread when corrupted records are compared later.
- Limited analysis (`db->nAnalysisLimit`) uses skip-ahead behavior from `stat_push()` and disables STAT4 accumulation by setting `mxSample` to zero.

## Test Signals

- The chunk contains many `testcase()`, `VdbeCoverage()`, `VdbeCoverageIf()`, and `VdbeCoverageNeverTaken()` markers. These are direct SQLite test-suite hooks for boolean branches, comparison opcodes, join NULL-row behavior, aggregate handling, STAT4 register allocation, and ALTER TABLE edge cases.
- Comments cite specific fuzz or regression signals, including OSSFuzz recursion prevention for collate/uplus nodes, a dbsqlfuzz `DROP COLUMN` empty-field case, and SQLite forum/regression references around subtype-preserving expression-index substitution and STAT4 temp-register cache clearing.
- Useful SQL-level tests for this range include expression-index queries with subtype-returning functions, generated columns, outer joins with expression indexes, `CASE`/`BETWEEN`/`IN` NULL semantics, aggregate duplicate detection, ALTER TABLE rename across views/triggers/foreign keys, ADD COLUMN constraint failures on non-empty tables, DROP COLUMN on rowid and WITHOUT ROWID tables, and ANALYZE with and without STAT4.
- Runtime verification signals include schema cookie changes, successful reparsing by `sqlite_rename_test`, `pragma_quick_check()` failures during ADD COLUMN, `sqlite_stat1` row contents, `sqlite_stat4` sample counts, and planner state after `OP_LoadAnalysis`.

## Cross-Chunk Notes

- This range begins in the middle of `expr.c`; some helper definitions used here, such as `codeCompare()`, `exprCodeVector()`, `sqlite3ExprCodeIN()`, `sqlite3ExprCodeGetColumn()`, and AST/type definitions, are defined earlier in the amalgamation.
- This range ends at the start of `attach.c`; ATTACH/DETACH implementation continues in the next chunk and should be researched separately.
- The final per-file report should reconcile this chunk with earlier `expr.c` chunks and later `analyze.c`/`attach.c` chunks to describe the full SQLite amalgamation file coherently.

### subset-b-009028: lines 122463-130124

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 122463-130124

## Scope

This chunk spans the tail of SQLite `attach.c`, all of `auth.c`, most of `build.c`, all of `callback.c`, and the beginning of `delete.c` within the SQLite amalgamation vendored under WiredTiger tests. It starts in ATTACH/DETACH code generation, covers schema name fixing for DDL expressions, authorization callbacks, table/index/view/foreign-key/schema construction and destruction helpers, collation and function lookup registries, schema cleanup/allocation, and ends in `sqlite3GenerateRowDelete()` immediately after the initial row seek for a generated single-row delete.

The covered range is parser/code-generator infrastructure, not the btree pager itself. It builds and maintains in-memory schema objects and emits VDBE opcodes that later mutate persistent database btrees and `sqlite_schema`.

## Purpose

The ATTACH/DETACH tail compiles `ATTACH` and `DETACH` statements into calls to internal SQL functions (`sqlite_attach`, `sqlite_detach`) after resolving arguments and checking authorization.

The DDL fixer code ensures views, triggers, and indexes stored in a specific schema do not contain persistent references to objects in a different schema, except for TEMP objects. It also marks DDL expressions and rejects host parameters outside schema initialization.

The authorization module implements `sqlite3_set_authorizer()` and the internal authorization checks used by parser actions and expression resolution. It gates schema changes, reads, writes, transactions, savepoints, ATTACH/DETACH, index rebuilds, and DELETE generation.

The large `build.c` portion is SQLite's parser action layer for schema construction and maintenance. It creates table, view, index, primary-key, CHECK, generated-column, foreign-key, and CTE structures; emits VDBE bytecode to update `sqlite_schema`, schema cookies, root pages, and statistics tables; manages schema reset and memory cleanup; and provides shared helpers for source lists, identifier lists, transactions, constraints, reindexing, and key metadata.

The `callback.c` portion manages application-defined collations/functions, built-in function lookup, text-encoding defaults, collation-needed callbacks, and schema object cleanup/allocation.

The `delete.c` prefix starts DELETE statement compilation: it locates the target table, rejects unsafe targets, handles view materialization and `DELETE ... ORDER BY ... LIMIT`, chooses truncate/one-pass/two-pass strategies, and invokes row-delete code generation.

## Important APIs, Types, and Functions

- ATTACH/DETACH and DDL fixing:
  - `codeAttach()`, `sqlite3Detach()`, `sqlite3Attach()` compile attach/detach statements into VDBE function calls and statement expiration.
  - `DbFixer`, `fixExprCb()`, `fixSelectCb()`, `sqlite3FixInit()`, `sqlite3FixSrcList()`, `sqlite3FixSelect()`, `sqlite3FixExpr()`, and `sqlite3FixTriggerStep()` walk parse trees for schema pinning and illegal cross-database references.
- Authorization:
  - `sqlite3_set_authorizer()` stores `db->xAuth`/`db->pAuthArg` and expires prepared statements when enabling authorization.
  - `sqlite3AuthReadCol()`, `sqlite3AuthRead()`, and `sqlite3AuthCheck()` call user authorization hooks and map `SQLITE_DENY`, `SQLITE_IGNORE`, and bad return codes into parse errors.
  - `sqlite3AuthContextPush()` and `sqlite3AuthContextPop()` manage `pParse->zAuthContext`, especially for views/triggers.
- Shared-cache and final VDBE coding:
  - `TableLock`, `lockTable()`, `sqlite3TableLock()`, and `codeTableLocks()` accumulate and emit `OP_TableLock`.
  - `sqlite3FinishCoding()` appends `OP_Halt`, emits transaction/schema-cookie checks, virtual-table `OP_VBegin`, table locks, autoincrement setup, constant-expression factoring, RETURNING cursor setup, and `sqlite3VdbeMakeReady()`.
  - `sqlite3NestedParse()` runs parser/codegen recursively for generated SQL used to update schema metadata.
- Schema lookup/lifecycle:
  - `sqlite3FindTable()`, `sqlite3LocateTable()`, `sqlite3LocateTableItem()`, `sqlite3PreferredTableName()`, `sqlite3FindIndex()`, `sqlite3FindDbName()`, `sqlite3FindDb()`, and `sqlite3TwoPartName()` resolve schema-qualified names.
  - `sqlite3FreeIndex()`, `sqlite3UnlinkAndDeleteIndex()`, `sqlite3DeleteColumnNames()`, `deleteTable()`, `sqlite3DeleteTable()`, `sqlite3UnlinkAndDeleteTable()`, `sqlite3SchemaClear()`, and `sqlite3SchemaGet()` clean schema-owned structures.
  - `sqlite3ResetOneSchema()`, `sqlite3ResetAllSchemasOfConnection()`, `sqlite3CollapseDatabaseArray()`, and `sqlite3CommitInternalChanges()` manage schema invalidation and attached-database array compaction.
- Table and column creation:
  - `sqlite3StartTable()` initializes `pParse->pNewTable`, checks names/authorization/collisions, allocates schema placeholder rows, and emits root-page allocation.
  - `sqlite3AddColumn()`, `sqlite3AddNotNull()`, `sqlite3AffinityType()`, `sqlite3AddDefaultValue()`, `sqlite3AddPrimaryKey()`, `sqlite3AddCheckConstraint()`, `sqlite3AddCollateType()`, and `sqlite3AddGenerated()` populate `Table`, `Column`, defaults, constraints, affinities, collations, and generated-column metadata.
  - `sqlite3ColumnSetExpr()`, `sqlite3ColumnExpr()`, `sqlite3ColumnSetColl()`, `sqlite3ColumnColl()`, `sqlite3StorageColumnToTable()`, and `sqlite3TableColumnToStorage()` support generated/default expression and virtual/stored column layout mapping.
- Table/view/drop behavior:
  - `sqlite3EndTable()` finalizes CREATE TABLE/CREATE TABLE AS SELECT, strict tables, generated columns, WITHOUT ROWID conversion, schema-table updates, autoincrement table creation, schema reparsing, and in-memory schema insertion.
  - `sqlite3CreateView()`, `viewGetColumnNames()`, `sqlite3ViewGetColumnNames()`, and `sqliteViewResetAll()` build views and lazily derive view column metadata.
  - `sqlite3RootPageMoved()`, `destroyRootPage()`, `destroyTable()`, `sqlite3ClearStatTables()`, `sqlite3CodeDropTable()`, `sqlite3DropTable()`, `sqlite3ReadOnlyShadowTables()`, and `tableMayNotBeDropped()` emit destructive schema changes and enforce protected-object rules.
- Index and key metadata:
  - `resizeIndexObject()`, `estimateTableWidth()`, `estimateIndexWidth()`, `isDupColumn()`, `recomputeColumnsNotIndexed()`, and `convertToWithoutRowidTable()` transform index metadata for rowid and WITHOUT ROWID tables.
  - `sqlite3RefillIndex()`, `sqlite3AllocateIndexObject()`, `sqlite3HasExplicitNulls()`, `sqlite3CreateIndex()`, `sqlite3DefaultRowEst()`, `sqlite3DropIndex()`, `sqlite3Reindex()`, and `sqlite3KeyInfoOfIndex()` allocate, validate, persist, rebuild, and describe indexes.
- Foreign keys, lists, transactions, and constraints:
  - `sqlite3CreateForeignKey()` and `sqlite3DeferForeignKey()` allocate `FKey` entries and link them into table and schema hashes.
  - `sqlite3ArrayAllocate()`, `sqlite3IdListAppend()`, `sqlite3IdListDelete()`, `sqlite3IdListIndex()`, and `sqlite3SrcList*()` helpers own parser list construction and cleanup.
  - `sqlite3BeginTransaction()`, `sqlite3EndTransaction()`, `sqlite3Savepoint()`, `sqlite3OpenTempDatabase()`, `sqlite3CodeVerifySchema()`, `sqlite3BeginWriteOperation()`, `sqlite3MultiWrite()`, and `sqlite3MayAbort()` set VDBE transaction, schema verification, and statement-journal requirements.
  - `sqlite3HaltConstraint()`, `sqlite3UniqueConstraint()`, and `sqlite3RowidConstraint()` emit constraint failure opcodes and messages.
- Collation/function/schema callbacks:
  - `callCollNeeded()`, `synthCollSeq()`, `sqlite3CheckCollSeq()`, `findCollSeqEntry()`, `sqlite3FindCollSeq()`, `sqlite3SetTextEncoding()`, `sqlite3GetCollSeq()`, and `sqlite3LocateCollSeq()` locate or synthesize collations and update default encoding state.
  - `matchQuality()`, `sqlite3FunctionSearch()`, `sqlite3InsertBuiltinFuncs()`, and `sqlite3FindFunction()` manage built-in and application-defined SQL functions.
- DELETE prefix:
  - `sqlite3SrcListLookup()`, `sqlite3CodeChangeCount()`, `sqlite3IsReadOnly()`, `sqlite3MaterializeView()`, `sqlite3LimitWhere()`, `sqlite3DeleteFrom()`, and the opening of `sqlite3GenerateRowDelete()` compile DELETE statements and begin single-row delete code.

## Control Flow

ATTACH/DETACH compilation first reads schema, resolves attach expressions using a `NameContext`, invokes authorization using either the literal auth string or NULL, then codes filename/dbname/key expressions into temporary registers. A VDBE function call dispatches to `attachFunc()` or `detachFunc()`, followed by `OP_Expire` to invalidate statements at the correct scope. All owned expressions are deleted on exit.

DDL fixing is walker-driven. `sqlite3FixInit()` binds a target schema and installs expression/select callbacks. Expression callbacks tag schema expressions with `EP_FromDDL` and reject variables unless schema initialization is in progress, where variables are converted to NULL. Select callbacks walk source lists, reject explicit cross-schema references, convert unresolved database names into fixed `Schema*` references, and recursively walk `ON` clauses and CTE subqueries.

Authorization control is callback-centered. Public registration is mutex-protected. Internal reads call `SQLITE_READ` with table/column/db/context; `SQLITE_IGNORE` rewrites readable expressions to NULL, while DENY sets `SQLITE_AUTH`. Generic checks skip during database initialization and special parses, call `db->xAuth`, and normalize illegal callback return values into an authorizer malfunction.

`sqlite3FinishCoding()` is the top-level closeout for one SQL statement. It short-circuits nested parses and earlier errors, ensures a VDBE exists, appends RETURNING result loops when needed, emits `OP_Halt`, rewinds to `OP_Init`, emits `OP_Transaction` and schema-cookie checks for every database in `cookieMask`, emits virtual-table and shared-cache lock setup, begins autoincrement state, evaluates factored constants, opens RETURNING ephemeral storage, jumps to executable code, then marks the program ready.

CREATE TABLE flows from `sqlite3StartTable()` through column/constraint routines into `sqlite3EndTable()`. Start-table resolves the target database, rejects illegal temp qualification and reserved names, checks auth and collisions, allocates a `Table`, and emits placeholder schema-table insertion and root-page allocation. End-table resolves CHECK and generated expressions, applies STRICT and WITHOUT ROWID transformations, estimates widths, generates CTAS population code if needed, updates the schema placeholder row with final SQL text, creates `sqlite_sequence` for AUTOINCREMENT, emits schema reparse and generated-column validation SQL, and inserts schema-loaded tables into the in-memory hash when reading existing schema.

WITHOUT ROWID conversion is an in-place metadata and bytecode rewrite. It marks primary-key columns NOT NULL, changes the table root btree from integer-key to blob-key, creates a primary-key index for former integer primary keys, removes duplicate PK columns, bypasses the separate PK btree/schema entry, points the PK index at the table root, appends missing PK columns to UNIQUE indexes, and makes the PK index covering by appending non-virtual table columns.

CREATE INDEX first resolves the table and index database, rejects views/virtual tables/system tables, invents automatic names for constraints, checks authorization, resolves and validates each indexed expression, computes collations and sort order, appends rowid or WITHOUT ROWID primary-key columns, suppresses duplicate automatic constraints, links schema structures, emits root-page creation and `sqlite_schema` insertion for explicit indexes, optionally refills the index from table contents, reparses schema, and reorders REPLACE-conflict indexes to the end of the table index list.

DROP TABLE/INDEX flows are destructive code-generation paths. They read schema, locate target objects, validate object kind and protected status, perform authorization, clear statistics rows, emit foreign-key/drop-trigger work, delete schema rows through generated SQL, destroy btree root pages in descending order to avoid auto-vacuum relocation hazards, emit `OP_DropTable`/`OP_DropIndex`/virtual-table destroy opcodes, change schema cookies, and reset view column caches.

The collation and function callback code uses hash tables and best-match scoring. Collation lookup first finds or creates a per-name triplet for UTF-8/UTF-16LE/UTF-16BE, invokes collation-needed callbacks if no comparator exists, and can copy a comparator from another encoding as a fallback. Function lookup searches application-defined functions first, then built-ins unless built-ins are preferred or a new function is being created; `matchQuality()` ranks arity and encoding compatibility.

DELETE compilation starts by resolving the single source table, collecting triggers and foreign-key complexity, optionally rewriting `ORDER BY/LIMIT` into a `rowid IN (SELECT ...)` or composite-PK `IN` expression, initializing view column names, rejecting read-only targets, checking delete authorization, assigning cursors, materializing views for INSTEAD OF triggers, resolving the WHERE clause, optionally using the truncate optimization, otherwise choosing rowid RowSet or WITHOUT ROWID ephemeral-PK collection plus WHERE one-pass planning, opening write cursors, and delegating each row to virtual-table `OP_VUpdate` or `sqlite3GenerateRowDelete()`.

## State and Persistence Behavior

This code mutates parser state (`Parse`), connection state (`sqlite3`), schema state (`Schema`, `Table`, `Index`, `FKey`, `Trigger`, `With`, `Cte`), and generated VDBE programs. Persistent disk effects are usually deferred into emitted opcodes and nested SQL: `sqlite_schema` rows are inserted/updated/deleted, root pages are created/destroyed, schema cookies are incremented, autoincrement state may create or update `sqlite_sequence`, and index refill/delete operations modify table/index btrees.

Schema caches are explicit and fragile. `sqlite3ResetOneSchema()` and `sqlite3ResetAllSchemasOfConnection()` clear table/index/trigger/fkey hashes or defer reset with `DB_ResetWanted` while schema locks are held. `sqlite3SchemaClear()` deletes triggers first, indexes, tables, foreign-key hashes, and bumps `iGeneration` only for loaded schemas. `sqlite3CollapseDatabaseArray()` removes detached database slots after schema reset.

Memory ownership is distributed through parser structures. Many routines consume `Expr*`, `ExprList*`, `SrcList*`, `Token`-derived strings, and schema objects even on error. Common exit labels free partially owned objects. `sqlite3DeleteTable()` uses `nTabRef`; `deleteTable()` unlinks indexes from hashes when not in byte-counting mode, frees foreign keys/virtual table/view select state, column names, checks, and table storage.

Name, type, and collation data are compacted inside column and index allocations. Column name storage may contain nul-separated type and collation strings. Index allocations pack `Index`, collation pointer array, row estimates, column numbers, sort-order bytes, name, and extra collation names into one allocation unless resized later.

DDL safety state is encoded in flags such as `TF_HasPrimaryKey`, `TF_WithoutRowid`, `TF_NoVisibleRowid`, `TF_Strict`, `TF_HasGenerated`, `TF_HasVirtual`, `TF_HasStored`, `TF_Shadow`, `COLFLAG_*`, `DBFLAG_SchemaChange`, `DBFLAG_SchemaKnownOk`, `DB_ResetWanted`, and per-parse `isMultiWrite`, `mayAbort`, `writeMask`, and `cookieMask`.

DELETE code may use transient RowSets or ephemeral btrees to store rowids/primary keys before deletion. For simple whole-table deletes, the truncate path emits `OP_Clear` directly for the table and indexes and can count changes. For complex deletes, state must preserve WHERE cursors, one-pass cursor positions, trigger/FK context, and autoincrement end-of-statement work.

## Dependencies and Integration Points

This chunk integrates with SQLite's parser, expression walker, resolver, VDBE code emitter, btree layer, virtual table layer, trigger/foreign-key modules, schema hashes, SQL function/collation registries, and memory allocator. Important dependencies include `sqlite3ReadSchema()`, `sqlite3RunParser()`, `sqlite3NestedParse()`, `sqlite3VdbeAddOp*()`, `sqlite3Btree*()`, `sqlite3Hash*()`, `sqlite3Walk*()`, `sqlite3Resolve*()`, `sqlite3Select*()`, `sqlite3Vtab*()`, `sqlite3Fk*()`, `sqlite3Trigger*()`, `sqlite3WhereBegin()`, `sqlite3WhereOkOnePass()`, and `sqlite3OpenTableAndIndices()`.

Compile-time feature gates heavily affect behavior: `SQLITE_OMIT_ATTACH`, `SQLITE_OMIT_AUTHORIZATION`, `SQLITE_OMIT_SHARED_CACHE`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_UPSERT`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_GENERATED_COLUMNS`, `SQLITE_OMIT_CHECK`, `SQLITE_OMIT_AUTOINCREMENT`, `SQLITE_OMIT_ALTERTABLE`, `SQLITE_OMIT_AUTOVACUUM`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_TEMPDB`, `SQLITE_OMIT_REINDEX`, `SQLITE_OMIT_CTE`, `SQLITE_OMIT_UTF16`, `SQLITE_ENABLE_HIDDEN_COLUMNS`, `SQLITE_ENABLE_SORTER_REFERENCES`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_ENABLE_PREUPDATE_HOOK`, and debug/test macros.

Authorization hooks are public API integration points and affect parse-time behavior rather than run-time btree checks. Collation-needed callbacks and application-defined SQL function registration are also public extension points.

In this repository, the code is part of a vendored SQLite amalgamation under `sources/storage-engines/wiredtiger/test/3rdparty/sqlite3`. It affects tests or tooling that compile this SQLite copy; it is not part of WiredTiger's storage engine implementation itself.

## Risks and Edge Cases

- Schema mutation code relies on exact ordering. For CREATE TABLE, the table schema row placeholder must exist before implicit index rows. For DROP under auto-vacuum, root pages must be destroyed from largest to smallest.
- DDL fixer behavior is security-sensitive. Missing `fixedSchema` tagging or cross-schema checks could allow persistent view/trigger/index definitions to bind to objects outside their intended schema.
- Authorization handling must preserve `SQLITE_IGNORE` semantics. In read expressions it becomes NULL; for some operations such as DELETE it disables optimizations rather than denying the operation.
- `sqlite3FinishCoding()` appends initialization/transaction code after the main program and patches `OP_Init`; incorrect cookie/write mask handling can miss schema-change detection or statement-journal requirements.
- `sqlite3NestedParse()` is reentrant and temporarily changes parser tail state plus `DBFLAG_PreferBuiltin`; missing restoration would corrupt the outer parse.
- STRICT tables, generated columns, WITHOUT ROWID, INTEGER PRIMARY KEY, AUTOINCREMENT, and DESC primary-key handling interact. Small changes can alter persistent record layout, index coverage, or legacy compatibility.
- Column storage layout is compact and non-obvious: name, optional type, and optional collation share one allocation. Offset mistakes would corrupt schema metadata.
- `sqlite3CreateIndex()` has many special cases: automatic constraint index deduplication, rename-object retention, partial-index resolution, expression index ownership, WITHOUT ROWID PK suffixes, missing collation deactivation, and REPLACE-index list ordering.
- Public callback lookup is mutable. Collation fallback copies a comparator but not its destructor. Function creation must never return read-only built-in `FuncDef` objects for overwrite.
- `sqlite3ShadowTableName()` temporarily writes into the supplied name string to split at the final underscore; callers must provide mutable strings.
- DELETE one-pass mode must preserve cursor positioning around triggers and index deletes. `aToOpen` cursor elision is sensitive to `aiCurOnePass` offsets.
- View DELETE requires INSTEAD OF triggers and materializes view rows into an ephemeral table; read-only checks must distinguish views with RETURNING triggers from modifiable trigger-backed views.
- Many paths deliberately continue on `ifNotExists`, `noErr`, or schema initialization with silent or empty errors. Tests need to distinguish OOM, corrupt schema, suppressed errors, and accepted no-op DDL.

## Test Signals

- ATTACH/DETACH tests with literal and expression arguments, authorization DENY, invalid authorizer return values, and statement expiration behavior.
- Authorizer tests for `SQLITE_READ` returning OK/IGNORE/DENY, DELETE returning IGNORE disabling truncate optimization, schema DDL permissions, transaction/savepoint auth strings, and view auth context names.
- DDL fixer tests for views/triggers/indexes referencing attached schemas, TEMP exemptions, host parameters in schema definitions, CTEs and `ON` clauses inside view definitions, and schema initialization behavior.
- CREATE TABLE tests covering existing table `IF NOT EXISTS`, TEMP qualification errors, reserved `sqlite_` names, shadow table protection, STRICT datatype enforcement, CTAS schema text generation, generated-column cycles/illegal expressions, and CHECK resolution failures.
- Primary-key and generated-column tests for INTEGER PRIMARY KEY, DESC primary key, duplicate primary keys, AUTOINCREMENT constraints, generated column primary-key rejection, WITHOUT ROWID conversion, and duplicate PK column pruning.
- Index tests for named and automatic indexes, duplicate automatic constraints with conflicting `ON CONFLICT`, expression and partial indexes, `NULLS FIRST/LAST` rejection, collation lookup failures, covering-index flags, WITHOUT ROWID suffix columns, CREATE INDEX schema rows, DROP INDEX restrictions, and REINDEX by database/table/index/collation.
- DROP TABLE/VIEW tests for protected system tables, shadow tables under defensive mode, eponymous virtual tables, wrong DROP TABLE vs DROP VIEW command, trigger cleanup, `sqlite_sequence` cleanup, statistics cleanup, virtual-table destroy, and auto-vacuum root-page movement.
- Foreign-key tests for inline and table-level FK definitions, mismatched column counts, unknown child columns, referenced-column storage, ON DELETE/ON UPDATE action flags, and deferred/immediate toggling.
- Source-list and CTE tests for FROM-list growth limits, JOIN type shifting including RIGHT JOIN `JT_LTORJ`, subquery attach/detach ownership, table-valued function args, INDEXED BY/NOT INDEXED flags, duplicate CTE names, and CTE cleanup.
- Collation/function registry tests for UTF-8/UTF-16 variants, collation-needed callbacks, fallback to alternate encodings, missing collation deactivating indexes through `sqlite3KeyInfoOfIndex()`, built-in preference during nested parse, and application function creation/overload resolution.
- DELETE tests for truncate optimization, row-by-row delete, WITHOUT ROWID composite PK deletes, one-pass single and multi deletes, virtual-table deletes, view deletes via INSTEAD OF triggers, `ORDER BY/LIMIT` rewrites, count-changes result rows, FK/trigger complexity, RETURNING interactions, and autoincrement end-state handling.

### subset-b-009029: lines 130125-137437

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 130125-137437

## Scope

This chunk spans the tail of SQLite's `delete.c`, the complete `func.c` section, the complete `fkey.c` section, and the beginning of `insert.c` through the first half of `sqlite3GenerateConstraintChecks()`. It is part of the amalgamated SQLite copy vendored under WiredTiger tests, so the visible units are static helpers and `SQLITE_PRIVATE`/`SQLITE_API` entry points used by other SQLite compiler/runtime sections in the same `sqlite3.c`.

## Purpose

The code in this span has three main responsibilities:

- Finish DELETE row code generation by deleting secondary-index entries, firing row triggers, and invoking foreign-key checks/actions.
- Define and register many built-in SQL scalar, aggregate, window-capable aggregate, LIKE/GLOB, diagnostic, and optional math functions.
- Generate VDBE bytecode for foreign-key validation/actions and for the front half of INSERT processing, including input source setup, row register assembly, trigger execution, rowid/autoincrement handling, foreign-key checks, and initial constraint/unique-conflict code.

The code is compiler-oriented: most routines do not directly mutate btrees at C runtime. Instead they append VDBE opcodes (`OP_Delete`, `OP_IdxDelete`, `OP_FkCounter`, `OP_NoConflict`, `OP_VUpdate`, `OP_NewRowid`, `OP_TypeCheck`, etc.) into `Parse->pVdbe`, which later executes the statement.

## Important APIs, Types, and Functions

### DELETE/index helper tail

- `sqlite3GenerateRowIndexDelete(Parse*, Table*, int iDataCur, int iIdxCur, int *aRegIdx, int iIdxNoSeek)` emits `OP_IdxDelete` for each non-primary secondary index that has an entry for the current table row. It skips indexes whose `aRegIdx[i]` is zero, the WITHOUT ROWID primary-key index, and the `iIdxNoSeek` optimization cursor. It uses `sqlite3GenerateIndexKey()` to build index records and resolves partial-index skip labels afterward.
- `sqlite3GenerateIndexKey(Parse*, Index*, int iDataCur, int regOut, int prefixOnly, int *piPartIdxLabel, Index *pPrior, int regPrior)` loads indexed columns or expressions from the data cursor into temporary registers, optionally emits `OP_MakeRecord`, handles partial-index predicates via `sqlite3ExprIfFalseDup()`, and avoids reloading shared columns from a prior index when safe.
- `sqlite3ResolvePartIdxLabel()` resolves the partial-index jump label returned by `sqlite3GenerateIndexKey()`.
- The visible tail of `sqlite3GenerateRowDelete()` populates `OLD.*` registers for triggers/FKs, runs BEFORE DELETE triggers, reseeks if triggers may have moved/deleted the row, calls `sqlite3FkCheck()`, deletes index/table entries, calls `sqlite3FkActions()` for cascade/set-null/set-default, and finally runs AFTER DELETE triggers.

### Built-in SQL functions

- Scalar function callbacks include `minmaxFunc`, `typeofFunc`, `subtypeFunc`, `lengthFunc`, `bytelengthFunc` (`octet_length`), `absFunc`, `instrFunc`, `printfFunc`/`format`, `substrFunc`/`substring`, `roundFunc`, `upperFunc`, `lowerFunc`, `randomFunc`, `randomBlob`, `last_insert_rowid`, `changes`, `total_changes`, `nullifFunc`, `versionFunc`, `sourceidFunc`, `errlogFunc`, `quoteFunc`, `unistrFunc`, `unicodeFunc`, `charFunc`, `hexFunc`, `unhexFunc`, `zeroblobFunc`, `replaceFunc`, `trimFunc`, `concatFunc`, `concatwsFunc`, `signFunc`, and optional `soundexFunc`, `loadExt`, math functions, and debug helpers.
- Pattern matching is implemented by `struct compareInfo`, `patternCompare()`, `sqlite3_strglob()`, `sqlite3_strlike()`, and `likeFunc()`. `sqlite3RegisterLikeFunctions()` installs case-sensitive or case-insensitive LIKE definitions, while `sqlite3IsLikeFunction()` exposes wildcard metadata for planner LIKE optimization.
- Aggregate/window state types include `SumCtx`, `CountCtx`, and `GroupConcatCtx`. Step/final/value/inverse callbacks implement `sum`, `total`, `avg`, `count`, `min`, `max`, `group_concat`, and `string_agg`.
- `sqlite3RegisterBuiltinFunctions()` builds the global `FuncDef aBuiltinFunc[]` array and registers regular, inline, deterministic, volatile, aggregate, LIKE, optional compile-option, optional extension-loading, optional math, debug, JSON/date/window/alter functions. `sqlite3RegisterPerConnectionBuiltinFunctions()` overloads `MATCH` per connection.

### Foreign-key code generation

- `sqlite3FkLocateIndex()` validates that a parent key maps to an INTEGER PRIMARY KEY or a UNIQUE/PRIMARY KEY index with matching columns and default collations. It returns an optional `Index*` and, for composite keys, an allocated child-column mapping.
- `fkLookupParent()` emits code for child-table changes (`I.1`/`D.1`): skip NULL child keys, search the parent table or index, and increment/decrement immediate or deferred FK counters or halt immediately for simple single-row immediate violations.
- `fkScanChildren()` emits a WHERE scan over child rows for parent-table changes (`I.2`/`D.2`), building expressions with parent-key affinity/collation and incrementing/decrementing FK counters for matches.
- `sqlite3FkCheck()` is the central INSERT/DELETE/UPDATE FK compiler. It loops over FKs where `pTab` is child and over FKs where `pTab` is parent, avoids unchanged UPDATE keys, honors disabled triggers/drop-table special cases, handles authorization `SQLITE_IGNORE`, and delegates to `fkLookupParent()`/`fkScanChildren()`.
- `sqlite3FkOldmask()` returns a bitmask of old-row columns needed for FK processing during UPDATE/DELETE.
- `sqlite3FkRequired()` tells UPDATE/DELETE code whether FK work is needed, returning `2` for cases that require stronger handling because parent actions or self-referential updates are involved.
- `fkActionTrigger()` synthesizes and caches internal `Trigger` objects that implement ON DELETE/ON UPDATE `CASCADE`, `SET NULL`, `SET DEFAULT`, and `RESTRICT`.
- `sqlite3FkActions()` invokes synthesized action triggers for affected parent rows.
- `sqlite3FkDropTable()`, `sqlite3FkClearTriggerCache()`, `fkTriggerDelete()`, and `sqlite3FkDelete()` handle drop-time FK checks, schema-change trigger-cache invalidation, and FK memory cleanup.

### INSERT and constraint code

- `sqlite3OpenTable()` emits read/write cursor opens for rowid tables or WITHOUT ROWID primary-key indexes and adds shared-cache table locks.
- `sqlite3IndexAffinityStr()`, `computeIndexAffStr()`, `sqlite3TableAffinityStr()`, and `sqlite3TableAffinity()` compute/apply index/table affinities or STRICT table `OP_TypeCheck`.
- `sqlite3ComputeGeneratedColumns()` computes generated column values, tracking loops among generated expressions and respecting virtual/stored column behavior.
- AUTOINCREMENT helpers `autoIncBegin()`, `sqlite3AutoincrementBegin()`, `autoIncStep()`, `autoIncrementEnd()`, and `sqlite3AutoincrementEnd()` read/update `sqlite_sequence` state through VDBE code.
- `sqlite3MultiValues()` optimizes multi-row `VALUES` input with a coroutine when safe, otherwise falls back to `UNION ALL`.
- `sqlite3Insert()` is the main INSERT compiler. It resolves the target, authorization, views/triggers, xfer optimization, autoincrement state, column-list mapping, SELECT/VALUES/default sources, temp-table materialization when the SELECT reads the destination, cursor opens, UPSERT target analysis, row register assembly, BEFORE/AFTER trigger calls, rowid generation, generated columns, virtual-table `OP_VUpdate`, ordinary-table constraints/FKs/insertion, row counting, and cleanup.
- `sqlite3ExprReferencesUpdatedColumn()` and its walker callback determine whether CHECK constraints or expression indexes reference columns changed by an UPDATE.
- `IndexIterator`/`IndexListTerm` allow `sqlite3GenerateConstraintChecks()` to visit indexes in UPSERT clause order instead of raw `Table.pIndex` order.
- The visible part of `sqlite3GenerateConstraintChecks()` handles NOT NULL constraints, CHECK constraints, table record generation, index ordering/UPSERT override selection, replace-trigger recheck setup, rowid uniqueness checks, index record generation, UNIQUE/PRIMARY KEY conflict detection, and conflict actions (`ROLLBACK`, `ABORT`, `FAIL`, `IGNORE`, `REPLACE`, `UPDATE`).

## Control Flow

DELETE code generation first materializes old-row registers only when triggers or FKs need them. BEFORE triggers may invalidate the cursor position, so the code reseeks and disables the `iIdxNoSeek` optimization before FK checks and physical deletes. It deletes secondary indexes before the table row, then runs FK actions and AFTER triggers.

Built-in functions follow the SQLite callback contract: read arguments with `sqlite3_value_*`, allocate through SQLite allocators or aggregate contexts, report via `sqlite3_result_*`, and signal OOM/toobig/errors on the context. Registration is centralized in `sqlite3RegisterBuiltinFunctions()` so parser/function lookup later sees a uniform `FuncDef` table.

FK checking has two mirrored flows. For child-row insert/delete/update, it searches for the parent key and adjusts counters if the parent is absent. For parent-row insert/delete/update, it scans matching child rows and adjusts counters. UPDATEs call the same machinery twice, once as a deletion of old values and once as an insertion of new values, and helper predicates skip FKs whose key columns are unchanged.

INSERT compilation chooses one of several templates. Single-row VALUES compiles straight-line expression code. INSERT FROM SELECT either yields rows directly from a coroutine or spools them into an ephemeral table when the SELECT also reads the destination or triggers require isolation. After each source row is mapped into storage-order registers, the compiler runs BEFORE triggers, computes rowids and generated columns, checks constraints/FKs, emits the insertion, increments row counts, and loops or cleans up.

Constraint checks are layered. NOT NULL and CHECK constraints run before UNIQUE probing. For rowid tables with an explicit rowid/IPK, `OP_NotExists` checks the table btree. For indexes and WITHOUT ROWID primary keys, index records are assembled in `aRegIdx[]` registers, partial indexes may skip via their WHERE predicate, and `OP_NoConflict` probes uniqueness. Conflict handling may call UPSERT update code, jump to ignore, halt with constraint errors, or delete conflicting rows for REPLACE.

## State and Persistence Behavior

- Persistent database state changes are represented as VDBE bytecode, not direct C writes in this chunk. Table/index btree modifications later occur through opcodes such as `OP_Delete`, `OP_IdxDelete`, `OP_Insert`, `OP_VUpdate`, `OP_FkCounter`, and generated trigger subprograms.
- FK deferred state is tracked by counters: connection-level counters for deferred constraints and statement-level counters for immediate constraints. `OP_FkCounter` and `OP_FkIfZero` maintain and test this state.
- AUTOINCREMENT persistence uses `AutoincInfo` structures during compilation and emits reads/writes against `sqlite_sequence` at statement start/end.
- Built-in aggregate state persists per aggregate invocation in `sqlite3_aggregate_context()`. `SumCtx` tracks integer vs approximate Kahan-Babuska-Neumaier accumulation and overflow; `GroupConcatCtx` owns a `StrAccum` plus separator-length tracking for window inverse support; `CountCtx` tracks count and debug inverse use.
- FK action triggers are cached on `FKey.apTrigger[2]` and invalidated on schema changes or freed with the FK/table. They are heap objects that mimic real triggers but are generated internally.
- Function registration mutates global/per-connection function hash tables. Many callbacks are pure for a single invocation, but volatile functions (`random`, `randomblob`, `changes`, `last_insert_rowid`, `total_changes`) depend on connection/runtime state.

## Dependencies and Integration Points

- Heavy dependence on SQLite internals: `Parse`, `Vdbe`, `VdbeOp`, `Table`, `Column`, `Index`, `FKey`, `Trigger`, `TriggerStep`, `Expr`, `ExprList`, `Select`, `SrcList`, `NameContext`, `WhereInfo`, `FuncDef`, `sqlite3_value`, `sqlite3_context`, `StrAccum`, and memory helpers.
- VDBE opcode integration is central: the compiler emits opcodes through `sqlite3VdbeAddOp*`, labels through `sqlite3VdbeMakeLabel()`/`sqlite3VdbeResolveLabel()`, P4 payloads such as `P4_TABLE`, `P4_COLLSEQ`, `P4_VTAB`, and coverage/test macros.
- The query planner is used by FK parent scans through `sqlite3WhereBegin()`/`sqlite3WhereEnd()`.
- Triggers integrate through `sqlite3CodeRowTrigger()`, `sqlite3CodeRowTriggerDirect()`, `sqlite3TriggersExist()`, and trigger-program cursor locking during REPLACE-on-UPDATE.
- UPSERT integrates through `sqlite3UpsertAnalyzeTarget()`, `sqlite3UpsertOfIndex()`, and `sqlite3UpsertDoUpdate()`.
- Virtual tables integrate through `sqlite3GetVTable()`, `sqlite3VtabMakeWritable()`, and `OP_VUpdate`; UPSERT is explicitly rejected for virtual tables in this span.
- Optional compile-time features shape the compiled surface: `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_FOREIGN_KEY`, `SQLITE_OMIT_LOAD_EXTENSION`, `SQLITE_SOUNDEX`, `SQLITE_ENABLE_MATH_FUNCTIONS`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_UNKNOWN_SQL_FUNCTION`, `SQLITE_DEBUG`, and others.

## Risks and Edge Cases

- Register layout is fragile. Many routines rely on row registers being `rowid, col0, col1, ...` with storage-order remapping via `sqlite3TableColumnToStorage()`. Generated/hidden/virtual columns and BEFORE triggers make this especially sensitive.
- Partial-index code must resolve labels after index-key generation. Incorrect label handling could skip deletes or uniqueness checks.
- `sqlite3GenerateIndexKey()` deliberately drops `OP_RealAffinity` before rebuilding index keys. Changes here could corrupt index representation for REAL-affinity columns stored compactly as integers.
- `patternCompare()` can be O(N^2) and recursive for wildcard-heavy LIKE/GLOB patterns; `likeFunc()` mitigates via `SQLITE_LIMIT_LIKE_PATTERN_LENGTH`.
- Text/blob functions frequently rely on `sqlite3_value_text()` followed by `sqlite3_value_bytes()` without invalidating pointers. Assertions document assumptions, but encoding conversions and OOM paths are critical.
- `absFunc()` handles `SMALLEST_INT64` as an overflow error; random integer generation masks that same impossible absolute-value case.
- `replaceFunc()`, `concatFuncCore()`, `quoteFunc()`, and aggregate accumulation must respect `SQLITE_LIMIT_LENGTH` and propagate OOM/toobig through result contexts.
- FK mismatch detection depends on parent-key uniqueness, column count, and default collation. Accepting an expression or partial index for FK enforcement would be invalid and is deliberately rejected.
- Drop-table FK handling disables triggers but keeps FK actions active; schema changes cannot be rolled back by statement transactions, so immediate FK violations must be detected before schema mutation.
- Internal FK action triggers are cached and must be cleared on schema change to avoid stale expression/table metadata.
- REPLACE conflict handling can fire delete triggers or FK actions, requiring uniqueness rechecks after triggers because side effects may create new conflicts. The visible code sets up `regTrigCnt`, `addrRecheck`, and `lblRecheckOk` for that later second pass.
- UPSERT ordering is non-trivial: IPK conflicts may be delayed behind targeted ON CONFLICT clauses, and duplicate conflict targets are ignored in the custom index iterator.
- WITHOUT ROWID tables share primary-key cursor semantics with index cursors; REPLACE optimization can skip explicit conflict detection only under narrow conditions and not with pre-update hooks.

## Test Signals

- Existing instrumentation uses `assert()`, `testcase()`, `VdbeCoverage()`, `VdbeCoverageIf()`, `VdbeModuleComment()`, and `VdbeNoopComment()` heavily. These are strong signals that SQLite's TH3/TCL test suites exercise branch coverage and opcode paths.
- Comments reference specific evidence/test requirements, including API behavior requirements (`IMP:`/`EVIDENCE-OF:`) and `TH3 withoutrowid04.test` for WITHOUT ROWID update conflict handling.
- Important behavior to validate around this span includes DELETE with BEFORE/AFTER triggers and FK actions, partial-index delete/update, generated column INSERT, STRICT table type checks, AUTOINCREMENT sequence updates, INSERT SELECT self-read temp-table materialization, UPSERT target ordering, REPLACE with recursive triggers/FKs, deferred vs immediate FK counters, LIKE/GLOB escape and pattern-length failures, aggregate window inverse behavior, and scalar edge cases such as `abs(-9223372036854775808)`, malformed `unistr()`, invalid `unhex()`, and length/encoding conversions.

## Chunk Boundary Notes

- The chunk begins in the middle of `sqlite3GenerateRowDelete()` and therefore inherits setup from previous lines, including cursor/opening assumptions and `iPk`/`nPk`/`opSeek` initialization.
- The chunk ends in the middle of `sqlite3GenerateConstraintChecks()`, immediately after generating REPLACE conflict logic for UNIQUE indexes and before the later recheck/finalization portions of that routine. The later chunk should verify how `addrRecheck`, `lblRecheckOk`, `seenReplace`, `pbMayReplace`, generated table records, and `aRegIdx[]` outputs are finalized.

### subset-b-009030: lines 137438-144608

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 137438-144608

## Chunk Scope

This chunk spans several logical SQLite amalgamation modules:

- The end of `insert.c`: final constraint recheck logic, `sqlite3CompleteInsertion()`, table/index cursor opening, and the `INSERT INTO ... SELECT * FROM ...` transfer optimization.
- `legacy.c`: the public `sqlite3_exec()` convenience wrapper.
- `loadext.c` plus embedded `sqlite3ext.h`: extension API dispatch table, dynamic extension loading, per-connection extension handle cleanup, load-extension enable flags, and global auto-extension registration/loading.
- The start and most of `pragma.c`: generated pragma metadata, helpers, `sqlite3Pragma()` dispatch, integrity checking code generation, pragma virtual table support, and `sqlite3PragmaVtabRegister()`.
- The start of `prepare.c`: schema initialization callback/loader, schema-cookie validation, parse object cleanup helpers, and the first part of `sqlite3Prepare()`/`sqlite3LockAndPrepare()`.

The source is third-party SQLite embedded under WiredTiger tests, so the code is vendor infrastructure rather than repository-native storage engine logic. Its integration surface is the SQLite C API and SQLite's internal VDBE, btree, schema, parser, pager, pragma, extension, and virtual table subsystems.

## Purpose

The chunk implements core database connection behavior around writes, execution, extension loading, pragmas, schema loading, and SQL preparation:

- Finish row insertion/update by emitting VDBE opcodes that insert index records and table records.
- Detect and fast-path compatible bulk table copies for `INSERT INTO dst SELECT * FROM src`.
- Provide `sqlite3_exec()` as a high-level loop over prepare/step/finalize for one or more SQL statements.
- Expose a stable ABI table for loadable SQLite extensions and manage loaded extension handles.
- Maintain process-wide auto-extension callbacks and invoke them for new database connections.
- Parse and compile PRAGMA statements into VDBE programs, including settings, schema introspection, integrity checks, WAL/checkpoint controls, heap/worker limits, and `PRAGMA optimize`.
- Represent PRAGMAs as eponymous virtual tables for queryable `pragma_*` table names.
- Load sqlite schema rows into internal `Table`, `Index`, `Trigger`, and `View` structures and start compiling SQL into VDBE statements.

## Important APIs, Types, and Functions

- `sqlite3CompleteInsertion()` at line 137593 emits final `OP_IdxInsert` and `OP_Insert` opcodes after constraint checks. It depends on `Table`, `Index`, index register array `aRegIdx`, cursor numbers, `OPFLAG_*` write flags, and preupdate hook support for WITHOUT ROWID tables.
- `sqlite3OpenTableAndIndices()` at line 137681 allocates/open cursors for a table and its indexes. It returns data and first-index cursor ids and treats rowid, WITHOUT ROWID, and virtual tables differently.
- `xferCompatibleIndex()` at line 137762 compares source/destination index metadata for transfer optimization compatibility: key/count shape, conflict behavior, columns or expressions, sort order, collation, and partial-index WHERE clause.
- `xferOptimization()` at line 137823 implements the raw-record transfer fast path for `INSERT INTO tab1 SELECT * FROM tab2`. It performs extensive syntax and schema compatibility checks, then emits VDBE copy loops for table and index btrees.
- `sqlite3_exec()` at line 138237 is the public convenience API that repeatedly calls `sqlite3_prepare_v2()`, `sqlite3_step()`, user callbacks, and `sqlite3VdbeFinalize()`.
- `struct sqlite3_api_routines` begins in the embedded extension header and is the loadable-extension ABI. New function pointers are appended to preserve binary compatibility.
- `sqlite3Apis` at line 139271 is the concrete static dispatch table passed into extensions. Compile-time omissions replace unavailable APIs with null pointers.
- `sqlite3LoadExtension()` at line 139623 opens a shared library through the VFS, finds an init symbol, calls it with `sqlite3Apis`, and appends the handle to `db->aExtension`.
- `sqlite3_load_extension()` at line 139784 is the public mutex-wrapped API for dynamic loading.
- `sqlite3CloseExtensions()` at line 139802 closes all dynamic-library handles owned by a database connection during connection close.
- `sqlite3_enable_load_extension()` at line 139815 toggles the connection flags `SQLITE_LoadExtension` and `SQLITE_LoadExtFunc`.
- `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, `sqlite3_reset_auto_extension()`, and `sqlite3AutoLoadExtensions()` at lines 139864, 139914, 139942, and 139964 maintain and run a process-wide list of extension init callbacks protected by `SQLITE_MUTEX_STATIC_MAIN`.
- `PragmaName`, `pragCName[]`, and `aPragmaName[]` define the generated pragma lookup table and result column metadata.
- `sqlite3GetBoolean()` at line 140929 is a shared helper for boolean-like pragma values.
- `setPragmaResultColumnNames()`, `returnSingleInt()`, and `returnSingleText()` generate standard PRAGMA result metadata/rows.
- `sqlite3JournalModename()` and `pragmaLocate()` support journal-mode name mapping and binary search over the lexicographically sorted pragma table.
- `pragmaFunclistLine()` formats `PRAGMA function_list` output for built-in and connection-defined SQL functions.
- `integrityCheckResultRow()` is a VDBE codegen helper for integrity-check result emission and max-error limiting.
- `sqlite3Pragma()` at line 141077 is the central PRAGMA compiler. It normalizes schema/name/value tokens, calls authorization and VFS file-control hooks, resolves the pragma entry, optionally loads schema, then dispatches by `PragTyp_*`.
- `PragmaVtab` and `PragmaVtabCursor` model eponymous virtual tables that execute PRAGMA statements underneath.
- `pragmaVtabConnect()`, `pragmaVtabBestIndex()`, `pragmaVtabFilter()`, `pragmaVtabNext()`, `pragmaVtabColumn()`, and `sqlite3PragmaVtabRegister()` at lines 143453-143731 implement the virtual table facade over PRAGMAs.
- `corruptSchema()`, `sqlite3IndexHasDuplicateRootPage()`, `sqlite3InitCallback()`, `sqlite3InitOne()`, `sqlite3Init()`, and `sqlite3ReadSchema()` at lines 143761-144217 build and validate in-memory schema state from `sqlite_schema`.
- `schemaIsValid()` compares stored schema cookies with btree metadata and resets stale schemas.
- `sqlite3SchemaToIndex()` maps a `Schema *` back to `db->aDb[]`.
- `sqlite3ParseObjectReset()`, `sqlite3ParserAddCleanup()`, and `sqlite3ParseObjectInit()` manage parser-lifetime allocations and cleanup hooks.
- `sqlite3Prepare()` at line 144427 is the internal compiler entry point; this chunk includes setup, schema-lock checks, parser invocation, error handling, and parser cleanup.
- `sqlite3LockAndPrepare()` starts at line 144590 and wraps prepare under the connection mutex and all btree mutexes, retrying transient prepare errors.

## Control Flow

### Insert Completion and Transfer Optimization

The chunk begins in the tail of constraint checking. It copies previously emitted uniqueness-check opcodes to recheck constraints after `REPLACE` triggers, bypasses partial indexes when their predicate register is null, and emits aborts if a replacement trigger caused a new uniqueness violation. It then optionally generates a row record with `OP_MakeRecord` for rowid tables and sets null-trim metadata through `sqlite3SetMakeRecordP5()` when enabled.

`sqlite3CompleteInsertion()` assumes constraint checks and index key generation already happened. It loops over `pTab->pIndex`, skips unused index registers, bypasses partial indexes via `OP_IsNull`, sets `OPFLAG_USESEEKRESULT` when allowed, and adds `OP_IdxInsert`. For a WITHOUT ROWID primary key it adds change-count/save-position flags and may call `codeWithoutRowidPreupdate()` for INSERT preupdate hook delivery. Rowid tables finish with one `OP_Insert` into `iDataCur`, using flags for nested writes, change counting, last-rowid tracking, append bias, and seek-result reuse.

`sqlite3OpenTableAndIndices()` centralizes cursor allocation. Virtual tables are a no-op and output illegal cursor numbers for detection. Rowid tables open the base table first and then all indexes. WITHOUT ROWID tables treat the primary key index as the canonical data cursor. If shared cache is enabled and a rowid table is not opened, the function still emits table locks.

`xferOptimization()` first rejects unsupported SELECT shapes: CTEs, multiple FROM entries, subqueries, WHERE/ORDER/GROUP/LIMIT/compound/DISTINCT, and anything other than a single `*` result expression. It then checks schema compatibility for rowid mode, ordinary-table status, column count, INTEGER PRIMARY KEY, STRICTness, hidden/generated columns, affinity, collation, NOT NULL strength, defaults, indexes, CHECK constraints, foreign keys, and `count_changes`. If accepted, it emits VDBE loops that copy raw table records or index records from source btrees to destination btrees, using faster `OP_RowCell`, `OP_SeekEnd`, `OPFLAG_PREFORMAT`, and `OPFLAG_APPEND` paths under VACUUM or sorted binary-collation cases. When safety requires an initially empty destination, it emits a runtime emptiness test and returns false so the caller can also compile the ordinary insertion fallback.

### `sqlite3_exec()`

`sqlite3_exec()` validates the database handle, converts null SQL to an empty string, takes `db->mutex`, clears prior error state, and loops until the SQL string is exhausted. Each statement is prepared with `sqlite3_prepare_v2()`. Whitespace/comment-only fragments advance to the returned tail. For real statements it steps until completion, lazily allocates `azCols` as a `2*nCol+1` array, stores column names in the first half and row text values in the second half, and calls the user callback for each row. If `SQLITE_NullCallback` is set and a statement returns no rows, it can invoke the callback once with column names but no values. Non-zero callback return aborts execution with `SQLITE_ABORT`. On exit it finalizes any active statement, frees callback column storage, maps the result through `sqlite3ApiExit()`, and optionally returns an allocated error string.

### Extension Loading

The embedded `sqlite3ext.h` section defines the ABI surface extensions use. The core build disables API macro redirection with `SQLITE_CORE`, while loadable extension builds map public names to `sqlite3_api->...`.

`sqlite3LoadExtension()` requires `SQLITE_LoadExtension` on the connection, rejects oversized and empty filenames, and opens the library via `sqlite3OsDlOpen()`. On Unix/Windows it retries with platform suffixes when the exact file name fails. It resolves the requested entry point or defaults to `sqlite3_extension_init`; if that default is absent, it derives `sqlite3_X_init` from the filename by dropping directory, optional `lib`, and suffix, lowercasing ASCII letters. It calls the entry point as `xInit(db, &zErrmsg, &sqlite3Apis)`. `SQLITE_OK_LOAD_PERMANENTLY` means success without retaining the handle. Other init failures close the handle. Successful loads append the handle to `db->aExtension`, replacing the old handle array.

Auto-extension registration uses the global `sqlite3Autoext` state vector, or an indirection macro when writable static data is omitted. Registration initializes SQLite, takes the static main mutex, deduplicates callbacks, and appends via `sqlite3_realloc64()`. Cancellation removes a matching callback by swapping with the last element. Reset frees the whole array. `sqlite3AutoLoadExtensions()` reads one callback at a time under the static mutex, releases the mutex while calling extension code, and stops on an error after storing a connection error message.

### PRAGMA Dispatch

The generated pragma table maps names to `PragTyp_*`, flags, result-column metadata, and type-specific arguments. `sqlite3Pragma()` compiles a PRAGMA into VDBE bytecode:

1. It creates a VDBE with `sqlite3GetVdbe()`, marks it run-once, parses optional schema qualification, opens temp schema if explicitly requested, and materializes left/right token strings.
2. It checks authorization with `SQLITE_PRAGMA`.
3. It gives the VFS first chance through `SQLITE_FCNTL_PRAGMA`; a successful VFS response becomes a one-column result, non-`SQLITE_NOTFOUND` errors become parse errors.
4. It binary-searches `aPragmaName[]`, optionally reads schema, and sets result column names unless the pragma suppresses columns.
5. It switches on the pragma type and emits code or directly mutates connection fields.

The included cases cover pager settings (`page_size`, `cache_size`, `cache_spill`, `mmap_size`, `secure_delete`, `journal_mode`, `journal_size_limit`, `locking_mode`, `synchronous`), vacuum/autovacuum controls, temp/data directory state, boolean connection flags, schema introspection (`table_info`, `table_list`, `index_info`, `index_list`, `database_list`, `collation_list`, `function_list`, `module_list`, `pragma_list`), foreign key introspection/checking, `case_sensitive_like`, integrity/quick checks, encoding, header cookies, compile options, WAL checkpoint/autocheckpoint, heap limits, worker thread limit, `analysis_limit`, debug lock status, and `PRAGMA optimize`.

`PRAGMA integrity_check` and `quick_check` generate one of the densest VDBE programs in this chunk. They collect btree root pages, run `OP_IntegrityCk`, compare table/index entry counts, verify WITHOUT ROWID primary key order, validate column storage classes and NOT NULL rules, evaluate CHECK constraints, verify index entries and UNIQUE keys, and invoke virtual-table `xIntegrity` for module version 4 tables. Quick check skips the more expensive index validation paths.

`PRAGMA optimize` scans eligible ordinary user tables, checks whether stats were used or missing, compares current table size against `sqlite_stat1` estimates, and emits either debug rows or `OP_SqlExec` ANALYZE statements. It bounds analysis work with `SQLITE_DEFAULT_OPTIMIZE_LIMIT` and scales the limit down for schemas with many btrees.

### PRAGMA Virtual Tables

`sqlite3PragmaVtabRegister()` recognizes `pragma_<name>` module names for pragmas that have queryable result forms. `pragmaVtabConnect()` declares a virtual table schema from the pragma's result columns plus hidden `arg` and/or `schema` columns. `pragmaVtabBestIndex()` encourages equality constraints on hidden parameters by assigning very high cost when the required first hidden argument is unconstrained. `pragmaVtabFilter()` builds a safe quoted PRAGMA SQL string from hidden arguments, prepares it, and advances to the first row. Columns before `iHidden` proxy `sqlite3_column_value()` from the prepared PRAGMA; hidden columns return captured argument text.

### Schema Loading and Prepare

`sqlite3InitCallback()` is the callback used by schema initialization. For CREATE statements from `sqlite_schema`, it runs `sqlite3Prepare()` while `db->init.busy` is set so parsing creates in-memory schema objects without executable VDBE output. For implicit indexes with blank SQL text, it finds the existing index and records its root page. `corruptSchema()` centralizes error text and respects malloc failure, ALTER TABLE context, `SQLITE_WriteSchema`, and extra schema checks.

`sqlite3InitOne()` creates the in-memory schema table definition, opens a read transaction if needed, reads btree metadata, sets schema cookie, encoding, cache size, file format, and legacy file-format flags, then executes `SELECT*FROM"<db>".sqlite_schema ORDER BY rowid` through `sqlite3_exec()` with `sqlite3InitCallback()`. It loads ANALYZE statistics on success and marks `DB_SchemaLoaded` when acceptable, including the special `SQLITE_NoSchemaError` path used to inspect corrupt schema tables.

`sqlite3Init()` loads main first, then attached schemas in reverse order with temp last, and commits internal schema changes when appropriate. `sqlite3ReadSchema()` is the parser-facing no-op-or-load wrapper. `schemaIsValid()` opens temporary read transactions if needed, compares btree schema cookies to in-memory schema cookies, resets stale schemas, and sets `SQLITE_SCHEMA`.

`sqlite3Prepare()` initializes a stack `Parse`, optionally disables lookaside for persistent statements, checks shared-cache schema locks across btrees, unlocks pending virtual-table disconnects, copies unterminated SQL when a byte count is provided, runs the parser, stores statement SQL text, finalizes failed VDBEs, transfers the compiled VDBE to `*ppStmt` on success, deletes trigger-program allocations, and resets parser-owned cleanup state. `sqlite3LockAndPrepare()` begins the public-facing lock wrapper, taking the database mutex and all btree mutexes and retrying through `sqlite3Prepare()`.

## State and Persistence Behavior

- Table and index writes are persisted through VDBE btree opcodes (`OP_Insert`, `OP_IdxInsert`) emitted by insert codegen, not directly by these C functions.
- Transfer optimization copies raw btree cells/records and can update autoincrement state with `autoIncBegin()` and `autoIncStep()`. It emits an `sqlite3AutoincrementEnd()` call path when an empty-destination fallback is needed.
- PRAGMA handlers modify a mix of in-memory connection state and persistent database header cookies. Persistent examples include default cache size, autovacuum metadata, and header values such as schema/user/application ids. In-memory examples include `db->temp_store`, `db->flags`, `db->busyTimeout`, `db->nAnalysisLimit`, `db->dfltLockMode`, mmap limit, heap limits, and WAL autocheckpoint callbacks.
- Dynamic extension handles persist for the lifetime of a connection in `db->aExtension` and are closed by `sqlite3CloseExtensions()`.
- Auto-extension callbacks are process-global mutable state in `sqlite3Autoext`, guarded by the static main mutex.
- Schema initialization persists no new database content during normal reads, but builds in-memory schema state and may load stats. It uses btree metadata to set `Schema` fields and schema loaded flags.
- `sqlite3_exec()` owns temporary callback arrays and error message allocations. Returned error strings are allocated outside the connection db allocator (`sqlite3DbStrDup(0, ...)`) for caller ownership.
- Parser cleanup state is explicit through `ParseCleanup` links and is guaranteed to run in `sqlite3ParseObjectReset()`, including immediate cleanup on allocation failure in `sqlite3ParserAddCleanup()`.

## Dependencies and Integration Points

- VDBE opcode generation is pervasive: `sqlite3VdbeAddOp*`, labels, P4 payloads, `VdbeCoverage`, result rows, `OP_SqlExec`, `OP_Checkpoint`, `OP_IntegrityCk`, and many cursor operations.
- Btree/pager integration includes table/index opens, schema metadata reads/writes, transactions, page size, auto-vacuum, cache, mmap, locking, journaling, WAL, and secure-delete controls.
- Parser integration includes `Parse`, token/name conversion, schema reads, authorization, self-table expression codegen, and statement preparation.
- Extension loading depends on VFS dynamic-link methods (`sqlite3OsDlOpen`, `sqlite3OsDlSym`, `sqlite3OsDlError`, `sqlite3OsDlClose`) and ABI stability of `sqlite3_api_routines`.
- Virtual table integration appears both in extension/module APIs and in PRAGMA virtual table support, including `sqlite3_declare_vtab`, `sqlite3VtabCreateModule`, and virtual table integrity callbacks.
- Shared-cache and mutex behavior is central: connection mutexes, btree mutexes, schema locks, tempdir mutex, and static main mutex protect different state classes.
- Compile-time feature flags heavily alter behavior and ABI slots, including `SQLITE_OMIT_*`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_ENABLE_CEROD`, `SQLITE_DEBUG`, and platform macros.
- WiredTiger integration is indirect: this file provides the bundled SQLite implementation used by test third-party code, so behavioral changes here can affect any tests or helper tools using SQLite APIs.

## Risks and Edge Cases

- Insert REPLACE recheck logic copies existing VDBE opcodes after possible opcode-array reallocations; the code explicitly copies whole `VdbeOp` values to avoid dangling pointers. Any edit here risks constraint enforcement regressions.
- `sqlite3CompleteInsertion()` relies on the caller's `aRegIdx` layout and assumes all REPLACE indexes are ordered at the end of `pTab->pIndex`. Violating those invariants could corrupt index writes or change conflict behavior.
- Transfer optimization is intentionally conservative. Relaxing compatibility checks can silently bypass column decoding, generated-column omission semantics, triggers, FK behavior, uniqueness checks, or rowid remapping requirements.
- The transfer path has separate VACUUM and non-VACUUM behavior. `OPFLAG_PREFORMAT`, `OP_RowCell`, and `OP_SeekEnd` are only safe when the source cell format/order assumptions hold.
- `sqlite3_exec()` callbacks receive pointers into statement-owned memory and column-name storage. Finalization invalidates those pointers. Callback abort and OOM paths must finalize exactly once and free `azCols`.
- Extension loading is security-sensitive. Loading is disabled by default, empty filenames are rejected, path length is bounded to avoid `dlopen()` crashes, and fallback entry point derivation must not overflow.
- `sqlite3Apis` order is ABI-critical. New extension APIs must be appended, never inserted, and omitted features must leave compatible null slots.
- Auto-extension callbacks are global and run outside the static mutex. This avoids deadlocks but means registration/cancellation can race with iteration in controlled ways; the loop rereads under mutex each iteration.
- PRAGMA handlers mix direct connection mutation and deferred VDBE effects. Transaction restrictions, defensive mode restrictions, schema reloads, and `OP_Expire` invalidation are important for correctness.
- `PRAGMA temp_store_directory` and `data_store_directory` mutate global directory pointers under a static mutex and are disabled under `SQLITE_OMIT_WSD`; they can invalidate temp storage and reset schemas.
- Integrity-check code has many generated jumps and temp registers. Type-check masks, virtual/generated columns, default handling, STRICT semantics, and WITHOUT ROWID primary-key order are easy regression points.
- Schema loading parses SQL from `sqlite_schema` while `db->init.busy` changes parser behavior. Corrupt schema handling varies under `SQLITE_WriteSchema`, ALTER TABLE contexts, and `SQLITE_NoSchemaError`.
- `sqlite3Prepare()` must reset parser state on every exit. Early cleanup on OOM is deliberate to avoid leaked parser-owned objects but creates use-after-free risk if callers keep using a cleaned pointer.

## Test Signals

Useful test coverage for this chunk includes:

- INSERT/UPDATE tests covering rowid and WITHOUT ROWID tables, partial indexes, UNIQUE conflicts, `ON CONFLICT REPLACE`, triggers that perform replacement, generated columns, STRICT tables, preupdate hooks, and `last_insert_rowid`/change-count behavior.
- Transfer optimization tests using `sqlite3_xferopt_count` under `SQLITE_TEST`, including accepted simple copies, fallback when destination is non-empty, and rejection for mismatched indexes, collations, defaults, generated expressions, CHECK constraints, FKs, STRICTness, hidden columns, CTEs, WHERE/ORDER/GROUP/LIMIT/DISTINCT, and virtual tables.
- `sqlite3_exec()` tests for multi-statement SQL, whitespace/comment tails, row callbacks, empty-result callbacks, callback abort, OOM in callback column allocation, prepare errors, step errors, and returned error message ownership.
- Extension tests for disabled loading, enabling/disabling C API and SQL-function loading, suffix fallback, alternate entry point derivation, init failure cleanup, permanent extensions, close-time handle cleanup, and omitted API null slots.
- Auto-extension tests for deduplication, cancellation, reset, initialization failure propagation, and thread-safety under concurrent registration/loading.
- PRAGMA tests for every table entry in `aPragmaName[]`, unknown pragma no-op behavior, VFS `SQLITE_FCNTL_PRAGMA` override behavior, authorization denial, schema-qualified forms, result column names, and `PragFlg_NoColumns1` debug assertions.
- Pager/state PRAGMA tests for transaction restrictions, defensive-mode restrictions, persistence of header cookies, WAL checkpoint modes, mmap limits, temp store invalidation, lock status, heap limits, worker thread limits, and statement expiration after flag changes.
- Integrity-check tests with corrupt btrees, missing index entries, wrong index counts, duplicate UNIQUE entries, rowid encoding errors, non-BINARY collation mismatch, STRICT type violations, NOT NULL/NaN handling, CHECK failures, WITHOUT ROWID order violations, quick-check omissions, and virtual-table `xIntegrity`.
- Schema loading/prepare tests for malformed `sqlite_schema`, orphan indexes/triggers, duplicate index root pages, invalid root pages with extra checks, encoding mismatch on ATTACH, schema cookie mismatch, shared-cache schema lock failures, SQL length limit, persistent prepare lookaside disabling, retry-on-`SQLITE_ERROR_RETRY`, and parser cleanup under OOM fault injection.

## Cross-Chunk Notes

- The line range starts in the middle of the function that generated constraint checks before insertion; earlier setup for registers, conflict policy, and labels is outside this chunk.
- `sqlite3LockAndPrepare()` continues beyond line 144608, so retry completion, btree leave/unlock behavior, and public prepare wrappers are covered by later chunks.
- Many PRAGMA cases depend on helper functions and VDBE opcodes defined elsewhere in the amalgamation; this chunk contains their dispatch and code generation, not the lower-level pager/btree implementations.

### subset-b-009031: lines 144609-151744

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 144609-151744

## Purpose

This chunk spans the end of SQLite statement preparation and the opening, substantial portion of `select.c` in the vendored SQLite amalgamation used by WiredTiger tests. It is the transition from public `sqlite3_prepare*()` entry points into SELECT parsing, expansion, flattening, compound-query planning, result metadata generation, and the first aggregate-codegen helpers.

The code covers:

- Repreparing statements after schema changes and UTF-8/UTF-16 `sqlite3_prepare*()` wrappers.
- Core `Select`, `SortCtx`, `DistinctCtx`, `RowLoadInfo`, `SubstContext`, and `WhereConst` helper state.
- SELECT object construction/destruction, destination initialization, column-name/type derivation, wildcard expansion, CTE resolution, view/subquery expansion, join normalization, and result-set table synthesis.
- VDBE code generation for SELECT inner loops, DISTINCT, ORDER BY/GROUP BY sorters, LIMIT/OFFSET, recursive CTE queues, compound SELECTs, and merge-based compound ORDER BY.
- Optimizations for subquery flattening, WHERE push-down, constant propagation, unused subquery result columns, min/max aggregate short-cuts, simple `count(*)`, sorter references, indexed aggregate expressions, and aggregate ORDER BY/DISTINCT setup.

## Important APIs, Types, and Functions

- `sqlite3Reprepare()` recompiles a saved-SQL VDBE after schema invalidation by calling `sqlite3LockAndPrepare()`, swapping the new VDBE into the old object, transferring bindings, and finalizing the temporary VDBE.
- Public prepare wrappers include `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, and, when UTF-16 support is enabled, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, and `sqlite3_prepare16_v3()`. The v2/v3 forms set `SQLITE_PREPARE_SAVESQL` so later `sqlite3_step()` can auto-reprepare.
- `sqlite3Prepare16()` converts UTF-16 SQL to UTF-8 under the database mutex, calls `sqlite3LockAndPrepare()`, and maps the returned UTF-8 tail pointer back to the original UTF-16 buffer by counting parsed characters.
- `DistinctCtx` carries DISTINCT strategy state: whether DISTINCT is active, the `WHERE_DISTINCT_*` strategy, the ephemeral cursor, and the delayed `OP_OpenEphemeral` address.
- `SortCtx` carries ORDER BY/GROUP BY sorter state: order list, satisfied prefix count, sorter cursor, block-output labels, sorter flags, deferred row-load data, optional sorter-reference cursors, and optional scan-status push ranges.
- `clearSelect()`, `sqlite3SelectNew()`, `sqlite3SelectDelete()`, and `sqlite3SelectDeleteGeneric()` allocate and tear down `Select` trees, including expression lists, source lists, WHERE/GROUP/HAVING/ORDER/LIMIT expressions, WITH clauses, window definitions, and compound `pPrior` chains.
- `sqlite3SelectDestInit()` initializes `SelectDest` output routing for result rows, transient tables, scalar subqueries, recursive queues, coroutines, and compound temporaries.
- `sqlite3JoinType()` parses permissive SQLite join keyword combinations into `JT_*` bitmasks, including RIGHT/FULL join support and compatibility with historical nonsensical join phrases.
- `sqlite3ColumnIndex()`, `sqlite3SrcItemColumnUsed()`, and `tableAndColumnIndex()` resolve column names in `Table`/`SrcList` objects and mark nested-FROM output columns as used.
- `sqlite3SetJoinExpr()` and `unsetJoinExpr()` annotate or remove `EP_OuterON`/`EP_InnerON` and `Expr.w.iJoin` metadata so WHERE processing knows which ON/USING expressions must be delayed for outer joins.
- `sqlite3ProcessJoin()` rewrites NATURAL joins into USING lists, validates USING columns, builds equality predicates, handles RIGHT/FULL join coalesce behavior for repeated USING names, and appends ON expressions to the SELECT WHERE clause with join-origin tags.
- `innerLoopLoadRow()`, `makeSorterRecord()`, `pushOntoSorter()`, `codeOffset()`, `codeDistinct()`, `fixDistinctOpenEph()`, and optional `selectExprDefer()` build the VDBE instructions for SELECT row materialization, ORDER BY insertion, LIMIT optimization, DISTINCT filtering, and sorter-reference payload deferral.
- `selectInnerLoop()` is the central SELECT row-output code generator. It routes each row to destinations such as `SRT_Output`, `SRT_Coroutine`, `SRT_Table`, `SRT_EphemTab`, `SRT_Set`, `SRT_Union`, `SRT_Except`, `SRT_Queue`, `SRT_DistQueue`, `SRT_Fifo`, `SRT_DistFifo`, `SRT_Mem`, `SRT_Exists`, and `SRT_Upfrom`.
- `sqlite3KeyInfoAlloc()`, `sqlite3KeyInfoRef()`, `sqlite3KeyInfoUnref()`, and `sqlite3KeyInfoFromExprList()` allocate/refcount collation and sort-order metadata for ephemeral btrees and sorters.
- `generateSortTail()` drains a sorter after scan completion, reconstructs result columns, applies OFFSET, supports sorter-reference row reloads, and emits rows to the final `SelectDest`.
- `columnTypeImpl()`, `generateColumnTypes()`, `sqlite3GenerateColumnNames()`, `sqlite3ColumnsFromExprList()`, `sqlite3SubqueryColumnTypes()`, and `sqlite3ResultSetOfSelect()` derive user-visible result-column names, declared types, origin metadata, collations, affinities, and transient `Table` structures for views/subqueries.
- `computeLimitRegisters()` emits VDBE code for LIMIT/OFFSET counters and updates row estimates when LIMIT is a non-negative integer constant.
- `generateWithRecursiveQuery()` implements recursive CTE execution using a current pseudo-table, a queue table, an optional distinct table, optional ORDER BY priority ordering, and LIMIT/OFFSET accounting.
- `multiSelectValues()`, `multiSelect()`, `sqlite3SelectWrongNumTermsError()`, `generateOutputSubroutine()`, and `multiSelectOrderBy()` implement VALUES compounds, UNION/UNION ALL/EXCEPT/INTERSECT without ORDER BY, wrong-column-count diagnostics, coroutine merge output, and ORDER BY merge logic.
- `SubstContext`, `substExpr()`, `substExprList()`, and `substSelect()` replace references to a flattened subquery cursor with duplicated result expressions, preserving collation and outer-join null-row behavior.
- `recomputeColumnsUsed()`, `renumberCursors()`, `findLeftmostExprlist()`, `compoundHasDifferentAffinities()`, and `flattenSubquery()` support subquery flattening, cursor remapping, compound UNION ALL flattening, and post-flattening column-use recalculation.
- `WhereConst`, `findConstInWhere()`, `propagateConstantExprRewrite()`, and `propagateConstants()` implement constant propagation by tagging matching column expressions with `EP_FixedCol` and attaching the constant expression rather than naively replacing affinity-sensitive comparisons.
- `pushDownWhereTerms()` duplicates safe outer WHERE predicates into subqueries, with restrictions for LIMIT, recursive CTEs, LEFT/RIGHT/FULL joins, window partitions, VALUES clauses, and non-BINARY compound operators.
- `disableUnusedSubqueryResultColumns()`, `minMaxQuery()`, `isSimpleCount()`, `sqlite3IndexedByLookup()`, `convertCompoundSelectToSubquery()`, `cannotBeFunction()`, `searchWith()`, `sqlite3WithPush()`, `resolveFromTermToCte()`, `sqlite3SelectPopWith()`, and `sqlite3ExpandSubquery()` handle smaller but important SELECT preparation and optimization tasks.
- `selectExpander()`, `sqlite3SelectExpand()`, `selectAddSubqueryTypeInfo()`, `sqlite3SelectAddTypeInfo()`, and `sqlite3SelectPrep()` are the high-level expansion pipeline before name resolution and type-info finalization.
- Aggregate helpers at the end of the chunk include `analyzeAggFuncArgs()`, `optimizeAggregateUseOfIndexedExpr()`, `aggregateConvertIndexedExprRefToColumn()`, `assignAggregateRegisters()`, `resetAccumulator()`, `finalizeAggFunctions()`, and the start of `updateAccumulator()`.

## Control Flow

Statement preparation at the top of the chunk is wrapper-oriented. `sqlite3_prepare*()` validates pointers through `sqlite3LockAndPrepare()`, which holds the database mutex and all btree mutexes while retrying `sqlite3Prepare()` for `SQLITE_ERROR_RETRY` and one schema reset for `SQLITE_SCHEMA`. `sqlite3Reprepare()` assumes the database mutex is already held, obtains saved SQL from the VDBE, recompiles with the original prepare flags and old VDBE context, swaps bytecode/data structures, transfers bindings, resets the temporary VDBE step result, and finalizes the temporary VDBE.

SELECT processing starts with AST construction and expansion:

- Parser actions allocate `Select` objects with `sqlite3SelectNew()`, defaulting an absent result list to `*` and an absent source list to an empty `SrcList`.
- `sqlite3SelectPrep()` calls `sqlite3SelectExpand()`, then name resolution, then `sqlite3SelectAddTypeInfo()`.
- `sqlite3SelectExpand()` first rewrites compound SELECTs with problematic `ORDER BY ... COLLATE` into a wrapper subquery when needed, then walks every SELECT with `selectExpander()`.
- `selectExpander()` pushes WITH context, assigns source cursors, resolves each FROM item as a subquery, CTE, table, view, or virtual table, resolves `INDEXED BY`, processes joins, expands `*` and `table.*`, enforces the result-column limit, and records complex-result flags.
- `sqlite3SelectAddTypeInfo()` walks resolved FROM-clause subqueries and fills their transient table columns with declaration type, affinity, and collation data.

Join processing is intentionally lowered early. NATURAL joins synthesize USING lists by intersecting visible column names on the left and right. USING terms become equality expressions between left and right columns. For RIGHT/FULL joins, repeated left-side USING names can become a `coalesce()` expression and ambiguous non-USING references produce errors. ON terms are moved into `p->pWhere` and tagged so later WHERE planning preserves outer-join semantics.

Row generation flows through `selectInnerLoop()`. It allocates result registers, optionally reserves ORDER BY prefix registers, loads expression output unless a LIMIT/sorter optimization defers it, applies DISTINCT filtering through `codeDistinct()`, then emits destination-specific VDBE instructions. Without a sorter it writes directly to result rows, scalar registers, ephemeral tables, queues, sets, or compound temp indexes. With a sorter it calls `pushOntoSorter()` so `generateSortTail()` can later output sorted rows.

Sorter control has several branches:

- `pushOntoSorter()` computes ORDER BY keys, optional sequence numbers, payload columns, and records. It supports a partial ORDER BY prefix already satisfied by an index (`nOBSat`), block-sort reset logic, and LIMIT/OFFSET top-N pruning that avoids storing rows larger than the current largest retained entry.
- `makeSorterRecord()` forces deferred row loading just before packing a sorter record.
- `generateSortTail()` emits `OP_Sort` or `OP_SorterSort`, reloads deferred table rows if `SQLITE_ENABLE_SORTER_REFERENCES` is active, reconstructs output columns either from ORDER BY keys, sorter payload columns, or table lookups, and writes to the requested destination.

Compound SELECTs have two major paths. Without ORDER BY, `multiSelect()` creates ephemeral tables for UNION/EXCEPT/INTERSECT as needed, streams UNION ALL arms directly when possible, and converts the final temp table back through `selectInnerLoop()`. Recursive CTEs are special-cased by `generateWithRecursiveQuery()`, which alternates between queue extraction, output of the current row, and recursive-step insertion back into the queue. With ORDER BY, `multiSelectOrderBy()` compiles the left and right sides as coroutines and emits a merge routine driven by `OP_Compare`, `OP_Permutation`, `OP_Yield`, and output subroutines; duplicate removal for UNION/EXCEPT/INTERSECT is handled by comparing against a previous-output register vector.

Subquery flattening and predicate movement run as SELECT-shape rewrites. `flattenSubquery()` enforces a long list of semantic restrictions, detaches the subquery, optionally duplicates parent SELECT arms for compound UNION ALL subqueries, moves subquery FROM terms into the parent FROM list, transfers WHERE/ORDER/LIMIT pieces where legal, substitutes result expressions for references to the old subquery cursor, recomputes `colUsed`, and schedules stale table structures for cleanup. `pushDownWhereTerms()` duplicates eligible predicates into subquery WHERE/HAVING clauses. `propagateConstants()` iteratively tags column references that are known equal to constants, stopping when no new changes occur.

The aggregate code at the chunk end prepares state rather than completing the full aggregate update loop. It analyzes aggregate arguments, adjusts `AggInfo` when indexed expressions can cover GROUP BY aggregate inputs, converts indexed expression references into aggregate-column opcodes, reserves accumulator registers, opens ephemeral distinct/order-by aggregate btrees in `resetAccumulator()`, and emits finalization code in `finalizeAggFunctions()`. The actual `updateAccumulator()` implementation begins at the boundary and continues in the next chunk.

## State and Persistence Behavior

Most persistent state in this chunk is compile-time/query-plan state rather than database page data. Key mutable structures include:

- `Select`: result expressions, FROM list, WHERE/GROUP/HAVING/ORDER/LIMIT, compound links, WITH/window lists, flags such as `SF_Expanded`, `SF_Resolved`, `SF_HasTypeInfo`, `SF_Compound`, `SF_Recursive`, `SF_Distinct`, `SF_Aggregate`, `SF_PushDown`, `SF_UsesEphemeral`, and row-estimate/register fields.
- `SrcItem`: resolved `Table` pointers, cursor numbers, join flags, ON/USING data, CTE/materialization state, subquery references, aliases, `colUsed` masks, INDEXED BY state, and recursive-CTE markers.
- `Expr` and `ExprList` metadata: join-origin flags, collations, `iOrderByCol`, `bSorterRef`, `bUsed`, `bNoExpand`, output names, aggregate mappings, and fixed-column constant substitutions.
- `Table`/`Column` objects synthesized for views, subqueries, and CTEs. These are transient schema objects with `TF_Ephemeral`, rowid visibility flags, generated column names, affinity/type/collation metadata, and parser-cleanup ownership.
- `KeyInfo` objects attached to ephemeral btree/sorter open opcodes. They are refcounted and contain collation pointers, sort flags, key-field counts, and payload-field counts.
- `Parse` state: VDBE pointer, current WITH stack, cursor/register counters, SELECT id counter, error/OOM flags, authorization context, cleanup callbacks, and optimization flags.
- `AggInfo`: aggregate column/function arrays, accumulator counts, sorting column count, first register, aggregate function definitions, distinct/order-by cursors, and subtype/order payload flags.

VDBE bytecode emitted here affects runtime persistence through transient btrees and sorters. DISTINCT, UNION, EXCEPT, INTERSECT, recursive CTE queues, recursive duplicate filters, aggregate DISTINCT, aggregate ORDER BY, and ORDER BY/GROUP BY all allocate ephemeral cursors. These objects live for statement execution and are closed by the VDBE or replaced with no-ops when an optimization proves them unnecessary. Persistent database state is not modified by this code directly except through generated SELECT destinations such as `SRT_Table`, `SRT_EphemTab`, and `SRT_Upfrom`, which emit `OP_Insert`/`OP_IdxInsert` into statement-local or caller-provided cursors.

The CTE path maintains shared `CteUse` state across references, including materialization preference, use count, and recursive error strings. Recursive references temporarily attach the CTE table to self-referential source items, assign a dedicated cursor for the recursive table, and manipulate `pParse->pWith` while walking recursive terms to detect circular or illegal recursive references.

## Dependencies and Integration Points

This chunk depends on broad SQLite internals:

- Parser and AST helpers: `sqlite3Expr*`, `sqlite3ExprList*`, `sqlite3SrcList*`, `sqlite3SelectDup()`, `sqlite3SubqueryDetach()`, `sqlite3SrcItemAttachSubquery()`, `sqlite3WalkSelect()`, `sqlite3ResolveSelectNames()`, `sqlite3ResolveOrderGroupBy()`, and token/name helpers.
- VDBE codegen APIs: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeGoto()`, `sqlite3VdbeScanStatusRange()`, `sqlite3VdbeScanStatusCounters()`, and opcode constants such as `OP_OpenEphemeral`, `OP_SorterOpen`, `OP_MakeRecord`, `OP_IdxInsert`, `OP_ResultRow`, `OP_Yield`, `OP_AggStep`, and `OP_AggFinal`.
- Schema/catalog helpers: `sqlite3LocateTableItem()`, `sqlite3ViewGetColumnNames()`, `sqlite3IndexedByLookup()`, `sqlite3SchemaToIndex()`, `sqlite3PrimaryKeyIndex()`, `sqlite3ColumnType()`, `sqlite3ColumnSetColl()`, `sqlite3ColumnPropertiesFromName()`, and table/view/virtual-table predicates.
- Name/collation/affinity logic: `sqlite3ExprCollSeq()`, `sqlite3ExprNNCollSeq()`, `sqlite3ExprAffinity()`, `sqlite3AffinityType()`, `sqlite3ExprDataType()`, `sqlite3ExprCompareCollSeq()`, `sqlite3IsBinary()`, and standard type tables.
- Planner-facing interfaces: join flags (`JT_*`), `WHERE_DISTINCT_*`, `WHERE_ORDERBY_*`, optimization toggles (`SQLITE_QueryFlattener`, `SQLITE_FlttnUnionAll`, `SQLITE_BalancedMerge`, `SQLITE_MinMaxOpt`, `SQLITE_FactorOutConst`), `ExplainQueryPlan` macros, and scan-status hooks.
- Optional compilation blocks: `SQLITE_OMIT_UTF16`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_CTE`, `SQLITE_OMIT_COMPOUND_SELECT`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_ENABLE_SORTER_REFERENCES`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ALLOW_ROWID_IN_VIEW`, `SQLITE_OMIT_DECLTYPE`, `SQLITE_OMIT_VIRTUALTABLE`, and debug/tree-trace flags.

For WiredTiger, this remains third-party SQLite test code rather than WiredTiger storage-engine logic. The integration point is build/test compatibility: modifications to this amalgamated file can alter vendored SQLite behavior visible to any tests or helper binaries compiled against this source.

## Risks and Edge Cases

- Public prepare APIs rely on exact mutex and btree-enter ordering. `sqlite3Prepare16()` enters `db->mutex` and then calls `sqlite3LockAndPrepare()`, which also enters the same mutex; this assumes SQLite's configured mutex behavior supports the internal pattern.
- UTF-16 tail mapping depends on correctly counting UTF-8 characters and UTF-16 bytes. Odd `nBytes`, missing terminators for negative `nBytes`, or malformed input are sensitive edge cases.
- Join tags are semantic, not cosmetic. Dropping `EP_OuterON`, `EP_InnerON`, `EP_CanBeNull`, or `w.iJoin` at the wrong time can turn LEFT/RIGHT/FULL joins into inner joins or filter null-extended rows too early.
- USING processing with RIGHT/FULL joins is delicate. The coalesce path is needed when multiple left-side USING columns may contribute, while ambiguous non-USING duplicates must remain errors.
- `selectInnerLoop()` has many destination-specific assumptions. Register layout, `nResultCol`, `nPrefixReg`, `regOrig`, and deferred row loading must remain consistent or sorter records will be decoded incorrectly.
- DISTINCT optimization rewrites delayed `OP_OpenEphemeral` opcodes into no-ops or `OP_Null`. This requires `codeDistinct()` and `fixDistinctOpenEph()` to agree on strategy and register initialization, especially for all-NULL first rows.
- Sorter LIMIT optimization changes memory and CPU behavior by keeping only the best LIMIT+OFFSET rows. Incorrect comparisons against partial ORDER BY prefixes or stale `labelOBLopt` labels can silently lose rows.
- Column-name behavior is compatibility-sensitive. Comments explicitly warn that legacy applications depend on undocumented naming details. `short_column_names`, `full_column_names`, AS-name precedence, duplicate suffixing, and `COLFLAG_NOEXPAND` need careful preservation.
- Flattening restrictions are correctness guards. Relaxing LIMIT, DISTINCT, aggregate, compound, window, recursive CTE, MATERIALIZED CTE, LEFT/RIGHT/FULL join, or affinity restrictions can produce wrong answers rather than just worse plans.
- Constant propagation intentionally avoids direct expression replacement for affinity/collation-sensitive comparisons. The `EP_FixedCol` representation is required to preserve cases such as numeric equality versus text `LIKE`.
- WHERE push-down across window functions is safe only for predicates that filter whole partitions. Pushing row-level predicates into a window subquery changes window results.
- CTE resolution mutates parser WITH-stack state and CTE error strings while walking. Missed restoration of `pParse->pWith` or `pCte->zCteErr` can produce bogus circular-reference errors or allow illegal recursion.
- Aggregate ORDER BY and DISTINCT use ephemeral btrees with `KeyInfo` built from expression lists. Wrong payload counts, sequence-column handling, or subtype preservation will change ordered aggregate results.
- The chunk ends immediately after `updateAccumulator()` initializes `directMode`; the logic that evaluates aggregate filters, DISTINCT checks, ORDER BY aggregate payload insertion, `OP_AggStep`, min/max hit tracking, and accumulator column loading is in the following chunk.

## Test Signals

Useful test signals in this range include:

- `assert()` checks for mutex ownership, parser state, SELECT flags, cursor mappings, result-column counts, KeyInfo writeability, aggregate register allocation, recursive CTE structure, and impossible walker callbacks.
- `testcase()` markers around join keyword combinations, compound operators, DISTINCT strategies, destination variants, LEFT/RIGHT/FULL join branches, OOM/name-collision paths, aggregate DISTINCT/window flags, and optimization-specific cases.
- `VdbeCoverage()` annotations on generated branches such as OFFSET, DISTINCT comparisons, LIMIT exits, sorter pruning, recursive queue iteration, compound merge yields, and temp-table membership tests.
- `ExplainQueryPlan()` output for temporary btrees, recursive CTE setup/step, compound query arms, merge plans, aggregate DISTINCT/ORDER BY temp storage, Bloom filter creation, and sorter usage.
- Debug-only tree tracing via `TREETRACE()` and `printAggInfo()` for SELECT expansion, flattening, compound processing, column-name generation, aggregate indexed-expression adjustment, and wildcard expansion.
- API armor and misuse checks in prepare wrappers: null `ppStmt`, invalid database handles, null SQL text, OOM during UTF-16 conversion, and prepare-flag masking.
- Error-message paths worth covering: unknown join type, NATURAL join with ON/USING, missing USING columns, ambiguous USING references, no such table for `table.*`, too many result columns, compound SELECT result-count mismatch, no such INDEXED BY index, unsafe view/virtual-table usage in untrusted schema, circular/multiple recursive CTE references, bad CTE column counts, and invalid DISTINCT aggregate arity.

### subset-b-009032: lines 151745-158971

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 151745-158971

## Scope

This chunk covers a large middle section of SQLite's amalgamated `sqlite3.c`. It starts in the tail of `select.c` aggregate accumulator code, then includes complete or partial embedded source-file sections for:

- `select.c`: the end of aggregate step generation, simple `count(*)` explain output, HAVING-to-WHERE movement, self-join view detection, count-of-UNION-ALL view optimization, subquery coroutine eligibility, and almost all of `sqlite3Select()`.
- `table.c`: `sqlite3_get_table()` and `sqlite3_free_table()` wrappers over `sqlite3_exec()`.
- `trigger.c`: trigger object creation, trigger-step builders, trigger lookup/drop/unlink, RETURNING handling, trigger subprogram generation, trigger invocation, and old/new column mask calculation.
- `update.c`: ordinary table/view/UPDATE-FROM/UPSERT UPDATE code generation plus virtual-table UPDATE support.
- `upsert.c`: `Upsert` lifetime, target analysis, index matching, and DO UPDATE dispatch.
- `vacuum.c`: VACUUM opcode generation and most of `sqlite3RunVacuum()`.
- `vtab.c`: virtual table module registration, constructor calls, schema declaration, transaction hooks, savepoint hooks, function overloads, writable marking, eponymous table setup, and vtab configuration APIs.
- The chunk ends at the beginning of `wherecode.c` and included `whereInt.h` comments. WHERE loop code generation itself continues in the next chunk.

This is executable core database engine code, not a test harness despite living under WiredTiger's third-party SQLite test copy.

## Purpose

The covered code translates parsed SQL constructs into SQLite VDBE bytecode and manages several public or extension-facing APIs. The main responsibilities are:

- Generate SELECT bytecode for ordinary scans, DISTINCT, ORDER BY, aggregate queries, GROUP BY, subqueries, views, CTEs, window-rewritten selects, and simple `count(*)` fast paths.
- Materialize `sqlite3_get_table()` result arrays for legacy callers.
- Build, store, delete, and execute triggers, including inline RETURNING support and trigger subprogram caching.
- Generate UPDATE bytecode for rowid tables, WITHOUT ROWID tables, views with triggers, virtual tables, UPDATE-FROM, limited UPDATE builds, foreign keys, generated columns, conflict policies, and UPSERT DO UPDATE.
- Analyze UPSERT conflict targets and route failed unique constraints to matching `ON CONFLICT` clauses.
- Implement VACUUM by attaching a transient database, recreating schema/data, copying btree content back or into a named output, and restoring connection state.
- Register and manage virtual table modules, call `xCreate`/`xConnect`/`xDestroy`, handle `sqlite3_declare_vtab()`, and coordinate virtual table transaction/savepoint callbacks.

## Important APIs, Types, and Functions

### SELECT and Aggregate Code Generation

- `updateAccumulator()` tail at the start of the chunk emits `OP_AggStep`, ORDER BY aggregate sorter inserts, DISTINCT filtering through `codeDistinct()`, collation selection for aggregate functions needing collations, and accumulator column refresh logic.
- `explainSimpleCount()` emits an `EXPLAIN QUERY PLAN` scan line for optimized `SELECT count(*) FROM table`.
- `havingToWhereExprCb()` and `havingToWhere()` move HAVING terms that are constant or GROUP BY-equivalent into WHERE, replacing the HAVING term with integer `1`.
- `isSelfJoinView()` detects repeated materialized view/subquery instances that can share a materialization, while rejecting push-down-modified views, coroutine views, and ambiguous CTE copies.
- `agginfoFree()` releases `AggInfo` arrays registered with parser cleanup.
- `countOfViewOptimization()` rewrites `SELECT count(*) FROM (SELECT ... UNION ALL SELECT ...)` into a sum of per-arm `count(*)` scalar subqueries when the compound subquery has no WHERE, LIMIT, GROUP BY/HAVING, aggregate, or DISTINCT terms.
- `sameSrcAlias()` supports UPDATE-FROM validation by finding duplicate target aliases in nested FROM sources.
- `fromClauseTermCanBeCoroutine()` decides whether a FROM-subquery can run as a coroutine instead of being materialized, excluding materialized or multiply-used CTEs, RIGHT/FULL join left operands, disabled coroutine optimization, self-joined views, UPDATE-FROM cases, and join shapes that cannot put the subquery in an outer loop.
- `sqlite3Select()` is the central SELECT compiler. It performs preparation, name resolution, window rewriting, FROM-clause optimization, compound SELECT dispatch, constant propagation, count-of-view rewriting, subquery code generation, DISTINCT-to-GROUP-BY rewriting, sorter/distinct setup, LIMIT setup, scan generation, aggregate/GROUP BY generation, result output, ORDER BY tail generation, and debug self-checks.

### `sqlite3_get_table()`

- `TabResult` accumulates `char **azResult`, row/column counts, allocated slots, used slots, error message, and callback return code.
- `sqlite3_get_table_cb()` appends column names on the first row, validates consistent column counts, copies row values, expands the result pointer array, and records out-of-memory or incompatible-query errors.
- `sqlite3_get_table()` initializes `TabResult`, runs `sqlite3_exec()`, handles aborts from the callback, shrinks the pointer array, returns row/column counts, and stores the slot count in the hidden element immediately before the public result pointer.
- `sqlite3_free_table()` walks that hidden slot count and frees all copied strings and the pointer array.

### Trigger Handling

- `sqlite3DeleteTriggerStep()`, `sqlite3DeleteTrigger()`, and `sqlite3UnlinkAndDeleteTrigger()` free trigger steps, trigger objects, and schema hash/table links.
- `sqlite3TriggerList()` merges TEMP triggers with persistent table triggers and also binds the synthetic RETURNING trigger to the current target table.
- `sqlite3BeginTrigger()` validates CREATE TRIGGER names, schema qualification, target table/view rules, virtual/shadow/system-table restrictions, authorization, orphan TEMP triggers, and initializes `pParse->pNewTrigger`.
- `sqlite3FinishTrigger()` fixes trigger-step schema references, writes the `sqlite_schema` row for new triggers, changes schema cookies, and installs triggers into schema hashes during schema load.
- `sqlite3TriggerSelectStep()`, `sqlite3TriggerInsertStep()`, `sqlite3TriggerUpdateStep()`, and `sqlite3TriggerDeleteStep()` construct `TriggerStep` nodes, duplicating parse trees unless rename processing requires preserving original pointers.
- `sqlite3TriggersExist()` and `triggersReallyExist()` filter trigger lists by operation, UPDATE OF columns, enabled-trigger configuration, RETURNING triggers, virtual table restrictions, and BEFORE/AFTER masks.
- `sqlite3TriggerStepSrc()` converts a trigger step target name and optional UPDATE-FROM list into a `SrcList`, schema-pinning non-TEMP triggers to their owning database.
- `sqlite3ExpandReturning()`, `sqlite3ProcessReturningSubqueries()`, and `codeReturningTrigger()` expand RETURNING expressions, mark self-referencing subqueries as correlated, resolve RETURNING names against OLD/NEW-style base registers, and store RETURNING rows in an ephemeral result cursor.
- `codeTriggerProgram()`, `codeRowTrigger()`, `getRowTrigger()`, `sqlite3CodeRowTriggerDirect()`, and `sqlite3CodeRowTrigger()` compile trigger bodies into reusable `SubProgram` bytecode and emit `OP_Program` calls or inline RETURNING code.
- `sqlite3TriggerColmask()` returns old/new column-use masks by compiling or retrieving trigger programs, allowing UPDATE/DELETE callers to avoid loading columns that triggers do not reference.

### UPDATE and UPSERT

- `sqlite3ColumnDefault()` attaches literal ALTER TABLE default values to `OP_Column` and emits `OP_RealAffinity` for REAL columns from ordinary tables.
- `indexColumnIsBeingUpdated()` and `indexWhereClauseMightChange()` conservatively decide whether an index or partial-index predicate depends on changing columns or rowid.
- `updateFromSelect()` builds a SELECT that writes candidate row identifiers, primary keys, view columns, and SET expressions into an ephemeral table for UPDATE-FROM or limited UPDATE flows.
- `sqlite3Update()` is the UPDATE compiler. It resolves target columns, generated-column dependencies, authorization, triggers, foreign keys, index update needs, cursor allocation, one-pass eligibility, row collection, old/new register loading, BEFORE/AFTER triggers, constraint checks, FK actions, row/index deletion and insertion, change counts, and cleanup.
- `updateVirtualTable()` emits `OP_VUpdate` for virtual tables, using a one-pass path when the virtual table scan can match at most one row and an ephemeral table otherwise. It passes `OPFLAG_NOCHNG` values so `sqlite3_vtab_nochange()` can observe unchanged columns.
- `sqlite3UpsertDelete()`, `sqlite3UpsertDup()`, and `sqlite3UpsertNew()` manage `Upsert` object lifetime.
- `sqlite3UpsertAnalyzeTarget()` resolves conflict targets, matches them to rowid or unique indexes including partial-index WHERE clauses and expression indexes, marks duplicate ON CONFLICT clauses, and reports unmatched targets.
- `sqlite3UpsertNextIsIPK()` and `sqlite3UpsertOfIndex()` help the INSERT constraint checker find the next relevant upsert clause.
- `sqlite3UpsertDoUpdate()` seeks from a failed unique index cursor to the table row if needed, applies REAL affinity to `excluded.*` data, and calls `sqlite3Update()` with the upsert's SET and WHERE expressions.

### VACUUM

- `execSql()` prepares and runs SQL, recursively executing single-column SELECT results only if the generated text starts with `CRE` or `INS`, which prevents corrupted schema SQL from executing arbitrary statement classes during VACUUM.
- `execSqlF()` formats SQL using SQLite allocation and calls `execSql()`.
- `sqlite3Vacuum()` emits `OP_Vacuum` after resolving an optional database name and optional VACUUM INTO expression.
- `sqlite3RunVacuum()` enforces autocommit and no-other-active-statement constraints, saves connection flags/counters/tracing/open flags, attaches a randomized transient database or output file, mirrors schema and data, copies btree metadata/content, commits the transient btree, restores flags, closes and detaches the transient database, and resets schemas.

### Virtual Tables

- `struct VtabCtx` tracks the active `xCreate`/`xConnect` constructor context, the in-progress `VTable`, the owning `Table`, and whether `sqlite3_declare_vtab()` has been called.
- `sqlite3VtabCreateModule()`, `createModule()`, `sqlite3_create_module()`, `sqlite3_create_module_v2()`, and `sqlite3_drop_modules()` register, replace, unregister, or bulk-drop virtual table modules.
- `sqlite3VtabModuleUnref()`, `sqlite3VtabLock()`, `sqlite3VtabUnlock()`, `sqlite3GetVTable()`, `vtabDisconnectAll()`, `sqlite3VtabDisconnect()`, `sqlite3VtabUnlockList()`, and `sqlite3VtabClear()` manage per-connection `VTable` references and deferred disconnect lists.
- `sqlite3VtabBeginParse()`, `addArgumentToVtab()`, `sqlite3VtabArgInit()`, `sqlite3VtabArgExtend()`, and `sqlite3VtabFinishParse()` parse `CREATE VIRTUAL TABLE`, store module arguments, write schema rows, issue `OP_VCreate`, and install schema-loaded virtual tables.
- `vtabCallConstructor()`, `sqlite3VtabCallConnect()`, and `sqlite3VtabCallCreate()` call module constructors, guard against recursive constructor calls, verify schema declaration, copy declared columns/index metadata, identify hidden columns, and enroll created vtabs in transaction tracking.
- `sqlite3_declare_vtab()` validates and parses the supplied CREATE TABLE statement, transfers columns/index metadata into the virtual table, and rejects writable WITHOUT ROWID virtual tables with multi-column primary keys.
- `sqlite3VtabCallDestroy()`, `sqlite3VtabSync()`, `sqlite3VtabRollback()`, `sqlite3VtabCommit()`, `sqlite3VtabBegin()`, and `sqlite3VtabSavepoint()` bridge DROP TABLE, commit, rollback, xSync, xBegin, xSavepoint, xRollbackTo, and xRelease module callbacks.
- `sqlite3VtabOverloadFunction()` lets modules overload MATCH, LIKE, GLOB, and REGEXP-style functions for virtual table columns through `xFindFunction`.
- `sqlite3VtabMakeWritable()` records virtual tables needing `OP_VBegin`.
- `sqlite3VtabEponymousTableInit()` and `sqlite3VtabEponymousTableClear()` create and destroy eponymous virtual table instances for modules whose `xCreate` is absent or aliases `xConnect`.
- `sqlite3_vtab_on_conflict()` exposes the active conflict mode to `xUpdate()`.
- `sqlite3_vtab_config()` records constraint support, innocuous/direct-only risk, and all-schema usage during constructor execution.

## Control Flow

`sqlite3Select()` has the densest control flow in this chunk. It first rejects invalid parse state and authorizes `SQLITE_SELECT`, drops ignorable ORDER BY/DISTINCT for certain destinations, runs `sqlite3SelectPrep()`, validates UPDATE-FROM aliases, generates output column names, and optionally rewrites window functions. It then loops through FROM terms to reduce outer joins, remove harmless subquery ORDER BY clauses, and flatten eligible subqueries. Compound SELECTs dispatch to `multiSelect()` and return early.

For simple SELECTs, `sqlite3Select()` may propagate constants, rewrite count-of-UNION-ALL views, authorize unreferenced tables, push WHERE terms into subqueries, null unused subquery columns, and generate subquery implementations. Subqueries may become coroutines, reuse existing CTE materialization, reuse a self-joined view's materialization, or be materialized into ephemeral tables/subroutines. After this, DISTINCT plus matching ORDER BY may become GROUP BY, sort and distinct ephemeral tables are opened, LIMIT registers are prepared, and execution splits into non-aggregate and aggregate paths.

The non-aggregate path starts `sqlite3WhereBegin()`, imports planner signals for distinctness and ordering, no-ops unneeded sorters, optionally delegates window step generation, runs `selectInnerLoop()`, and closes the WHERE loop. The aggregate path builds `AggInfo`, analyzes result/ORDER BY/HAVING expressions, optionally moves HAVING terms into WHERE, handles min/max and DISTINCT aggregate optimizations, and then either performs GROUP BY processing with sorted or already-grouped input, or the no-GROUP-BY path with a special `OP_Count` fast path for `SELECT count(*) FROM table` and a general accumulator scan otherwise. Output subroutines finalize aggregates, apply HAVING, and invoke `selectInnerLoop()`.

`sqlite3Update()` first resolves the target table, triggers, view status, UPDATE-FROM shape, limits, read-only checks, cursors, and update column mapping. It computes generated-column dependency propagation, FK requirements, indexes that need recomputation, REPLACE risk, registers, and optional view materialization. Virtual tables branch to `updateVirtualTable()`. Ordinary tables choose between collecting keys in an ephemeral table and one-pass WHERE updates. Per row, it computes new rowid/PK values, loads old values needed by FKs/triggers, builds `NEW.*`, computes generated columns, fires BEFORE triggers, reloads unmodified columns after BEFORE triggers, checks constraints and FKs, deletes old index entries/row as needed, inserts new records/index entries, runs FK actions, counts changes, fires AFTER triggers, and advances the loop.

Trigger execution has two paths. Ordinary triggers are compiled once per top-level parse/or-conflict pair into `SubProgram` bytecode through `codeRowTrigger()` and then invoked by `OP_Program`. RETURNING triggers are not subprograms; `codeReturningTrigger()` builds and resolves RETURNING expressions inline and inserts each RETURNING row into a cursor owned by the current statement.

`sqlite3RunVacuum()` uses SQL execution as orchestration: attach transient database, create mirrored schema from selected schema SQL, copy table data with generated INSERT statements, copy views/triggers/virtual table schema rows directly, then copy btree metadata and content. All exits converge through `end_of_vacuum`, which restores saved connection state, closes the transient btree, resets schemas, and returns the saved error code.

Virtual table constructors flow through `vtabCallConstructor()`. The active context is pushed on `db->pVtabCtx`, `xCreate` or `xConnect` is called, the constructor must call `sqlite3_declare_vtab()`, and then the resulting `sqlite3_vtab` is wired to a `VTable` with module reference counts and hidden-column metadata. Transaction hooks are tracked in `db->aVTrans`; commit/rollback/finalizer paths lock and unlock each `VTable` around callbacks and clear the transaction array.

## State and Persistence Behavior

This chunk manipulates several layers of state:

- Parser/codegen state: `Parse` fields such as `nMem`, `nTab`, `nErr`, `zAuthContext`, `pTriggerPrg`, `pNewTrigger`, `eTriggerOp`, `pTriggerTab`, `bReturning`, and cleanup lists are updated heavily. Many AST nodes are duplicated or registered for parser cleanup to avoid leaks on early exits.
- VDBE state: bytecode cursors, registers, labels, ephemeral btrees, sorters, coroutines, subprograms, and P4 payloads are emitted for SELECT, triggers, UPDATE, VACUUM, and virtual tables.
- Schema state: triggers are inserted into or removed from schema hashes and table trigger lists; virtual tables are stored in `sqlite_schema` with `rootpage=0`; VACUUM resets all connection schemas after replacing or copying database content.
- Table/index persistence: UPDATE emits record and index deletion/insertion bytecode, enforces constraints, updates autoincrement state, and may cascade foreign key actions. VACUUM rewrites the database image and selected btree metadata.
- Trigger persistence: CREATE TRIGGER writes a `sqlite_schema` row outside schema initialization and installs trigger objects during schema reload. DROP TRIGGER removes schema rows and emits `OP_DropTrigger`.
- `sqlite3_get_table()` persistence is caller-owned heap state. It stores a hidden element count before the returned pointer and requires `sqlite3_free_table()`.
- Virtual table connection state: registered modules live in `db->aModule`; per-connection `VTable` objects hang off `Table.u.vtab.p` or `db->pDisconnect`; transaction participants live in `db->aVTrans`; constructor context lives temporarily in `db->pVtabCtx`.
- VACUUM temporarily changes connection flags such as writable schema, disabled checks/FKs/defensive/count rows/reverse order, trace settings, open flags, change counters, `db->init.iDb`, and `db->autoCommit`, then restores them on exit.

The code is allocation-heavy but uses SQLite's ownership conventions: parse-tree inputs are usually consumed and freed by cleanup labels, duplicated when needed for deferred compilation, and protected by `db->mallocFailed` checks.

## Dependencies and Integration Points

The code depends on SQLite's internal AST, schema, planner, VDBE, btree, pager, and authorization subsystems. Important internal integration points include:

- Name resolution and expression walkers: `sqlite3SelectPrep()`, `sqlite3ResolveExprNames()`, `sqlite3ResolveExprListNames()`, `sqlite3WalkExpr()`, aggregate analyzers, collation lookup, and generated-column expression helpers.
- Planner and WHERE code: `sqlite3WhereBegin()`, `sqlite3WhereEnd()`, `sqlite3WhereOkOnePass()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereIsOrdered()`, `sqlite3WhereOutputRowCount()`, min/max early-out, and ORDER BY LIMIT optimization labels.
- VDBE builders: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChange*()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeTakeOpArray()`, `OP_AggStep`, `OP_Count`, `OP_Program`, `OP_VUpdate`, `OP_Vacuum`, and many cursor/sorter opcodes.
- Schema/auth APIs: `sqlite3AuthCheck()`, `sqlite3CodeVerifySchema()`, `sqlite3NestedParse()`, schema cookies, schema hash tables, `sqlite3Fix*()` database-name fixers, and rename token remapping.
- Constraint and write paths: `sqlite3GenerateConstraintChecks()`, `sqlite3CompleteInsertion()`, `sqlite3GenerateRowIndexDelete()`, `sqlite3FkRequired()`, `sqlite3FkCheck()`, `sqlite3FkActions()`, autoincrement finalization, and pre-update hook support.
- Btree/pager/VFS layers: VACUUM calls `sqlite3BtreeBeginTrans()`, page-size/autovacuum setters, metadata getters/updaters, `sqlite3BtreeCopyFile()`, `sqlite3BtreeCommit()`, pager journal-mode checks, and file-size checks for VACUUM INTO output.
- Virtual table module ABI: public module methods `xCreate`, `xConnect`, `xDestroy`, `xDisconnect`, `xUpdate`, `xBegin`, `xSync`, `xCommit`, `xRollback`, `xSavepoint`, `xRollbackTo`, `xRelease`, and `xFindFunction`, plus public APIs `sqlite3_create_module*()`, `sqlite3_declare_vtab()`, `sqlite3_vtab_config()`, and `sqlite3_vtab_on_conflict()`.
- Compile-time feature gates: `SQLITE_OMIT_GET_TABLE`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_VIEW`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_UPSERT`, `SQLITE_OMIT_VACUUM`, `SQLITE_OMIT_ATTACH`, `SQLITE_ENABLE_UPDATE_DELETE_LIMIT`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ALLOW_ROWID_IN_VIEW`, and tracing/debug macros.

In this repository, the immediate consumer is WiredTiger's vendored SQLite copy used by tests. Behavioral changes here would affect SQLite SQL execution semantics inside that embedded test dependency rather than WiredTiger storage-engine code directly.

## Risks and Edge Cases

- SELECT codegen is high-risk because many optimizations mutate the AST in place. Incorrect HAVING pushdown, ORDER BY omission, subquery flattening, coroutine choice, or count-of-view rewriting can silently change query results.
- Aggregate handling is sensitive to first-row behavior, min/max accumulator "magnet" registers, FILTER clauses, DISTINCT aggregate handling, and ORDER BY aggregate sorters. Register or label mistakes can produce wrong aggregates only for narrow query shapes.
- GROUP BY code has two paths: naturally grouped planner output and sorter-backed grouping. Bugs can appear only when planner ordering changes, when DISTINCT combines with GROUP BY, or when ORDER BY is considered redundant.
- Trigger code must carefully duplicate parse trees or retain originals during ALTER TABLE rename processing. Ownership mistakes lead to leaks, double frees, or stale rename-token mappings.
- RETURNING is implemented as a synthetic trigger but generated inline. It must only run for the current statement and must correctly expand `*`, reject `TABLE.*`, resolve self-referencing subqueries as variable, and avoid firing in nested statements where disallowed.
- UPDATE one-pass optimization is correctness-sensitive. It deliberately falls back when triggers, FKs, key changes, REPLACE, nested updates, subqueries, or updated scan indexes might invalidate the current cursor or cause loops.
- UPDATE-FROM uses ephemeral tables to separate row discovery from modification. Wrong primary-key/rowid packing can update the wrong row or mishandle duplicate join matches.
- Generated columns are not directly updatable but may become implicitly changed by dependencies. Missed dependency propagation can leave stored/generated values or constraints inconsistent.
- WITHOUT ROWID paths use composite PK records and index cursors instead of rowid. Many UPDATE, UPSERT, and virtual-table paths have separate handling and stricter assumptions.
- `sqlite3_get_table()` stores metadata before the returned pointer. Any caller freeing it directly or passing an offset pointer other than the returned value will corrupt memory; the code relies on `sqlite3_free_table()`.
- VACUUM executes SQL text from `sqlite_schema` but restricts recursive generated statements to CREATE/INSERT prefixes. Any relaxation there would re-open historical schema-corruption attack surfaces.
- VACUUM temporarily disables defensive mode, FKs, checks, count rows, and tracing. Failure exits must restore every saved flag and close the transient database; leaks here would affect subsequent statements on the same connection.
- Virtual table constructor handling is reentrancy-sensitive. Recursive constructor calls return `SQLITE_LOCKED`, and constructors must call `sqlite3_declare_vtab()`. Bad reference counts can leak modules or disconnect live vtabs.
- Virtual table transaction/savepoint callbacks run while manipulating `db->aVTrans`; writes during xSync are explicitly rejected by `sqlite3VtabInSync()` behavior checked in `sqlite3VtabBegin()`.
- Security/risk flags from `sqlite3_vtab_config()` affect whether a vtab is treated as innocuous, direct-only, all-schema-using, or constraint-supporting. Incorrect propagation can alter trusted-schema and planner behavior.

## Test and Validation Signals

Useful validation for this chunk should exercise SQL behavior rather than line-level unit tests:

- SELECT regression suites covering subquery flattening, FROM-subquery materialization, coroutine subqueries, self-joined views, CTE materialization hints, UPDATE-FROM alias rejection, DISTINCT ORDER BY rewrite, GROUP BY sorting vs index grouping, HAVING pushdown, min/max optimization, simple count optimization, window-rewritten SELECTs, and aggregate FILTER/DISTINCT/ORDER BY combinations.
- `sqlite3_get_table()` tests for zero rows, column-name row construction, NULL values, multiple statements with incompatible column counts, callback abort, OOM paths, and correct `sqlite3_free_table()` behavior.
- Trigger tests for TEMP triggers, orphan TEMP triggers during schema load, triggers on views vs tables, virtual/shadow/system table restrictions, CREATE/DROP schema updates, BEFORE trigger row deletion/modification, UPDATE OF column filtering, recursive-trigger configuration, conflict policy inheritance, and trigger subprogram reuse.
- RETURNING tests for INSERT/UPDATE/DELETE, UPSERT UPDATE firing, wildcard expansion, rejection of `TABLE.*`, virtual table restrictions, subqueries that reference the modified table, generated column expressions, and nested trigger interactions.
- UPDATE tests for rowid changes, INTEGER PRIMARY KEY aliases, WITHOUT ROWID primary key changes, generated columns, partial/expression index updates, REPLACE conflicts, foreign keys, pre-update hook behavior, UPDATE-FROM, limited UPDATE builds, one-pass vs two-pass plans, and views with INSTEAD OF triggers.
- Virtual table UPDATE tests for one-pass and ephemeral strategies, rowid and WITHOUT ROWID virtual tables, `sqlite3_vtab_nochange()`, conflict policy reporting, `xUpdate` error propagation, and writable marking via `OP_VBegin`.
- UPSERT tests for rowid targets, unique indexes, expression indexes, partial unique indexes, duplicate ON CONFLICT clauses, unmatched conflict targets, DO NOTHING vs DO UPDATE, and seeking from secondary unique indexes to table rows.
- VACUUM tests for ordinary VACUUM, VACUUM INTO existing/non-text output paths, WAL page-size behavior, autovacuum/page-size metadata preservation, schema cookie increment, corrupted schema SQL safety, in-transaction rejection, active-statement rejection, and cleanup after attach/copy failures.
- Virtual table API tests for module registration/replacement/drop, destructor invocation on failed registration, `sqlite3_declare_vtab()` misuse and syntax validation, hidden-column parsing, eponymous virtual tables, recursive constructor locking, `xDestroy` lock handling, xSync/xCommit/xRollback/xSavepoint ordering, xFindFunction overloads, and `sqlite3_vtab_config()` option handling.

## Chunk Boundary Notes

The chunk begins inside aggregate accumulator update generation, so surrounding setup for `updateAccumulator()` and related `AggInfo` helpers is in the previous chunk. It ends after the `wherecode.c` and `whereInt.h` opening comments, before the WHERE planner/codegen structures and routines continue. The later merge lane should connect this report with adjacent chunks to present whole-file SELECT/update/where interactions coherently.

### subset-b-009033: lines 158972-165680

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 158972-165680

## Scope

This chunk covers SQLite's internal WHERE-planner interface (`whereInt.h`), the tail of `wherecode.c`, all of `whereexpr.c` in this slice, and the beginning of `where.c` through the opening of `constructAutomaticIndex()`. It is part of the vendored SQLite amalgamation under WiredTiger test third-party sources, so the code is SQLite query planner and VDBE code-generation logic rather than WiredTiger storage-engine code.

The range begins with planner data structures and bit flags, proceeds through VDBE generation for one WHERE loop, expression decomposition and optimization-term synthesis, WHERE-clause memory/scanner utilities, DISTINCT redundancy detection, cursor/debug helpers, outer-join compatibility checks, and the first half of automatic-index setup. The final line ends mid-call to `sqlite3GenerateIndexKey()` inside `constructAutomaticIndex()`, so automatic-index population and cleanup are completed by the following chunk.

## Purpose

The code turns SQL `WHERE` and join predicates into a planner-internal representation, then emits VDBE bytecode for the selected loop plan. The main responsibilities in this range are:

- Representing candidate loops (`WhereLoop`), chosen nested-loop implementation state (`WhereLevel`), paths through the join graph (`WherePath`), decomposed WHERE terms (`WhereTerm`/`WhereClause`), cursor-to-bitmask mappings (`WhereMaskSet`), OR-cost alternatives (`WhereOrSet`), and planner-wide state (`WhereInfo`).
- Defining planner operator masks (`WO_*`) and selected-loop flags (`WHERE_*`) that drive later planning and code generation.
- Producing `EXPLAIN QUERY PLAN`, Bloom-filter explain text, and `sqlite3_stmt_scanstatus()` ranges for generated scans.
- Emitting VDBE loop prologues for virtual tables, rowid equality/range scans, ordinary index scans, multi-index OR plans, full scans, skip-scan, `IN` loops, Bloom filters, deferred seeks, cursor hints, LIKE/GLOB range rewrites, partial-index implication, and outer joins.
- Analyzing WHERE expressions into planner-usable terms, including commuted comparisons, BETWEEN-derived ranges, OR decomposition, OR-to-IN transformations, `IS NOT NULL` virtual ranges, LIKE/GLOB prefix ranges, row-value/vector slices, vector `IN` slices, virtual-table auxiliary constraints, LIMIT/OFFSET pseudo-constraints, and table-valued-function hidden-column constraints.
- Providing the public file-scope interfaces used by the wider planner: row-count/order/distinct/one-pass query answers, WHERE break/continue labels, term lookup, memory lifetime helpers, and start of automatic-index construction.

## Important APIs And Types

Planner state types introduced or defined in `whereInt.h`:

- `WhereMemBlock` chains scratch allocations owned by a `WhereInfo`; `sqlite3WhereMalloc()` and `sqlite3WhereRealloc()` attach these blocks to `pWInfo->pMemToFree`.
- `WhereRightJoin` carries RIGHT JOIN match tracking: `iMatch` ephemeral index, `regBloom` Bloom filter, `regReturn`, and subroutine address bounds.
- `WhereLevel` is the concrete implementation state for one chosen nested loop: table/index cursors, break/continue/next labels, LIKE and big-null loop state, Bloom-filter register, right/left join state, selected `WhereLoop`, not-ready mask, and `IN`-loop metadata.
- `WhereLoop` describes a candidate access algorithm: prerequisites, table bit, cost estimates, btree or virtual-table access details, `wsFlags`, associated `WhereTerm` pointers, and optional trace metadata.
- `WherePath` is the solver path through chosen `WhereLoop` objects, with accumulated row/cost/order information.
- `WhereTerm` represents one analyzed predicate. Important fields are `pExpr`, `wtFlags`, `eOperator`, `leftCursor`, `u.x.leftColumn`/`iField`, `prereqRight`, and `prereqAll`.
- `WhereClause` owns a flat array of `WhereTerm` objects for an AND or OR split, with static inline space and optional outer-clause links.
- `WhereOrInfo` and `WhereAndInfo` hold nested decomposed subclauses for compound terms.
- `WhereMaskSet` maps sparse VDBE cursor IDs into dense `Bitmask` bits. This is the source of the default 64-table join limit.
- `WhereLoopBuilder` is the construction context for candidate loops, with STAT4 probe state when enabled and `iPlanLimit` throttling pathological index/constraint combinations.
- `WhereInfo` is the planner-wide state returned by `sqlite3WhereBegin()` and consumed by `sqlite3WhereEnd()`: parse context, FROM list, order/result lists, one-pass cursors, loop labels, selected levels, row estimates, order/distinct results, memory chain, main `WhereClause`, and cursor mask set.

Important flags and constants:

- `TERM_*` flags control predicate lifecycle and generated terms: dynamic expression ownership, virtual/derived terms, already-coded terms, parent-child relationships, OR/AND subinfo ownership, LIKE optimization state, correlated subquery tracking, row-value slices, and null-range virtual terms.
- `WO_*` flags encode indexable operators and planner-only categories: `WO_IN`, `WO_EQ`, inequalities, `WO_AUX`, `WO_IS`, `WO_ISNULL`, `WO_OR`, `WO_AND`, `WO_EQUIV`, `WO_NOOP`, and `WO_ROWVAL`.
- `WHERE_*` flags describe selected loop algorithms and constraints: equality/range/IN/null constraints, top/bottom range bounds, covering index use, integer-primary-key access, virtual-table access, multi-index OR, automatic index, skip-scan, partial index, IN early-out/seek-scan, transitive constraints, Bloom filters, coroutine access, and expression-index use.
- `N_OR_COST` is fixed at 3, keeping only the best few OR-subplan cost alternatives.
- `SQLITE_QUERY_PLANNER_LIMIT` and `SQLITE_QUERY_PLANNER_LIMIT_INCR` cap candidate generation to avoid runaway planning.

Key functions in this chunk:

- Explain and instrumentation: `explainIndexColumnName()`, `explainAppendTerm()`, `explainIndexRange()`, `sqlite3WhereAddExplainText()`, `sqlite3WhereExplainOneScan()`, `sqlite3WhereExplainBloomFilter()`, `sqlite3WhereAddScanStatus()`, `whereTraceIndexInfoInputs()`, and `whereTraceIndexInfoOutputs()`.
- Loop-code helpers: `disableTerm()`, `codeApplyAffinity()`, `updateRangeAffinityStr()`, `adjustOrderByCol()`, `removeUnindexableInClauseTerms()`, `codeINTerm()`, `codeEqualityTerm()`, `codeAllEqualityTerms()`, `whereLikeOptimizationStringFixup()`, `codeCursorHint()`, `codeDeferredSeek()`, `codeExprOrVector()`, `whereApplyPartialIndexConstraints()`, `filterPullDown()`, and `whereLoopIsOneRow()`.
- Main loop codegen: `sqlite3WhereCodeOneLoopStart()` and `sqlite3WhereRightJoinLoop()`.
- WHERE expression analysis: `whereOrInfoDelete()`, `whereAndInfoDelete()`, `whereClauseInsert()`, `allowedOp()`, `exprCommute()`, `operatorMask()`, `isLikeOrGlob()`, `isAuxiliaryVtabOperator()`, `transferJoinMarkings()`, `markTermAsChild()`, `whereNthSubterm()`, `whereCombineDisjuncts()`, `exprAnalyzeOrTerm()`, `termIsEquivalence()`, `exprSelectUsage()`, `exprMightBeIndexed()`, and `exprAnalyze()`.
- Public where-expression utilities: `sqlite3WhereSplit()`, `whereAddLimitExpr()`, `sqlite3WhereAddLimit()`, `sqlite3WhereClauseInit()`, `sqlite3WhereClauseClear()`, `sqlite3WhereExprUsageNN()`, `sqlite3WhereExprUsage()`, `sqlite3WhereExprListUsage()`, `sqlite3WhereExprAnalyze()`, and `sqlite3WhereTabFuncArgs()`.
- Beginning of `where.c`: `sqlite3WhereOutputRowCount()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereIsOrdered()`, `sqlite3WhereOrderByLimitOptLabel()`, `sqlite3WhereMinMaxOptEarlyOut()`, `sqlite3WhereContinueLabel()`, `sqlite3WhereBreakLabel()`, `sqlite3WhereOkOnePass()`, `sqlite3WhereUsesDeferredSeek()`, `whereOrMove()`, `whereOrInsert()`, `sqlite3WhereGetMask()`, `sqlite3WhereMalloc()`, `sqlite3WhereRealloc()`, `createMask()`, `whereRightSubexprIsColumn()`, `indexInAffinityOk()`, `whereScanNext()`, `whereScanInit()`, `sqlite3WhereFindTerm()`, `findIndexCol()`, `indexColumnNotNull()`, `isDistinctRedundant()`, `estLog()`, `translateColumnToCopy()`, `constraintCompatibleWithOuterJoin()`, `columnIsGoodIndexCandidate()`, `termCanDriveIndex()`, `explainAutomaticIndex()`, and the opening part of `constructAutomaticIndex()`.

## Control Flow

The data flow starts with `sqlite3WhereSplit()`, which recursively decomposes an expression tree into `WhereClause.a[]` entries by AND or OR separators. `sqlite3WhereExprAnalyze()` then invokes `exprAnalyze()` for each term. Analysis computes dependency bitmasks, recognizes indexable operators, normalizes comparison direction with `exprCommute()`, adds commuted virtual copies for column-to-column comparisons, identifies equivalence terms for transitive use, and attaches operator masks used by later scans.

Expression analysis also synthesizes additional terms. BETWEEN becomes two range comparisons. `x IS NOT NULL` can become a virtual `x>NULL` term. LIKE/GLOB with a constant or currently bound prefix becomes lower/upper range terms and may mark the original function term skippable when the prefix is complete. Row-value equality/IS terms become per-column slice terms and disable the original row-value expression. Vector `IN (SELECT...)` terms become per-field virtual terms when the RHS is a simple select. OR terms are recursively analyzed, record the set of indexable tables, may combine disjuncts, and may be transformed into an equivalent virtual `IN` term when every disjunct compares the same table column/expression to compatible RHS values.

After the planner selects loops, `sqlite3WhereCodeOneLoopStart()` emits bytecode for one `WhereLevel`. It initializes labels, left-join match registers, right-join safe break addresses, and then selects one of several access paths based on `WhereLoop.wsFlags`:

- Coroutine subquery tables initialize and yield from the subquery fill program.
- Virtual tables allocate argument registers, code constraints, handle virtual-table-managed `IN`, emit `OP_VFilter`, install `OP_VNext`, and conditionally recheck `IN` constraints that the virtual table did not accept as handled.
- Rowid equality or rowid `IN` paths code a single equality value, optionally run a Bloom filter and inner filter pull-down, then `OP_SeekRowid`.
- Rowid range paths choose seek operations from the expression operator, code start/end values, handle forward/reverse scans, and install rowid end tests.
- Ordinary index paths code equality and `IN` values, optional skip-scan prefixes, LIKE range fixups, seek-scan, big-null two-pass handling, Bloom filters, start and end index seeks, deferred table seeks, WITHOUT ROWID PK lookups, partial-index constraint elimination, and the terminating `OP_Next`/`OP_Prev`/`OP_Noop`.
- Multi-index OR plans recursively call `sqlite3WhereBegin()` for each OR branch, use a RowSet for rowid tables or an ephemeral PK index for WITHOUT ROWID tables to suppress duplicates, invoke the outer loop body through `OP_Gosub`, and keep a candidate covering index only if every OR branch uses the same index cursor.
- Full scans issue `OP_Rewind`/`OP_Last` and `OP_Next`/`OP_Prev` unless the source is a recursive pseudo-cursor.

After the access path is opened, `sqlite3WhereCodeOneLoopStart()` codes residual WHERE terms in priority passes: terms covered by an index first, then non-correlated terms, then correlated subquery terms. It observes outer-join markings so ON-clause constraints and WHERE-clause constraints are evaluated at the correct phase. It also codes transitive constraints such as using `t1.a=123` when the original terms imply `t1.a=t2.b` and `t2.b=123`.

RIGHT JOIN handling has two phases. During ordinary matched-row processing, the code records the right-table PK/rowid in `WhereRightJoin.iMatch` and `regBloom`. For unmatched rows, `sqlite3WhereRightJoinLoop()` nulls all tables to the left, builds a one-table sub-WHERE for the right table, scans right rows, skips those found by the Bloom filter/match index, and calls the saved right-join subroutine for rows that had no match.

The `where.c` utilities expose planner answers after loop selection. `sqlite3WhereIsOrdered()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereOutputRowCount()`, `sqlite3WhereOkOnePass()`, and label helpers are read-side APIs used by SELECT/UPDATE/DELETE code generation. `whereScanInit()` and `whereScanNext()` implement the core term search primitive used by index matching and DISTINCT redundancy checks; they walk equivalence chains up to the fixed `WhereScan.aiCur[]`/`aiColumn[]` capacity.

The automatic-index setup begins by checking equality/IS terms with `termCanDriveIndex()`, rejecting terms from the wrong cursor, unsafe outer-join terms, not-ready RHS dependencies, non-column/expression columns, and affinity-incompatible terms. `constructAutomaticIndex()` emits `OP_Once`, gathers driving columns, logs `SQLITE_WARNING_AUTOINDEX`, marks the selected `WhereLoop` as `WHERE_AUTO_INDEX | WHERE_INDEXED | WHERE_IDX_ONLY`, adds all extra columns required for a covering index, creates an ephemeral `Index` object and `OP_OpenAutoindex`, optionally creates a Bloom filter, then starts scanning either the source table or coroutine to fill the transient index. The chunk ends at the call that generates index keys for that fill loop.

## State And Persistence Behavior

Most state here is per-prepare, per-statement planner state rather than database persistence. `WhereInfo`, `WhereClause`, `WhereLevel`, `WhereLoop`, and `WhereScan` are transient and live only while compiling a statement. `sqlite3WhereMalloc()` chains allocations to `WhereInfo` so they are freed when the WHERE object is destroyed; this is important because `whereClauseInsert()` may reallocate `WhereTerm` arrays and invalidate raw term pointers.

The code emits VDBE state that persists for the lifetime of the prepared statement execution. Examples include registers for equality values, `IN` loop state, left-join match flags, RIGHT JOIN match indexes and Bloom filters, cursor-hint expressions, scanstatus metadata, RowSets/ephemeral indexes for OR duplicate elimination, and automatic index cursors. These are runtime structures inside the VDBE, not durable database objects.

Automatic indexes are query-time transient btrees. `constructAutomaticIndex()` allocates an `Index` descriptor with name `"auto-index"`, opens it with `OP_OpenAutoindex`, fills it from the source table or subquery coroutine, and forces it to be covering because it is not maintained if the base table changes during statement execution. It may also create a partial automatic index by combining single-table constraints and setting `WHERE_PARTIALIDX`.

Outer-join state is correctness-critical. LEFT JOINs use a memory cell to remember whether the right side matched. RIGHT JOINs use a match index and Bloom filter keyed by right-table PK/rowid. Predicate disabling and cursor hints explicitly avoid pushing unsafe WHERE constraints below outer-join null-extension points.

## Dependencies

This slice depends heavily on SQLite internal planner, parser, expression, table/index, and VDBE APIs:

- Parser and schema objects: `Parse`, `Select`, `SrcList`, `SrcItem`, `Table`, `Index`, `Expr`, `ExprList`, `CollSeq`, `Subquery`, `UnpackedRecord`, and `sqlite3`.
- Expression analysis/codegen: `sqlite3WhereExprUsage*()`, `sqlite3ExprCode*()`, `sqlite3ExprCompare*()`, `sqlite3ExprAffinity()`, `sqlite3IndexAffinityOk()`, `sqlite3ExprIsVector()`, `sqlite3ExprForVectorField()`, `sqlite3ExprDup()`, `sqlite3PExpr()`, `sqlite3ExprAnd()`, `sqlite3ExprIfFalse()`, `sqlite3ExprCanBeNull()`, and `sqlite3CodeSubselect()`.
- VDBE construction: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, `sqlite3VdbeGetOp()`, `sqlite3VdbeGetLastOp()`, `sqlite3VdbeCurrentAddr()`, `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeSetP4KeyInfo()`, `sqlite3VdbeScanStatus*()`, and many opcodes such as `OP_Explain`, `OP_VFilter`, `OP_SeekRowid`, `OP_SeekGE`, `OP_IdxGE`, `OP_DeferredSeek`, `OP_Filter`, `OP_FilterAdd`, `OP_RowSetTest`, `OP_OpenEphemeral`, and `OP_OpenAutoindex`.
- Planner options and compile-time switches: `SQLITE_OMIT_EXPLAIN`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_OR_OPTIMIZATION`, `SQLITE_OMIT_LIKE_OPTIMIZATION`, `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_STAT4`, `SQLITE_OMIT_AUTOMATIC_INDEX`, and `WHERETRACE_ENABLED`.
- Runtime knobs and heuristics: `SQLITE_CursorHints`, `SQLITE_BloomFilter`, `SQLITE_Transitive`, `SQLITE_EnableQPSG`, `SQLITE_WARNING_AUTOINDEX`, `SQLITE_STMTSTATUS_FULLSCAN_STEP`, and `SQLITE_STMTSTATUS_AUTOINDEX`.
- Virtual table API contracts: `sqlite3_index_info`, `xBestIndex` constraint/operator codes, `sqlite3_vtab_collation()`, `sqlite3_vtab_rhs_value()`, and virtual-table `LIMIT`/`OFFSET` pseudo-constraints.

## Integration Points

This code is the glue between high-level SQL compilation and low-level VDBE execution. SELECT, UPDATE, DELETE, aggregate/min-max, DISTINCT, ORDER BY, LIMIT, virtual table, table-valued function, and outer join code generation all consume the planner state and labels produced here.

Virtual tables integrate in two places. Expression analysis creates `WO_AUX` terms for MATCH/LIKE/GLOB/REGEXP, `!=`, `IS NOT`, and `IS NOT NULL` forms that ordinary btree planning does not use but `xBestIndex` may. Loop code then passes selected constraints through `OP_VFilter`, supports virtual-table-managed `IN` terms, rechecks unhandled `IN` values, and can push `LIMIT`/`OFFSET` values with `sqlite3WhereAddLimit()`.

Indexes integrate through `WhereScan`, affinity/collation checks, expression-index matching, skip-scan support, partial-index implication, deferred seek, covering-index detection, DISTINCT redundancy checks, and automatic-index construction. The `findIndexCol()`/`indexColumnNotNull()`/`isDistinctRedundant()` path lets the SELECT layer suppress DISTINCT work when uniqueness and nullability prove it redundant.

Instrumentation surfaces are integrated directly into planner output. `EXPLAIN QUERY PLAN` receives human-readable scan text, Bloom-filter text, and OR-branch labels. `sqlite3_stmt_scanstatus()` receives scan ranges and row estimates, including special handling for coroutine sources and automatic index explain records.

WiredTiger's repository consumes this as vendored SQLite test infrastructure. Behavioral changes in this area would affect any SQLite-backed test utility or imported SQLite conformance behavior, but not WiredTiger's production storage engine directly unless the vendored SQLite is executed by tests.

## Risks And Edge Cases

- The planner relies on many bit flags with overlapping semantics. Incorrect `TERM_CODED`, `TERM_VIRTUAL`, `WO_EQUIV`, `WHERE_IDX_ONLY`, or outer-join markings can silently produce wrong answers rather than crashes.
- Outer joins are especially sensitive. The code deliberately defers WHERE constraints until after null-extension, rejects unsafe automatic-index terms with `constraintCompatibleWithOuterJoin()`, and excludes unsafe cursor hints. Reordering or over-disabling terms can change LEFT/RIGHT/FULL JOIN semantics.
- Transitive constraints are guarded by affinity, collation, and join checks. Returning true from `termIsEquivalence()` too broadly risks substituting values where SQL comparison semantics differ.
- LIKE/GLOB optimization has many text encoding and numeric-affinity pitfalls. The prefix range optimization is disabled for malformed UTF-8, UTF16LE-sensitive cases, numeric-looking prefixes on non-TEXT left sides, and complete-prefix edge cases. The two-pass BLOB/string logic depends on `SQLITE_LIKE_DOESNT_MATCH_BLOBS`.
- Vector and row-value optimization is deliberately limited. Vector `IN` slicing only supports simple non-window SELECT RHS cases, and OR pushdown skips row-value slices and subqueries to avoid uninitialized RHS values or invalid index cursor references inside subroutines.
- `whereClauseInsert()` may reallocate the term array. Callers must refresh `WhereTerm *` pointers after insertion; many comments and local resets exist because stale pointers would corrupt planning.
- `WhereMaskSet` depends on the fixed `Bitmask` width. Joins over the supported table count must be rejected before mask overflow; equivalence scanning also has a fixed 11-entry chain limit.
- Multi-index OR duplicate suppression differs for rowid and WITHOUT ROWID tables. RowSet and ephemeral PK index behavior must stay aligned, especially when `WHERE_DUPLICATES_OK` is set.
- Deferred seeks and covering-index substitutions are disabled or adjusted in write statements and OR/RIGHT JOIN subclauses. Enabling them too broadly could read columns from an index when the table cursor is required.
- Automatic indexes are intentionally covering and transient. If a generated automatic index omitted a needed column or failed to include WITHOUT ROWID primary-key columns, subsequent code could read stale or unavailable data.
- Automatic-index Bloom filters are heuristic and only enabled for non-TEXT-capable key columns. Incorrect hashing assumptions or filter placement could cause performance regressions; false negatives would be correctness bugs.
- The chunk ends before `constructAutomaticIndex()` finishes. Research consumers should combine this document with the following chunk before assessing full automatic-index population, `OP_FilterAdd`, scanstatus counters, cleanup, and error paths.

## Test Signals

Useful validation signals for this code include:

- SQLite planner regression tests covering EXPLAIN QUERY PLAN text for full scans, covering index scans, automatic covering/partial indexes, virtual tables, Bloom filters, rowid scans, skip-scans, multi-index OR, and LEFT/RIGHT JOINs.
- `sqlite3_stmt_scanstatus()` tests for normal table/index scans, coroutine subqueries, automatic indexes, Bloom filters, and OR subplans.
- WHERE expression tests for commuted comparisons, column equivalence/transitive constraints, incompatible affinities/collations, `IS` versus `=`, `IS NULL` on non-null columns, BETWEEN virtual terms, row-value equality, vector `IN`, OR-to-IN conversion, OR duplicate suppression, and expression indexes.
- LIKE/GLOB optimization tests for case-sensitive and case-insensitive patterns, bound parameters and repreparation, escaped wildcards, malformed UTF-8, UTF16LE databases, numeric-looking prefixes, BLOB behavior with and without `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, and complete-prefix skipping.
- Outer join tests ensuring ON-clause and WHERE-clause terms are evaluated at the correct phase for LEFT, RIGHT, and mixed left-to-right joins, including constraints that imply non-null values on the wrong side.
- Virtual-table tests for `xBestIndex` inputs and outputs, auxiliary operators, handled and unhandled `IN` constraints, `LIMIT`/`OFFSET` pseudo-constraints, collation names, and omitted constraints.
- Automatic-index tests for warning logs, covering-column selection, WITHOUT ROWID primary-key inclusion, partial automatic indexes, coroutine-backed subqueries, Bloom-filter creation, affinity/collation checks, and unsafe outer-join term rejection.
- Fuzz and TH3-style tests around pointer invalidation after virtual-term insertion, nested OR/AND decomposition, subqueries in OR branches, cursor-hint safety, deferred seek with OR branches, and DISTINCT redundancy with unique non-null indexes.

### subset-b-009034: lines 165681-172668

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 165681-172668

## Scope

This chunk covers the end of SQLite's `where.c` implementation and the beginning of `window.c` inside the amalgamated SQLite source vendored under WiredTiger tests. The range starts in the tail of automatic-index construction, includes most of the query planner loop enumeration, costing, order-by analysis, `sqlite3WhereBegin()`, and `sqlite3WhereEnd()`, then transitions into the window-function module comments and the first built-in window-function aggregate callbacks through the beginning of `last_valueInvFunc()`.

The code is compiled conditionally by feature macros such as `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_ENABLE_STAT4`, `WHERETRACE_ENABLED`, `SQLITE_OMIT_WINDOWFUNC`, and several debug/test configuration flags. It is not WiredTiger-specific logic; it is the upstream SQLite query planner and bytecode generator used by the embedded SQLite test dependency.

## Purpose

The `where.c` portion builds and executes SQLite's low-level plan for scanning tables in a `SELECT`, `UPDATE`, or `DELETE` statement. It:

- Describes available access paths as `WhereLoop` objects for ordinary b-tree tables, rowid lookups, indexes, automatic indexes, skip-scans, virtual tables, and multi-index OR scans.
- Estimates row counts and costs using `sqlite_stat1` and optional STAT4 samples.
- Chooses a nested-loop order with a bounded dynamic-programming solver.
- Determines whether an access path satisfies `ORDER BY`, `GROUP BY`, or `DISTINCT`.
- Opens table/index/virtual-table cursors and emits VDBE bytecode for loop starts and loop endings.
- Applies optimizations such as Bloom filters, covering-index opcode rewrites, omitted no-op LEFT JOIN tables, one-pass UPDATE/DELETE, reverse unordered scan order, automatic indexes, and indexed-expression substitution.

The `window.c` portion begins the window-function subsystem. The comments document how window queries are rewritten into ordered subqueries and how `select.c` drives `sqlite3WindowCodeStep()`. The executable code in this chunk implements state and callbacks for built-in window functions including `row_number`, `dense_rank`, `nth_value`, `first_value`, `rank`, `percent_rank`, `cume_dist`, `ntile`, and the start of `last_value`.

## Important APIs, Types, and Functions

### Bloom Filters and Automatic Index Tail

- `sqlite3ConstructBloomFilter(WhereInfo *pWInfo, int iLevel, WhereLevel *pLevel, Bitmask notReady)` emits one-time VDBE setup for a Bloom filter register. It creates an `OP_Blob` sized from `Table.nRowLogEst`, scans the table/index cursor, filters rows by single-table constraints, and adds rowid or index-prefix keys using `OP_FilterAdd`.
- The preceding automatic-index tail inserts computed records with `OP_IdxInsert`, optionally populates a Bloom filter from automatic-index keys, handles coroutine subqueries through `translateColumnToCopy()`, and records scan-status counters.

### Virtual Table Planning

- `termFromWhereClause()` maps the flattened `sqlite3_index_constraint.iTermOffset` back to a `WhereTerm`, walking outer `WhereClause` chains.
- `allocateIndexInfo()` allocates `sqlite3_index_info` plus a trailing `HiddenIndexInfo`, constraint arrays, order-by arrays, usage arrays, and cached RHS slots. It marks usable virtual-table constraints, maps SQLite `WO_*` operators to public `SQLITE_INDEX_CONSTRAINT_*` codes, exposes `colUsed`, order-by terms, `eDistinct`, and IN-clause metadata.
- `freeIdxStr()` and `freeIndexInfo()` release `idxStr`, cached RHS `sqlite3_value` objects, and the packed allocation.
- `vtabBestIndex()` invokes `xBestIndex()`, brackets the call with schema-lock accounting, reports module errors, propagates OOM, and handles virtual tables that require all schemas.
- `whereLoopAddVirtualOne()` performs one `xBestIndex()` attempt for a chosen usable-constraint mask, validates returned `argvIndex` values, handles omit masks, IN constraints, LIMIT/OFFSET retry behavior, order consumption, unique-scan flags, and inserts the resulting `WhereLoop`.
- `whereLoopAddVirtual()` calls `xBestIndex()` repeatedly with all constraints, without IN, with selected prerequisite masks, and with all external terms disabled, ensuring at least one globally usable plan exists.
- Public virtual-table helper APIs implemented here are `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, and `sqlite3_vtab_distinct()`.
- `sqlite3VtabUsesAllSchemas()` verifies or starts transactions on every attached schema when a virtual table needs cross-schema visibility.

### STAT4 and Cost Estimation

- `whereKeyStats()` binary-searches STAT4 samples and effective prefixes to estimate rows less than and equal to an `UnpackedRecord`.
- `whereRangeAdjust()` applies likelihood and default range-selectivity heuristics.
- `sqlite3IndexColumnAffinity()` returns index-column affinity for STAT4 probing.
- `whereRangeSkipScanEst()` estimates skip-scan range selectivity by comparing lower/upper extracted values against STAT4 sample columns.
- `whereRangeScanEst()` adjusts `WhereLoop.nOut` for range scans using STAT4 when possible, including descending-index bound swapping, vector bound probing, fallback open/closed range heuristics, and default 1/4 or 1/64 selectivity.
- `whereEqualScanEst()` and `whereInScanEst()` estimate equality and list-IN result sizes from STAT4 histograms.
- `whereLoopOutputAdjust()` reduces output estimates for post-index WHERE terms, using explicit `likelihood()` values, self-culling flags, and heuristics for equality-like predicates.

### WhereLoop Lifecycle and Enumeration

- Debug helpers `sqlite3WhereTermPrint()`, `sqlite3WhereClausePrint()`, `sqlite3WhereLoopPrint()`, and related show functions emit planner diagnostics when tracing is compiled in.
- `whereLoopInit()`, `whereLoopClearUnion()`, `whereLoopClear()`, `whereLoopResize()`, `whereLoopXfer()`, `whereLoopDelete()`, and `whereInfoFree()` manage planner objects and their owned arrays, automatic indexes, virtual-table `idxStr` allocations, and `WhereInfo` memory blocks.
- `whereLoopCheaperProperSubset()` and `whereLoopAdjustCost()` enforce monotonic cost relationships between loops that use subsets/supersets of the same constraints.
- `whereLoopFindLesser()` and `whereLoopInsert()` prune dominated loops, replace inferior loops, track OR-subplan costs in `WhereOrSet`, and enforce the planner search limit.
- `whereRangeVectorLen()` determines how many vector inequality components can be used with the current index prefix.
- `whereLoopAddBtreeIndex()` recursively builds constrained b-tree loops for equality, `IS`, `IS NULL`, IN, range, LIKE-optimized ranges, vector ranges, and skip-scans. It computes run costs, seek multipliers for IN, STAT4 estimates, one-row flags, transitive-constraint flags, and optional seek-scan handling for large IN lists.
- `indexMightHelpWithOrderBy()`, `whereUsablePartialIndex()`, `exprIsCoveredByIndex()`, `whereIsCoveringIndexWalkCallback()`, `whereIsCoveringIndex()`, `wherePartIdxExpr()`, and `whereAddIndexedExpr()` support covering-index detection, partial-index implication, expression-index substitution, and generated-column/expression index handling.
- `whereLoopAddBtree()` adds full scans, covering/non-covering index scans, rowid fake-index scans, automatic-index loops, partial-index loops, and all constrained index loops for one b-tree table.
- `whereLoopAddOr()` recursively builds subplans for OR terms and combines their costs into `WHERE_MULTI_OR` loops.
- `whereLoopAddAll()` iterates FROM terms, applies join-order barriers for CROSS/outer/RIGHT joins, calls b-tree or virtual-table loop builders, and adds OR loops.

### Order, Sorting, and Path Solving

- `wherePathMatchSubqueryOB()` lets an ordered materialized subquery or CTE satisfy an outer `ORDER BY` prefix when result columns and directions line up.
- `wherePathSatisfiesOrderBy()` tests whether a candidate path and appended loop satisfy `ORDER BY`, `GROUP BY`, or `DISTINCT`, including equality-constrained order terms, virtual-table ordering, unique/order-distinct loops, expression-index columns, collation matching, reverse-scan masks, NULLS ordering, and block-sort prefixes.
- `sqlite3WhereIsSorted()` reports whether `WHERE_SORTBYGROUP` planning actually preserves sorted order.
- `whereSortingCost()` estimates full or partial sort cost, accounting for row count, number of output columns, LIMIT, and DISTINCT.
- `computeMxChoice()` chooses solver beam width and applies the star-schema heuristic. For detected fact/dimension star queries it raises full-scan costs of dimension tables so fact-table outer-loop paths are not pruned too early.
- `whereLoopIsNoBetter()` breaks exact ties between indexed loops by preferring smaller index rows.
- `wherePathSolver()` is the bounded dynamic-programming join-order solver. It allocates path buffers on the stack, iteratively extends paths with legal `WhereLoop` candidates, includes setup/run/sort costs, keeps at most `mxChoice` best paths, then installs the selected loops into `WhereInfo.a[]`, sets order/distinct metadata, row estimates, reverse masks, and ordered-inner-loop flags.
- `whereInterstageHeuristic()` runs between the two solver passes and disables full scans for tables already chosen with indexed equality constraints, preventing an ORDER BY-oriented second pass from replacing a selective search with a dangerous full scan.
- `whereShortCut()` handles the simplest one-table primary-key or unique-index equality lookups without running the full planner.

### WHERE Bytecode Generation and Cleanup

- `exprNodeIsDeterministic()` and `exprIsDeterministic()` support the false-WHERE-term bypass by rejecting non-deterministic scalar functions while ignoring subselect contents.
- `whereOmitNoopJoin()` removes unused LEFT JOIN RHS tables when the result, ordering, and ON/USING terms prove they cannot affect output.
- `whereCheckIfBloomFilterIsUseful()` marks equality search loops for Bloom-filter construction when earlier loops imply many lookups into a smaller self-culling table with statistics.
- `whereReverseScanOrder()` implements `reverse_unordered_selects` by setting reverse bits except for materialized CTEs with their own ordering.
- `sqlite3WhereBegin()` is the main planner/codegen entry point. It allocates `WhereInfo`, splits/analyzes WHERE terms, adds LIMIT constraints, handles constant false terms, configures DISTINCT-as-ordering, builds loops, solves paths, opens cursors, handles one-pass UPDATE/DELETE eligibility, builds RIGHT JOIN bookkeeping, emits automatic-index/Bloom-filter setup, emits explain and scan-status metadata, and calls `sqlite3WhereCodeOneLoopStart()` for each selected loop.
- `sqlite3WhereEnd()` emits loop-advance and break/continue code in reverse nesting order, handles RIGHT JOIN subroutines, skip-ahead DISTINCT, IN-loop tails and early-out checks, LIKE repeat counters, LEFT JOIN null-row output, RIGHT JOIN unmatched-row processing, coroutine column rewrites, covering-index opcode rewrites, final break-label resolution, and `WhereInfo` cleanup.
- `OpcodeRewriteTrace` is a debug-only wrapper around `sqlite3WhereOpcodeRewriteTrace()` for tracing post-generation opcode rewrites.

### Window-Function Callbacks

- `row_numberStepFunc()` increments an aggregate `i64`; `row_numberValueFunc()` returns it.
- `struct CallCount` carries `nValue`, `nStep`, and `nTotal` for rank-like functions.
- `dense_rankStepFunc()` marks a peer-group step; `dense_rankValueFunc()` increments rank only once per peer group.
- `struct NthValueCtx`, `nth_valueStepFunc()`, and `nth_valueFinalizeFunc()` implement slow-mode `nth_value()`, validating that the second argument is a positive integer and duplicating the selected `sqlite3_value`.
- `first_valueStepFunc()` and `first_valueFinalizeFunc()` reuse `NthValueCtx` to retain the first duplicated value.
- `rankStepFunc()` and `rankValueFunc()` track total stepped rows and report the first row number in each peer group.
- `percent_rankStepFunc()`, `percent_rankInvFunc()`, and `percent_rankValueFunc()` compute `(rank-1)/(partition_rows-1)` with a zero result for singleton partitions.
- `cume_distStepFunc()`, `cume_distInvFunc()`, and `cume_distValueFunc()` compute rows up to the current peer group divided by total partition rows.
- `struct NtileCtx`, `ntileStepFunc()`, `ntileInvFunc()`, and `ntileValueFunc()` divide a partition into `N` buckets, validating `N > 0` and assigning larger buckets first.
- `struct LastValueCtx` and `last_valueStepFunc()` retain the latest duplicated value. The chunk ends at the beginning of `last_valueInvFunc()`.

## Control Flow

Planner construction starts with `sqlite3WhereBegin()`. It normalizes inputs, builds bitmasks for FROM terms, splits and analyzes WHERE terms, optionally adds LIMIT-derived terms, applies false-term bypasses, and then either uses `whereShortCut()` or builds full loop candidates with `whereLoopAddAll()`. Candidate construction dispatches by table type: b-tree tables use `whereLoopAddBtree()` and recursive `whereLoopAddBtreeIndex()`, virtual tables use `allocateIndexInfo()` plus repeated `whereLoopAddVirtualOne()` calls, and OR terms use nested builders through `whereLoopAddOr()`.

Path selection occurs in one or two `wherePathSolver()` passes. The first pass finds the cheapest path without considering output order. If `ORDER BY` or related ordering constraints exist, `whereInterstageHeuristic()` may disable risky full scans before a second solver pass scores sort-aware paths. `computeMxChoice()` can adjust beam width and costs for star-schema joins before the solver begins.

Once a path is selected, `sqlite3WhereBegin()` performs late optimizations and bytecode generation: omitted joins shrink `WhereInfo.a[]`, Bloom-filter flags are computed, table/index/virtual cursors are opened, automatic indexes and Bloom filters are materialized as needed, and `sqlite3WhereCodeOneLoopStart()` emits the body entry for each loop. The caller emits the SELECT/UPDATE/DELETE body between `sqlite3WhereBegin()` and `sqlite3WhereEnd()`.

`sqlite3WhereEnd()` closes the control-flow shape. It emits next/prev/virtual-next operations, resolves continue and break labels, completes IN-loop subloops, emits null-row passes for unmatched LEFT JOIN rows, invokes RIGHT JOIN unmatched-row generation, and then scans already-generated bytecode to replace table cursor reads with index cursor reads when a covering index or expression index can provide the data.

The window-function code in this chunk uses SQLite's aggregate/window callback control flow. The VDBE calls step/inverse/value/final callbacks according to the rewritten window frame. Each callback uses `sqlite3_aggregate_context()` to retain per-window state and uses `sqlite3_result_*()` APIs to return values or errors.

## State and Persistence Behavior

Most state in the `where.c` portion is per-prepare transient planner state. `WhereInfo`, `WhereLoop`, `WhereLevel`, `WhereClause`, `WhereTerm`, `WhereLoopBuilder`, `WherePath`, and related arrays live only while generating one statement's VDBE program. They are allocated from the parse connection (`sqlite3DbMalloc*()`), stack scratch space (`sqlite3StackAllocRawNN()`), or `WhereInfo` memory blocks, and are released by `whereInfoFree()` or parser cleanup callbacks.

Persistent database state is read but not changed in normal planning: table/index schemas, `Table.nRowLogEst`, `Index.aiRowLogEst`, STAT4 samples, partial-index WHERE expressions, index collations, and table flags drive estimates and plan choices. Some table flags are marked as advisory state during planning, such as `TF_MaybeReanalyze`, to indicate that better statistics could matter.

Generated VDBE bytecode persists for the lifetime of the prepared statement. The planner encodes access-path choices as cursor openings, seek/scan opcodes, automatic-index setup, Bloom-filter blobs held in VM registers, RIGHT JOIN match tracking ephemeral tables and Bloom registers, and opcode rewrites for covering-index access. One-pass UPDATE/DELETE state is recorded in `WhereInfo.eOnePass` and `aiCurOnePass` before being translated into writable cursors.

Virtual-table planning state crosses the module boundary through `sqlite3_index_info`. The virtual table may allocate `idxStr`, request constraint omission, indicate ORDER BY consumption, mark unique scans, request IN handling, and expose estimated cost/rows. This state is copied into `WhereLoop.u.vtab` and must be freed correctly if ownership is transferred.

Window-function state is per aggregate/window instance. It is stored in contexts allocated by `sqlite3_aggregate_context()` and may own duplicated `sqlite3_value` objects for `nth_value`, `first_value`, and `last_value`. Finalizers free duplicated values after returning them. Errors such as OOM or invalid arguments are reported through the SQLite function context rather than persistent global state.

## Dependencies and Integration Points

This code depends heavily on SQLite internal planner, parser, schema, expression, VDBE, and virtual-table APIs. Important dependencies include `Parse`, `sqlite3`, `Vdbe`, `VdbeOp`, `SrcList`, `SrcItem`, `Table`, `Index`, `WhereInfo`, `WhereLoop`, `WhereLevel`, `WhereClause`, `WhereTerm`, `WhereScan`, `WherePath`, `Expr`, `ExprList`, `Select`, `Walker`, `CollSeq`, `UnpackedRecord`, `IndexSample`, and virtual-table structs.

Major internal API integrations include:

- VDBE emission: `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP*()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeResolveLabel()`, `sqlite3VdbeGetOp()`, `sqlite3VdbeSetP4KeyInfo()`, scan-status helpers, and explain helpers.
- Expression and WHERE analysis: `sqlite3WhereExprAnalyze()`, `sqlite3WhereSplit()`, `sqlite3WhereFindTerm()`, `sqlite3ExprIfFalse()`, expression walkers, implication checks, collation/affinity helpers, STAT4 probe helpers, and indexed-expression helpers.
- Schema/table/index services: `sqlite3OpenTable()`, `sqlite3TableLock()`, `sqlite3SchemaToIndex()`, `sqlite3PrimaryKeyIndex()`, `sqlite3TableColumnToIndex()`, `sqlite3StorageColumnToTable()`, and schema-verification/write-operation helpers.
- Virtual-table module ABI: `sqlite3_index_info`, `xBestIndex`, `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, and `sqlite3_vtab_distinct()`.
- Window function ABI: `sqlite3_context`, `sqlite3_value`, `sqlite3_aggregate_context()`, `sqlite3_result_int64()`, `sqlite3_result_double()`, `sqlite3_result_value()`, `sqlite3_result_error()`, `sqlite3_result_error_nomem()`, `sqlite3_value_dup()`, and `sqlite3_value_free()`.

Upstream callers are primarily `select.c`, `update.c`, and `delete.c`, which call `sqlite3WhereBegin()` and `sqlite3WhereEnd()` around generated statement bodies. The window subsystem is integrated with SELECT rewriting (`sqlite3WindowRewrite()`), `select.c` coroutine scans, and later `sqlite3WindowCodeStep()` logic outside this chunk.

## Risks

- Planner cost heuristics are intentionally approximate. Small changes to `LogEst` constants, STAT4 use, skip-scan thresholds, IN seek-scan decisions, sorting costs, or star-query adjustments can cause large query-plan shifts and performance regressions.
- Dominance pruning in `whereLoopInsert()` and path pruning in `wherePathSolver()` are correctness-sensitive. Discarding a path with different prerequisites, ordering, or outer-join constraints can produce wrong results, not just slower plans.
- Outer join and RIGHT/FULL join handling is fragile. `constraintCompatibleWithOuterJoin()`, omitted no-op joins, null-row generation, RIGHT JOIN match tracking, and order-elimination disabling must preserve SQL null-extension semantics.
- Virtual-table `xBestIndex()` validation protects against malformed modules. Relaxing `argvIndex`, omit-mask, LIMIT/OFFSET, or IN-handling checks can admit invalid plans or wrong ORDER BY behavior.
- Covering-index and expression-index opcode rewrites run after other code has emitted table reads. Incorrect column mapping, WITHOUT ROWID handling, partial-index constant substitution, or expression-index certainty can create invalid bytecode. The code explicitly reports an internal planner error if a claimed covering index misses a required table column.
- Automatic-index and Bloom-filter setup create extra VDBE work and memory. Incorrect selectivity checks can waste prepare/runtime time, while incorrect key composition can filter out valid rows.
- STAT4 probes allocate `sqlite3_value` objects and depend on collations and affinities. OOM, missing collation, vector bounds, descending-index bound swaps, or stale statistics can alter plans or trigger prepare errors.
- The false-WHERE-term bypass deliberately preserves legacy behavior for non-deterministic functions. Broadening it to expressions containing `random()`-like functions would change observable behavior.
- Window callbacks that duplicate values must free them exactly once. Invalid `nth_value()` or `ntile()` arguments must remain error paths, and divide-by-zero behavior for singleton partitions must stay guarded.

## Test and Validation Signals

Relevant validation should exercise both correctness and plan stability:

- SQLite query-planner test suites covering indexed equality/range scans, skip-scan, IN-list and IN-subquery plans, LIKE range optimization, automatic indexes, covering indexes, expression indexes, partial indexes, STAT1/STAT4 estimates, and ANALYZE-dependent planning.
- Virtual-table tests for `xBestIndex()` constraint usability, omitted constraints, `sqlite3_vtab_rhs_value()`, `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, LIMIT/OFFSET constraints, `orderByConsumed`, `estimatedRows`, `SQLITE_INDEX_SCAN_UNIQUE`, and malformed `argvIndex` responses.
- Join tests for CROSS JOIN barriers, LEFT/RIGHT/FULL join constraints, no-op LEFT JOIN omission, RIGHT JOIN unmatched rows, OR optimization under joins, and one-pass UPDATE/DELETE eligibility.
- ORDER BY/GROUP BY/DISTINCT tests for index-order satisfaction, reverse scan masks, NULLS FIRST/LAST, collations, partial sorting, subquery ORDER BY reuse, DISTINCT ordered/noop/unique modes, and `reverse_unordered_selects`.
- Regression tests for star-schema planning and planner search-limit behavior, including evidence from `EXPLAIN QUERY PLAN` and runtime comparisons on representative schemas.
- VDBE bytecode validation through `EXPLAIN`, `PRAGMA vdbe_addoptrace`, and debug builds to catch opcode rewrite assertions and covering-index mismatches.
- OOM/fault-injection tests around `sqlite3DbMalloc*()`, STAT4 value extraction, virtual-table `idxStr` ownership, automatic-index generation, Bloom-filter registers, and window value duplication.
- Window-function tests for `row_number`, `rank`, `dense_rank`, `percent_rank`, `cume_dist`, `ntile`, `first_value`, `nth_value`, and `last_value` across partitions, peer groups, frame modes, EXCLUDE modes, invalid arguments, NULL inputs, and OOM paths.
- Build-matrix coverage with and without `SQLITE_ENABLE_STAT4`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_OMIT_WINDOWFUNC`, debug tracing, cursor hints, column-used masks, and offset SQL function support.

### subset-b-009035: lines 172669-179062

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 172669-179062

## Chunk Scope

This chunk spans the end of SQLite's `window.c` implementation inside the amalgamated `sqlite3.c`, then crosses into the generated Lemon parser file `parse.c`. The window portion covers built-in window-function registration, `Window` object resolution and query rewriting, VDBE cursor/register initialization, frame-bound validation, aggregate step/inverse/final helpers, and most of `sqlite3WindowCodeStep()`. The parser portion begins with generated parser setup, token/action tables, debug rule names, parser stack management, destructors for parser semantic values, shift/reduce lookup helpers, and the start of reduction actions through early `CREATE TABLE` grammar handling.

Because this is amalgamated generated code, the canonical sources are SQLite's `src/window.c` and `src/parse.y`/Lemon output. Local changes to this chunk should normally be made in canonical SQLite sources and regenerated, not patched directly in the amalgamation.

## Purpose And Responsibilities

The `window.c` portion implements SQLite SQL window functions after parsing and name resolution:

- Registers non-aggregate built-in window functions such as `row_number`, `rank`, `dense_rank`, `percent_rank`, `cume_dist`, `ntile`, `first_value`, `last_value`, `nth_value`, `lead`, and `lag`.
- Resolves named `WINDOW` clauses and chains derived windows against base definitions.
- Rewrites a `SELECT` containing window functions into a subquery that materializes the data needed by window processing in partition/order order.
- Allocates ephemeral cursors and VDBE registers used to buffer partition rows and evaluate window frames.
- Emits VDBE bytecode to advance frame start/current/end cursors, invoke aggregate `xStep`, `xInverse`, `xValue`, and `xFinalize` callbacks, and produce one output row at a time.
- Handles special built-in behavior for min/max, `first_value`, `nth_value`, `lead`, and `lag` without relying only on the generic aggregate-window callback path.

The `parse.c` portion initializes and drives SQLite's generated LALR parser:

- Defines parser support macros and small helper routines used by grammar actions.
- Stores generated token names, grammar rule names, parser action tables, fallback token mappings, and rule metadata.
- Manages the parser stack, including optional dynamic growth, tracing, coverage collection, and cleanup of semantic objects on pop/finalize/error.
- Begins `yy_reduce()`, where grammar reductions call into SQLite semantic routines such as transaction handling and table creation.

## Important APIs, Types, And Functions

### Window function registration and resolution

- `sqlite3WindowFunctions()` registers built-in window-only functions through `sqlite3InsertBuiltinFuncs()`. It uses `WINDOWFUNCALL`, `WINDOWFUNCNOOP`, and `WINDOWFUNCX` to create `FuncDef` entries with `SQLITE_FUNC_BUILTIN`, `SQLITE_UTF8`, and `SQLITE_FUNC_WINDOW`.
- Static function-name arrays such as `row_numberName`, `leadName`, and `nth_valueName` are intentionally compared by pointer in later logic, avoiding repeated string comparisons once a `FuncDef` is selected.
- `windowFind()` searches named window definitions and reports `no such window` through `sqlite3ErrorMsg()`.
- `sqlite3WindowUpdate()` copies a named window definition into an `OVER name` clause, chains base-window inheritance through `sqlite3WindowChain()`, enforces `RANGE` offset requirements, rejects `FILTER` on built-in non-aggregate window functions, and coerces frames required by built-ins such as `row_number`, `rank`, `lead`, and `lag`.

### SELECT rewriting

- `WindowRewrite` carries rewrite state: the main window list, original source list, accumulating subquery expression list, ephemeral `Table`, and current scalar subselect.
- `selectWindowRewriteExprCb()` rewrites selected expressions, aggregate expressions, outer-column references, and out-of-list window functions into `TK_COLUMN` reads from the future ephemeral cursor. It appends deduplicated source expressions to the subquery projection and carefully avoids rewriting expressions that belong to nested scalar subqueries.
- `selectWindowRewriteSelectCb()` preserves the nested-subquery boundary while still allowing outer references to be processed.
- `selectWindowRewriteEList()` runs the walker over result and order expression lists.
- `exprListAppendList()` appends duplicated expression lists, optionally replacing integer constants with `NULL` for sort expressions used only to preserve positional shape.
- `sqlite3WindowRewrite()` is the main public rewrite hook. It detaches the original `FROM`, `WHERE`, `GROUP BY`, and `HAVING`; builds a subquery sorted by `PARTITION BY` plus window `ORDER BY`; rewrites the outer result/order expressions against an ephemeral table; appends partition/order/window-argument/filter expressions to the subquery; assigns accumulator/result registers; attaches the subquery as the new `FROM`; and preserves aggregate-depth semantics for aggregate functions moved under the extra subquery layer.

### Window object lifecycle and comparison

- `sqlite3WindowUnlinkFromSelect()`, `sqlite3WindowDelete()`, and `sqlite3WindowListDelete()` detach and free linked `Window` objects and their owned expressions/lists.
- `sqlite3WindowOffsetExpr()` converts non-constant frame offsets to `NULL` so runtime validation catches them without leaving variable expressions in the tree.
- `sqlite3WindowAlloc()` validates frame-bound ordering, records implicit frames, applies `SQLITE_WindowFunc` optimization handling for `EXCLUDE`, and owns start/end offset expressions.
- `sqlite3WindowAssemble()` attaches partition/order/base-window pieces.
- `sqlite3WindowChain()` applies base window inheritance while rejecting attempts to override partition clauses, duplicate `ORDER BY`, or inherit from a window with an explicit frame.
- `sqlite3WindowAttach()` marks function expressions with `EP_WinFunc`, sets ownership, and rejects `DISTINCT` on window functions except for filter-frame internals.
- `sqlite3WindowLink()` links compatible windows into a `Select` so identical frames can be processed in one scan; incompatible partitioning records `SF_MultiPart`.
- `sqlite3WindowCompare()` compares frame type, bounds, exclusion mode, start/end expressions, partition list, order list, and optionally filters. Return value `0` means identical, `1` different, and `2` indeterminate from expression-list comparison.
- `sqlite3WindowDup()` and `sqlite3WindowListDup()` duplicate window definitions for expression/select duplication paths.

### VDBE setup and window execution helpers

- `sqlite3WindowCodeInit()` opens the main ephemeral table and three duplicate cursors, allocates partition tracking registers, initializes `regOne`, and creates auxiliary cursors/registers for `EXCLUDE`, min/max, `first_value`, `nth_value`, `lead`, and `lag`.
- `windowCheckValue()` emits bytecode that validates frame offsets and `nth_value()`'s second argument. Integer ROWS/GROUPS offsets use `OP_MustBeInt`; RANGE offsets accept non-negative numeric values.
- `windowArgCount()` returns the SQL argument count from the owner expression.
- `WindowCsrAndReg` pairs a VDBE cursor with peer-value registers.
- `WindowCodeArg` is the stack context passed to code-generation helpers. It carries parse/VDBE state, the main window list, gosub target, argument registers, deletion policy, rowid tracking, and the start/current/end cursor-register triples.
- `windowReadPeerValues()` loads window `ORDER BY` peer values from an ephemeral cursor.
- `windowAggStep()` emits either `OP_AggStep` or `OP_AggInverse`, or inline maintenance for min/max and positional built-ins. It handles filters, subtype-expression argument evaluation, collation requirements, and special `nth_value()` argument sourcing.
- `windowAggFinal()` emits `OP_AggValue` or `OP_AggFinal`, with min/max reading from an auxiliary index and finalization resetting accumulator state.
- `windowFullScan()` evaluates frames that require `EXCLUDE` handling by scanning from `regStartRowid` through `regEndRowid`, skipping current/group/ties rows as required, and then finalizing results.
- `windowReturnOneRow()` computes built-in positional outputs for `first_value`, `nth_value`, `lead`, and `lag`, then invokes the caller's output-row subroutine with `OP_Gosub`.
- `windowInitAccum()` initializes accumulators and auxiliary state at partition start.
- `windowCacheFrame()` determines when all rows must remain cached because a built-in needs random access or an `EXCLUDE` full scan is active.
- `windowIfNewPeer()` emits `ORDER BY` peer comparison logic used by GROUPS/RANGE processing.
- `windowCodeRangeTest()` emits RANGE-bound comparisons for the single-`ORDER BY` offset case, including ASC/DESC reversal, numeric add/subtract semantics, nonnumeric pass-through behavior, collations, `NULLS FIRST/LAST` and `KEYINFO_ORDER_BIGNULL` handling.
- `windowCodeOp()` emits one logical window operation: return current row, add rows to the aggregate frame, or inverse rows out of the frame. It also handles group/peer loops, EOF jumps, range countdown tests, and safe deletion from the ephemeral table.
- `sqlite3WindowCodeStep()` is the main bytecode generator after `sqlite3WhereBegin()`. It buffers each subquery row, detects partition changes, initializes frame offsets and cursors on the first partition row, emits different loop shapes for ROWS/GROUPS/RANGE and PRECEDING/CURRENT/FOLLOWING/UNBOUNDED combinations, flushes partitions after the input loop, and calls `sqlite3WhereEnd()` before emitting flush logic.

### Parser generated structures and routines

- `struct TrigEvent` and `struct FrameBound` are semantic-value helper structs used by parser actions for triggers and window frame bounds.
- `parserSyntaxError()`, `disableLookaside()`, `updateDeleteLimitError()`, `parserDoubleLinkSelect()`, `attachWithToSelect()`, `parserStackRealloc()`, `tokenExpr()`, `binaryToUnaryIfNull()`, and `parserAddExprIdListTerm()` are `%include` helper routines embedded before generated tables.
- Token definitions (`TK_*`) include core SQL, window-specific tokens (`TK_WINDOW`, `TK_OVER`, `TK_FILTER`, `TK_RANGE`, `TK_ROWS`, `TK_GROUPS`, `TK_EXCLUDE`, `TK_TIES`), and internal expression tokens.
- `yy_action`, `yy_lookahead`, `yy_shift_ofst`, `yy_reduce_ofst`, and `yy_default` implement the generated parser automaton.
- `yyFallback` lets many keywords fall back to `ID` in grammar positions where they may be identifiers.
- `yyTokenName`, `yyRuleName`, `yyRuleInfoLhs`, and `yyRuleInfoNRhs` support debugging, tracing, coverage, and reductions. The visible rules include SQL statements, expressions, CTEs, DML `RETURNING`, virtual tables, and window grammar rules.
- `yyParser`, `yyStackEntry`, `sqlite3ParserInit()`, optional `sqlite3ParserAlloc()`, `sqlite3ParserFinalize()`, optional `sqlite3ParserFree()`, and optional `sqlite3ParserStackPeak()` manage parser lifetime.
- `yy_destructor()` frees semantic values by type using SQLite-specific destructors such as `sqlite3SelectDelete()`, `sqlite3ExprDelete()`, `sqlite3ExprListDelete()`, `sqlite3SrcListDelete()`, `sqlite3WithDelete()`, `sqlite3WindowListDelete()`, `sqlite3WindowDelete()`, `sqlite3IdListDelete()`, and `sqlite3DeleteTriggerStep()`.
- `yy_find_shift_action()`, `yy_find_reduce_action()`, `yyStackOverflow()`, `yyTraceShift()`, `yy_shift()`, and the beginning of `yy_reduce()` implement parser execution mechanics.

## Control Flow Notes

Window execution has three major phases:

1. During parsing/name resolution, `Window` objects are allocated, assembled, attached to function expressions, linked into a `Select`, and updated against named/base windows.
2. Before planning/execution, `sqlite3WindowRewrite()` converts the original `SELECT` into a subquery-driven form. The subquery produces all columns, partition keys, order keys, function arguments, and filter values required by the window engine. The outer query reads from the ephemeral cursor instead of directly re-evaluating those expressions.
3. During VDBE generation, `sqlite3WindowCodeInit()` opens cursors and registers, while `sqlite3WindowCodeStep()` emits the row-processing loops. Input rows are inserted into a temporary table. Partition changes call a generated flush subroutine. Depending on frame type and bounds, the code advances `start`, `current`, and `end` cursors, calls `windowAggStep()` for xStep/xInverse, calls `windowAggFinal()` or built-in positional logic to populate result registers, and returns rows through the caller-provided gosub.

The frame loop structure is deliberately specialized:

- ROWS frames count physical rows.
- GROUPS frames process peer groups, using `windowIfNewPeer()` to detect new groups.
- RANGE frames compare order-key values through `windowCodeRangeTest()` and only allow offset RANGE frames with exactly one `ORDER BY` expression.
- `UNBOUNDED`, `CURRENT ROW`, `PRECEDING`, and `FOLLOWING` combinations are optimized by omitting impossible branches and by choosing when rows can be discarded from the ephemeral table.
- `EXCLUDE` handling switches to rowid-bound full scans through `windowFullScan()`.

The parser control flow is table-driven:

1. The tokenizer calls the generated parser with tokens and semantic minor values.
2. `yy_find_shift_action()` selects a shift, shift-reduce, reduce, accept, or error action from generated tables, applying fallback tokens when configured.
3. `yy_shift()` pushes tokens and grows the stack if allowed.
4. `yy_reduce()` executes grammar-specific semantic actions, pops the right-hand side, then finds and shifts the resulting nonterminal state.
5. Stack pops and parser finalization route owned semantic values through `yy_destructor()`, which is critical for freeing partially built AST objects after syntax errors or OOM.

## State And Persistence Behavior

The code in this chunk does not directly persist database file state. It builds transient parser, AST, and VDBE state that later execution may use to read or write the database.

Important transient state includes:

- `Window` fields such as `pPartition`, `pOrderBy`, frame bounds, exclusion mode, owner expression, function definition, buffer-column count, argument-column offset, accumulator/result registers, auxiliary cursors/registers, partition registers, and ephemeral cursor numbers.
- Parse-level counters `pParse->nTab` and `pParse->nMem`, which allocate VDBE cursor ids and register numbers for window processing.
- Ephemeral btree/table contents created by `OP_OpenEphemeral`, `OP_OpenDup`, `OP_Insert`, `OP_Delete`, and `OP_ResetSorter`; these hold partition rows only for statement execution.
- Aggregate contexts owned by VDBE aggregate opcodes and function implementations, finalized or reset as frame processing requires.
- Parser stack entries and semantic values, which own partially constructed `Select`, `Expr`, `ExprList`, `SrcList`, `With`, `Window`, `IdList`, and trigger-step objects until reductions transfer ownership or destructors free them.
- Optional debug globals `yyTraceFILE` and `yyTracePrompt`, plus optional parser coverage matrix `yycoverage`.

Window row-deletion policy (`WindowCodeArg.eDelete`) is a key memory behavior: rows may be retained for the whole partition, deleted after returning, deleted after entering the aggregate, or deleted after inverse processing. The selected policy depends on frame bounds and whether built-ins require random access to buffered rows.

## Dependencies And Integration Points

The window code integrates tightly with SQLite internals:

- Parser and AST types: `Parse`, `Select`, `Window`, `Expr`, `ExprList`, `SrcList`, `Table`, `FuncDef`, `Walker`, and `WhereInfo`.
- Expression and select helpers: `sqlite3ExprDup()`, `sqlite3ExprDelete()`, `sqlite3ExprListDup()`, `sqlite3ExprListAppend()`, `sqlite3ExprCompare()`, `sqlite3ExprListCompare()`, `sqlite3SelectNew()`, `sqlite3SrcListAppend()`, `sqlite3SrcItemAttachSubquery()`, `sqlite3ResultSetOfSelect()`, `sqlite3WalkSelect()`, `sqlite3WalkExprList()`, and parser cleanup hooks.
- VDBE APIs and opcodes: `sqlite3GetVdbe()`, `sqlite3VdbeAddOp*()`, `sqlite3VdbeAppendP4()`, `sqlite3VdbeChangeP5()`, `sqlite3VdbeMakeLabel()`, `sqlite3VdbeResolveLabel()`, `OP_OpenEphemeral`, `OP_OpenDup`, `OP_AggStep`, `OP_AggInverse`, `OP_AggValue`, `OP_AggFinal`, `OP_Gosub`, `OP_Return`, `OP_Compare`, `OP_Jump`, `OP_SeekRowid`, `OP_SeekGE`, `OP_Next`, and others.
- Planner/codegen integration: `sqlite3WindowRewrite()` runs before normal SELECT generation, `sqlite3WindowCodeInit()` is called before stepping subquery rows, and `sqlite3WindowCodeStep()` is called around `sqlite3WhereBegin()`/`sqlite3WhereEnd()` flow from select code.
- Collation/key helpers: `sqlite3KeyInfoFromExprList()` and `sqlite3ExprNNCollSeq()` preserve SQL ordering and comparison semantics.
- Parser integration: the generated parser actions call semantic routines from many SQLite modules, including transaction, schema, expression, select, trigger, CTE, virtual table, upsert, returning, and window-definition construction code. The window grammar rules visible here feed `Window` objects into the `window.c` APIs.

## Risks And Edge Cases

- This is generated amalgamation code. Direct edits are easy to lose and can desynchronize from `window.c`, `parse.y`, and Lemon-generated tables.
- The window rewrite path mutates the `Select` tree extensively. Ownership mistakes around `pSrc`, `pWhere`, `pGroupBy`, `pHaving`, `pSublist`, and temporary `Table` objects can cause leaks or use-after-free, especially on OOM paths.
- Built-in window functions are identified partly by pointer equality against static name strings. Any alternate registration path that does not preserve these name pointers would bypass specialized behavior.
- `RANGE` offset frames are valid only with one `ORDER BY` expression; the code enforces this in `sqlite3WindowUpdate()`. Missing this restriction would make generated RANGE comparisons ambiguous.
- Frame offsets are validated at runtime. Non-constant offsets are converted to `NULL` earlier, then rejected by generated bytecode. Tests must cover both parse-time and runtime error paths.
- `windowCodeRangeTest()` handles DESC order, nonnumeric values, collations, and `NULLS FIRST/LAST`/BIGNULL semantics. Small changes can silently alter SQL-standard window frame membership.
- The ephemeral-table deletion policy is performance-sensitive and correctness-sensitive. Deleting too early breaks `lead`, `lag`, `first_value`, `nth_value`, `EXCLUDE`, or inverse processing; never deleting increases memory use for large partitions.
- `EXCLUDE` mode forces full-frame scans and rowid boundary tracking, which can be much more expensive than incremental aggregate/inverse processing.
- Min/max inline window maintenance uses an auxiliary ephemeral index and special delete logic. Duplicate values and NULL handling need coverage.
- Parser destructors are critical for syntax-error and OOM safety. A wrong semantic-type mapping can leak AST nodes or double-free them.
- Fallback keyword behavior affects SQL compatibility. Changing token tables or fallback mappings can make previously valid identifiers fail to parse.
- Parser stack behavior differs by build: amalgamation uses stack allocation for the engine object, while non-amalgamation builds may allocate/free parser objects and optionally grow stacks. OOM behavior must remain consistent in both modes.
- This chunk ends inside `yy_reduce()` at early table-option handling; most grammar semantic actions continue in later chunks, so parser behavior cannot be fully audited from this range alone.

## Test Signals

Useful tests and coverage signals for this chunk include:

- Window function SQL covering all built-ins registered here: `row_number`, `rank`, `dense_rank`, `percent_rank`, `cume_dist`, `ntile`, `first_value`, `last_value`, `nth_value`, `lead`, and `lag`.
- Named and inherited windows: base-window lookup success/failure, prohibited overrides of `PARTITION BY`, duplicate `ORDER BY`, and explicit inherited frame specifications.
- `FILTER` behavior: allowed on aggregate window functions and rejected on built-in non-aggregate window functions.
- Frame variants across `ROWS`, `GROUPS`, and `RANGE`, including `UNBOUNDED`, `CURRENT ROW`, `PRECEDING`, `FOLLOWING`, empty frames, equal-bound FOLLOWING/PRECEDING cases, and runtime cases where start/end expressions make a frame empty.
- `RANGE` offset validation: no `ORDER BY`, multiple `ORDER BY` terms, DESC ordering, numeric/text/blob/NULL peer values, `NULLS FIRST`, `NULLS LAST`, and BIGNULL ordering.
- `EXCLUDE CURRENT ROW`, `EXCLUDE GROUP`, `EXCLUDE TIES`, and `EXCLUDE NO OTHERS` against peer groups and partitions of size zero/one/many.
- Sliding aggregate tests that require xInverse and compare results against equivalent correlated subqueries.
- min/max window frames with duplicates, NULLs, descending/ascending collation effects, and moving frame boundaries.
- `first_value`, `nth_value`, `lead`, and `lag` tests with default arguments, explicit offsets, invalid offsets, out-of-range offsets, and partitions with sparse row counts.
- OOM/fault-injection tests around `sqlite3WindowRewrite()`, `sqlite3WindowAlloc()`, expression duplication, `sqlite3ResultSetOfSelect()`, key-info allocation, parser stack allocation, and parser semantic destructors.
- Parser tests for visible grammar features: transactions/savepoints, `CREATE TABLE` table options (`STRICT`, `WITHOUT ROWID`, invalid options), CTEs with materialization modifiers, DML with `RETURNING`, virtual table declarations, expression operators, and window grammar productions.
- Debug/coverage builds using parser tracing and `YYCOVERAGE` should report exercised parser state/lookahead combinations, especially around `WINDOW`, `FILTER`, `OVER`, `RANGE`, `ROWS`, `GROUPS`, and frame exclusion tokens.

### subset-b-009036: lines 179063-186320

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 179063-186320

## Scope

This chunk starts inside the generated Lemon parser reduction switch and continues through parser acceptance/error handling, tokenizer keyword/token classification, SQL statement completeness checking, the beginning of `main.c`, global and per-connection configuration, connection close/rollback/error/hook APIs, collation and limit setup, URI filename parsing, and most of the `sqlite3_open*()` implementation. It is an amalgamation chunk, so the code is source-tree aligned to SQLite subsystems rather than to one hand-written C module.

The chunk ends inside `sqlite3_open16()` after converting the UTF-16 filename to UTF-8 and before that wrapper's cleanup/return tail.

## Purpose

- Translate SQL grammar reductions into parse-tree and schema-building side effects for DDL, DML, expressions, triggers, virtual tables, CTEs, window functions, pragmas, attach/detach, vacuum, analyze, alter table, and reindex statements.
- Provide the generated parser entry points used by SQLite's SQL compiler: syntax-error handling, parser failure/acceptance, stack shifting/reduction, and `sqlite3RunParser()`.
- Classify SQL text into tokens and keywords, including SQLite's generated compact keyword hash table and special disambiguation for `WINDOW`, `OVER`, and `FILTER`.
- Implement `sqlite3_complete()` / `sqlite3_complete16()` to decide whether a text buffer contains a complete SQL statement, with special handling for `CREATE TRIGGER ... END;`.
- Initialize and shut down process-global SQLite state: mutexes, malloc, page cache, VFS, memdb, builtin functions, compile-time extra init hooks, and global configuration options.
- Configure individual database handles, lookaside memory, busy/progress/trace/profile/commit/update/rollback/preupdate/autovacuum/WAL hooks, error reporting, limits, collations, and temporary-storage policy.
- Parse filenames and `file:` URIs into the internal filename-plus-URI-parameter format consumed by the VFS and URI accessors.
- Open a `sqlite3` connection by allocating the handle, setting defaults, selecting the VFS, opening the main b-tree, loading built-ins/extensions, registering per-connection functions/collations, and setting WAL autocheckpoint defaults.

## Important APIs, Types, And Functions

- Parser reduction actions call many semantic builders: `sqlite3AddDefaultValue`, `sqlite3AddPrimaryKey`, `sqlite3CreateIndex`, `sqlite3CreateForeignKey`, `sqlite3SelectNew`, `sqlite3ExprListAppend`, `sqlite3PExpr`, `sqlite3BeginTrigger`, `sqlite3Trigger*Step`, `sqlite3Attach`, `sqlite3Detach`, `sqlite3Alter*`, `sqlite3Vtab*`, `sqlite3CteNew`, and `sqlite3Window*`.
- Parser runtime functions include `yy_parse_failed()`, `yy_syntax_error()`, `yy_accept()`, `sqlite3Parser()`, `sqlite3ParserFallback()`, and `sqlite3RunParser()`.
- Tokenizer and keyword APIs include `keywordCode()`, `sqlite3KeywordCode()`, `sqlite3_keyword_name()`, `sqlite3_keyword_count()`, `sqlite3_keyword_check()`, `sqlite3IsIdChar()`, `getToken()`, `analyzeWindowKeyword()`, `analyzeOverKeyword()`, `analyzeFilterKeyword()`, `sqlite3GetToken()`, and optional `sqlite3Normalize()`.
- Statement-completeness APIs are `sqlite3_complete()` and, when UTF-16 is enabled, `sqlite3_complete16()`.
- Global lifecycle/configuration APIs include `sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_config()`, `sqlite3_libversion()`, `sqlite3_libversion_number()`, and `sqlite3_threadsafe()`.
- Per-connection configuration and cache APIs include `setupLookaside()`, `sqlite3_db_mutex()`, `sqlite3_db_release_memory()`, `sqlite3_db_cacheflush()`, `sqlite3_db_config()`, and `sqlite3_limit()`.
- Connection lifecycle helpers include `sqlite3Close()`, `sqlite3_close()`, `sqlite3_close_v2()`, `sqlite3LeaveMutexAndCloseZombie()`, `sqlite3RollbackAll()`, `sqlite3CloseSavepoints()`, `disconnectAllVtab()`, and `connectionIsBusy()`.
- Hook and callback APIs include `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, `sqlite3_setlk_timeout()`, `sqlite3_progress_handler()`, `sqlite3_interrupt()`, `sqlite3_is_interrupted()`, `sqlite3_trace()`, `sqlite3_trace_v2()`, `sqlite3_profile()`, `sqlite3_commit_hook()`, `sqlite3_update_hook()`, `sqlite3_rollback_hook()`, `sqlite3_preupdate_hook()`, `sqlite3_autovacuum_pages()`, `sqlite3_wal_hook()`, and `sqlite3_wal_autocheckpoint()`.
- Function and collation registration uses `sqlite3CreateFunc()`, `createFunctionApi()`, `sqlite3_create_function*()`, `sqlite3_create_window_function()`, `sqlite3_overload_function()`, `createCollation()`, `binCollFunc()`, `rtrimCollFunc()`, `nocaseCollatingFunc()`, and `sqlite3IsBinary()`.
- WAL/checkpoint and error APIs include `sqlite3_wal_checkpoint_v2()`, `sqlite3_wal_checkpoint()`, `sqlite3Checkpoint()`, `sqlite3_errmsg()`, `sqlite3_errmsg16()`, `sqlite3_error_offset()`, `sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_system_errno()`, `sqlite3_errstr()`, `sqlite3ErrStr()`, and optional `sqlite3ErrName()`.
- Open path functions include `sqlite3ParseUri()`, `uriParameter()`, `openDatabase()`, `sqlite3_open()`, `sqlite3_open_v2()`, and the beginning of `sqlite3_open16()`.

## Control Flow

The parser section is generated control flow. Each grammar rule number enters a `case`, consumes semantic stack values from `yymsp`, builds or updates SQLite AST/schema objects, stores the result back into the parser stack, then falls through to common reduce logic. The common reduce tail computes the left-hand nonterminal, finds the next reduce action, adjusts the stack, and returns the new parser action. Parse failure pops the stack and runs parse-failure hooks; syntax errors delegate to `parserSyntaxError()` or report incomplete input; acceptance pops the stack and stores parser context.

`sqlite3RunParser()` drives tokenization and parsing together. It repeatedly calls `sqlite3GetToken()`, adjusts tokens that depend on context, passes tokens to `sqlite3Parser()`, tracks parser errors and error offsets, and finalizes with an end-of-input token. Tokenization is table-driven by first-byte character class, with explicit branches for comments, operators, quoted identifiers/strings, numeric literals, bracket identifiers, variables, blob literals, and bare identifiers. Bare identifiers of length at least two are passed through the generated keyword hash, then special window-function keywords can be demoted to identifiers if their surrounding tokens make them aliases or ordinary names.

`sqlite3_complete()` uses a small finite-state machine over a simplified token stream. In normal statements, reaching the `START` state after a semicolon means complete. With trigger support, entering a trigger body changes the expected terminator to `;END;`, so internal semicolons do not mark the whole statement complete.

`sqlite3_initialize()` first ensures WSD, pointer-size sanity, mutex initialization, and malloc initialization. It then serializes process-wide initialization with `pInitMutex`, registers built-in SQL functions, initializes page cache, initializes OS/VFS, optionally initializes memdb and extra hooks, and marks `sqlite3GlobalConfig.isInit` only after the sequence succeeds. `sqlite3_shutdown()` unwinds VFS, auto extensions, page cache, malloc, mutexes, and directory globals in reverse-ish order.

`sqlite3_config()` mutates `sqlite3GlobalConfig` before initialization for most opcodes, while allowing only logging and page-cache header-size queries after initialization. It accepts varargs for mutex, allocator, page cache, heap, lookaside, URI, mmap, PMA, statement-journal spill, rowid-in-view, and optional build-specific controls.

Connection close runs in stages. `sqlite3Close()` validates the handle, enters the connection mutex, emits trace close events, disconnects virtual tables, rolls back vtab transactions, and either returns `SQLITE_BUSY` for legacy `sqlite3_close()` if statements/backups remain or marks the connection as zombie. `sqlite3LeaveMutexAndCloseZombie()` later completes cleanup only when no statements/backups remain: rollback all b-trees, close savepoints and b-trees, clear schemas, modules, functions, collations, extensions, lookaside memory, mutexes, and the `sqlite3` allocation itself.

`openDatabase()` is the main open path. It autoinitializes the library, resolves mutex mode from global threading config and open flags, normalizes shared-cache flags, masks unsupported open flags, allocates and initializes the `sqlite3` object, installs default flags/limits/collations, rewrites optional `:localStorage:` and `:sessionStorage:` names, validates read/write/create flag combinations, parses the URI or filename, opens the main b-tree, attaches main/temp schemas, sets encoding and safety levels, registers per-connection built-ins and compiled-in/automatic extensions, applies optional default locking mode, enables lookaside, installs WAL autocheckpointing, and returns either an open handle, a sick handle, or NULL on allocation failure.

## State And Persistence Behavior

The parser and tokenizer mostly build in-memory `Parse`, `Expr`, `Select`, `SrcList`, `TriggerStep`, `With`, `Window`, and schema-related objects. Their side effects later become VDBE programs and schema changes, but this chunk itself is the construction and dispatch layer, not the b-tree writer for SQL statements.

Global state is concentrated in `sqlite3GlobalConfig`: initialization flags, mutex and malloc methods, page-cache buffers, lookaside defaults, URI defaults, mmap defaults, sorter and statement-journal settings, SQL logging, rowid-in-view policy, and VFS/pcache initialization state. Incorrect ordering matters because most `sqlite3_config()` opcodes are rejected after initialization.

Connection state lives in `sqlite3`: mutex, open state, error mask/code/message, flags, limits, lookaside freelists, schema array, b-tree pointers, registered functions/collations/modules, hooks, busy handler state, WAL callback state, temp-store mode, last rowid, change counters, deferred constraints, interrupt flag, and optional autovacuum callback. Close and rollback paths explicitly reset transactional, schema, savepoint, virtual table, hook-owned, and allocator-owned resources.

Persistence effects are indirect but important. URI `mode`, `cache`, and `vfs` options affect which database file is opened and with what access mode. Open flags decide read-only/read-write/create behavior and shared/private cache behavior. `openDatabase()` opens the main b-tree and initializes schemas; the pager/b-tree layers then own persistent database file state. Busy timeout, set-lock timeout, WAL hooks, WAL autocheckpoint, synchronous defaults, locking mode, and checkpoint APIs affect durability, locking, and WAL file lifecycle once transactions run.

Error state is persisted on the connection until overwritten. `sqlite3_errmsg*()`, `sqlite3_errcode()`, and `sqlite3_error_offset()` read `db->pErr`, `db->errCode`, `db->errMask`, and `db->errByteOffset`; extended result codes are masked unless the connection was opened with `SQLITE_OPEN_EXRESCODE`.

## Dependencies And Integration Points

- Generated Lemon parser tables and grammar symbols integrate with the surrounding SQLite parse subsystem and semantic constructors from create/select/expr/trigger/alter/vtab/window/with modules.
- Tokenization depends on character-class tables, `sqlite3CtypeMap`, `sqlite3Isdigit`, `sqlite3Isspace`, `sqlite3Isxdigit`, dequoting helpers, and compile-time ASCII/EBCDIC paths.
- Normalization depends on `sqlite3_str`, VDBE double-quoted-string tracking, token scanning, and SQLite allocation through the owning `sqlite3` handle.
- Initialization depends on mutex, memory, pcache, OS/VFS, memdb, builtin-function, and optional compile-time extension initialization hooks.
- Built-in extension loading integrates optional FTS3/FTS5, RTREE, ICU, DBPAGE, DBSTAT, JSON table functions, STMTVTAB, BYTECODE, and `SQLITE_EXTRA_AUTOEXT`.
- Database opening integrates with VFS lookup, URI filename format, b-tree open/schema APIs, pager locking mode, per-connection built-in function registration, automatic extensions, WAL autocheckpoint, and lookaside allocation.
- Hook APIs integrate external application callbacks into VDBE execution, pager/busy handling, commit/update/rollback notifications, preupdate processing, autovacuum page callbacks, tracing/profile callbacks, and WAL commit/checkpoint behavior.
- Configuration and limit APIs are public C API integration points used by embedders before initialization and by applications per connection.

## Risks And Edge Cases

- This is generated and amalgamated code; hand edits to parser reductions, keyword tables, or tokenizer tables can desynchronize generated metadata and grammar behavior.
- Parser reductions transfer ownership among AST objects by direct pointer assignment. Error paths depend on later destructors and explicit deletes; missing a delete or clearing the wrong semantic value can leak or double-free parse objects.
- Token classification has many context-sensitive exceptions. `WINDOW`, `OVER`, and `FILTER` disambiguation is especially sensitive because changing fallback behavior can silently alter valid SQL parses.
- `sqlite3_complete()` is a lightweight scanner, not a full parser. It intentionally ignores many SQL details and can only answer statement completeness, so callers must still prepare/parse the SQL for correctness.
- Most `sqlite3_config()` operations are unsafe after initialization and return misuse/error if called too late. Embedders that call `sqlite3_open()` first may find later allocator/mutex/page-cache configuration ignored or rejected.
- `setupLookaside()` refuses to reconfigure while lookaside slots are in use. It also clamps slot size/count, so requested settings may be reduced or disabled.
- Closing semantics differ between `sqlite3_close()` and `sqlite3_close_v2()`: the first returns busy with active statements/backups, while the second zombie-closes and defers final deallocation. Code that assumes immediate finalizers can mis-handle `close_v2()`.
- Hook setters store raw callback pointers and user data. SQLite does not own that memory, so application lifetime discipline is required.
- `sqlite3CreateFunc()` rejects modifications while VDBEs are active and invalidates prepared statements when overriding functions. Destructor reference counting is subtle for `SQLITE_ANY`, which creates multiple encoding-specific `FuncDef` entries sharing one destructor object.
- URI parsing has security-sensitive behavior: authority handling depends on `SQLITE_ALLOW_URI_AUTHORITY`; `%00` either truncates the current URI component or errors depending on `SQLITE_ENABLE_URI_00_ERROR`; query parameters can alter VFS, access mode, and shared-cache behavior.
- Open flag validation only allows sensible read-only/read-write/create combinations after masking internal bits. Invalid combinations return `SQLITE_MISUSE_BKPT` before reaching lower b-tree assertions.
- Error-message APIs can allocate while converting UTF-16 messages and may clear OOM flags in controlled ways; callers must not assume error strings survive after later API calls.
- WAL checkpointing over all attached databases collapses multiple busy results into one final `SQLITE_BUSY`, and output counters are only meaningful for the first checkpointed database because the pointers are nulled after the first use.

## Test Signals

- Parser tests should cover DDL constraints, defaults, generated columns, foreign keys, compound SELECTs, VALUES, nested FROM terms, joins, triggers, CTEs, window frames, virtual tables, ALTER TABLE variants, `RAISE()`, `ATTACH`, `DETACH`, `VACUUM`, `PRAGMA`, and `IN`/`BETWEEN` expression rewrites.
- Tokenizer tests should cover comments, bracket/backtick/double/single-quoted tokens, blob literals, variables, digit separators, hex integers, floating-point exponents, JSON pointer operators, illegal tokens, keyword fallback, and `WINDOW`/`OVER`/`FILTER` ambiguity.
- `sqlite3_complete()` tests should include whitespace-only input, comments, unterminated comments/quotes/brackets, simple semicolon termination, and trigger bodies requiring `;END;`.
- Initialization/configuration tests should verify pre-init versus post-init `sqlite3_config()` behavior, custom mutex/malloc/pcache hooks, URI global defaults, mmap clamping, lookaside defaults, page-cache header-size queries, and shutdown/reinitialize cycles.
- Connection lifecycle tests should cover `sqlite3_open`, `sqlite3_open_v2`, invalid flag combinations, NULL filename memory databases, URI `mode/cache/vfs`, invalid URI authorities, `%00` behavior under both compile options, missing VFS errors, OOM during open, and sick-handle return behavior.
- Close tests should exercise `sqlite3_close()` busy returns with unfinalized statements/backups, `sqlite3_close_v2()` zombie cleanup after finalization, virtual table disconnect/rollback, open transaction rollback, function/collation destructor invocation, and lookaside deallocation.
- Hook tests should cover busy timeout backoff, progress callbacks, interrupts, trace/profile callbacks, commit/update/rollback/preupdate hooks, autovacuum page callbacks, WAL hooks, autocheckpoint setup, and checkpoint modes including busy attached databases.
- Error and limit tests should cover extended result-code masking, UTF-8/UTF-16 error messages, error offsets from parse failures, system errno retrieval, hard-limit clamping, invalid limit IDs, and per-connection config flags expiring prepared statements.

### subset-b-009037: lines 186321-194031

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 186321-194031

## Scope

This chunk begins at the tail of SQLite UTF-16 open handling, then covers public connection APIs from collation registration through compile-option diagnostics, the optional unlock-notify implementation, and the start of the FTS3/FTS4 module. The FTS portion includes the large format overview for varints, doclists, segment leaves, segment interior nodes, and segment directory tables; the private FTS3 header surface; tokenizer and hash-table interfaces; the FTS3 virtual table constructor and module methods; doclist/position-list merge helpers; segment-reader setup; cursor filtering and row retrieval; transaction/savepoint hooks; overloaded FTS SQL functions; module initialization; and the beginning of full-text query phrase evaluation through token-cost collection setup.

The code is part of SQLite's amalgamated source vendored under WiredTiger tests. It is not WiredTiger storage-engine code, but it provides a complete embedded SQLite implementation used by the test tree.

## Purpose

The first part exposes SQLite core public APIs and helper glue around database handles. It registers collations and collation-needed callbacks, stores per-connection client data, reports autocommit and errors, returns table column metadata, forwards file-control operations to pager/VFS objects, implements test-control verbs, builds URI filename memory layouts for VFS use, exposes attached database names and filenames, supports WAL snapshots when enabled, and reports compile-time options.

The unlock-notify section implements the `sqlite3_unlock_notify()` API for shared-cache locking. It tracks blocked connections in a global list protected by the static main mutex, detects deadlocks, groups callbacks by callback function, and invokes callbacks when blocking transactions end.

The FTS3/FTS4 section implements a virtual table module for full-text search. It defines how FTS doclists and segment btrees are encoded, parses `CREATE VIRTUAL TABLE ... USING fts3/fts4(...)` arguments, creates or connects to shadow tables, selects query plans for rowid lookup, MATCH lookup, or full scan, scans segment indexes, merges term doclists into phrase/prefix/OR/NEAR results, exposes snippet/offsets/matchinfo/optimize functions, registers built-in tokenizers, and starts per-query phrase readers with either full in-memory doclists or incremental doclist loading.

## Important APIs, Types, and Functions

- Collation APIs: `sqlite3_create_collation()`, `sqlite3_create_collation_v2()`, `sqlite3_create_collation16()`, `sqlite3_collation_needed()`, and `sqlite3_collation_needed16()` install comparison callbacks or factories under the connection mutex. The v2 form accepts an `xDel` destructor.
- Client-data APIs: `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` manage a linked list of `DbClientData` entries on `sqlite3.pDbData`, keyed by name and protected by `db->mutex`.
- Connection and diagnostics APIs: `sqlite3_get_autocommit()`, `sqlite3_extended_result_codes()`, `sqlite3_sleep()`, `sqlite3_global_recover()`, `sqlite3_thread_cleanup()`, `sqlite3_compileoption_used()`, and `sqlite3_compileoption_get()`.
- Error breakpoint helpers: `sqlite3ReportError()`, `sqlite3CorruptError()`, `sqlite3MisuseError()`, `sqlite3CantopenError()`, and debug-only OOM/corrupt-page variants log the error class and source line through `sqlite3_log()`.
- Schema metadata API: `sqlite3_table_column_metadata()` loads schema state, locates a table and column, handles rowid aliases, and returns declared type, collation, NOT NULL, primary-key, and autoincrement attributes.
- File-control and filename APIs: `sqlite3_file_control()`, `sqlite3_create_filename()`, `sqlite3_free_filename()`, `sqlite3_uri_parameter()`, `sqlite3_uri_key()`, `sqlite3_uri_boolean()`, `sqlite3_uri_int64()`, `sqlite3_filename_database()`, `sqlite3_filename_journal()`, `sqlite3_filename_wal()`, `sqlite3_db_name()`, `sqlite3_db_filename()`, `sqlite3_db_readonly()`, and private `sqlite3DbNameToBtree()`.
- Snapshot APIs under `SQLITE_ENABLE_SNAPSHOT`: `sqlite3_snapshot_get()`, `sqlite3_snapshot_open()`, `sqlite3_snapshot_recover()`, and `sqlite3_snapshot_free()` coordinate WAL snapshot handles with btree/pager transactions.
- `sqlite3_test_control()` verbs in this range include PRNG save/restore/seed, foreign-key no-action override, Bitvec tests, fault hooks, benign malloc hooks, pending-byte override, assert status, always/never corruption flags, localtime faulting, internal-function flags, extra schema checks, seek-count reporting, sort/count-of-view/optimization toggles, log-est conversion, byte-order probing, assertion of a pending byte invariant, FTS3 corruption test mode, tune parameters, SQL keyword counters, parser-coverage callbacks, parse-out handoff, and JSON self-check toggles where compiled in.
- Unlock-notify state and functions: static `sqlite3BlockedList`, `checkListProperties()`, `removeFromBlockedList()`, `addToBlockedList()`, `enterMutex()`, `leaveMutex()`, `sqlite3_unlock_notify()`, `sqlite3ConnectionBlocked()`, `sqlite3ConnectionUnlocked()`, and `sqlite3ConnectionClosed()`.
- FTS tokenizer interfaces: `sqlite3_tokenizer_module`, `sqlite3_tokenizer`, and `sqlite3_tokenizer_cursor` define tokenizer construction, destruction, open/close, token iteration, optional language-ID callbacks, and test counters.
- FTS hash interfaces: `Fts3Hash`, `Fts3HashElem`, `sqlite3Fts3HashInit()`, `sqlite3Fts3HashInsert()`, `sqlite3Fts3HashFind()`, `sqlite3Fts3HashFindElem()`, and `sqlite3Fts3HashClear()` back tokenizer/module lookup.
- Core FTS types: `Fts3Table`, `Fts3Cursor`, `Fts3Doclist`, `Fts3PhraseToken`, `Fts3Phrase`, `Fts3Expr`, `Fts3SegFilter`, `Fts3MultiSegReader`, `Fts3HashWrapper`, `TermSelect`, `TokenDoclist`, and the opening `Fts3TokenAndCost`.
- FTS table construction helpers: `sqlite3Fts3Dequote()`, `fts3CreateTables()`, `fts3DatabasePageSize()`, `fts3IsSpecialColumn()`, `fts3QuoteId()`, `fts3ReadExprList()`, `fts3WriteExprList()`, `sqlite3Fts3ReadInt()`, `fts3GobbleInt()`, `fts3PrefixParameter()`, `fts3ContentColumns()`, and `fts3InitVtab()`.
- FTS virtual table module methods: `fts3CreateMethod()`, `fts3ConnectMethod()`, `fts3BestIndexMethod()`, `fts3OpenMethod()`, `fts3CloseMethod()`, `fts3FilterMethod()`, `fts3NextMethod()`, `fts3EofMethod()`, `fts3ColumnMethod()`, `fts3RowidMethod()`, `fts3UpdateMethod()`, `fts3SyncMethod()`, `fts3BeginMethod()`, `fts3CommitMethod()`, `fts3RollbackMethod()`, `fts3RenameMethod()`, `fts3SavepointMethod()`, `fts3ReleaseMethod()`, `fts3RollbackToMethod()`, `fts3ShadowName()`, and `fts3IntegrityMethod()`.
- FTS varint and doclist primitives: `sqlite3Fts3PutVarint()`, `sqlite3Fts3GetVarintU()`, `sqlite3Fts3GetVarint()`, `sqlite3Fts3GetVarintBounded()`, `sqlite3Fts3GetVarint32()`, `sqlite3Fts3VarintLen()`, `fts3GetDeltaVarint()`, `fts3GetReverseVarint()`, `fts3PutDeltaVarint()`, `fts3GetDeltaVarint3()`, and `fts3PutDeltaVarint3()`.
- FTS position/doclist merge helpers: `fts3PoslistCopy()`, `fts3ColumnlistCopy()`, `fts3ReadNextPos()`, `fts3PutColNumber()`, `fts3PoslistMerge()`, `fts3PoslistPhraseMerge()`, `fts3PoslistNearMerge()`, `fts3DoclistOrMerge()`, `fts3DoclistPhraseMerge()`, `sqlite3Fts3FirstFilter()`, `fts3TermSelectMerge()`, `fts3TermSelectFinishMerge()`, `fts3DoclistCountDocids()`, `sqlite3Fts3DoclistPrev()`, and `sqlite3Fts3DoclistNext()`.
- FTS segment and term selection: `fts3ScanInteriorNode()`, `fts3SelectLeaf()`, `fts3SegReaderCursorAppend()`, `fts3SegReaderCursor()`, `sqlite3Fts3SegReaderCursor()`, `fts3SegReaderCursorAddZero()`, `fts3TermSegReaderCursor()`, `fts3SegReaderCursorFree()`, and `fts3TermSelect()`.
- FTS overloaded SQL functions: `fts3FunctionArg()`, `fts3SnippetFunc()`, `fts3OffsetsFunc()`, `fts3OptimizeFunc()`, `fts3MatchinfoFunc()`, and `fts3FindFunctionMethod()`.
- FTS module initialization: `sqlite3Fts3Init()` registers auxiliary FTS objects, tokenizers (`simple`, `porter`, `unicode61`, optional `icu`), overloaded scalar functions, `fts3`, `fts4`, and tokenizer virtual-table support. `hashDestroy()` reference-counts shared tokenizer hash storage.
- FTS query evaluation setup: `fts3EvalAllocateReaders()`, `fts3EvalPhraseMergeToken()`, `fts3EvalPhraseLoad()`, `fts3EvalDeferredPhrase()`, `fts3EvalPhraseStart()`, `fts3EvalDlPhraseNext()`, `incrPhraseTokenNext()`, `fts3EvalIncrPhraseNext()`, `fts3EvalPhraseNext()`, `fts3EvalStartReaders()`, and the initial `fts3EvalTokenCosts()`.

## Control Flow and Contracts

Public SQLite APIs generally follow a pattern of API-armor checks, entering `db->mutex`, delegating to private helpers, converting the result through `sqlite3ApiExit()` where appropriate, and leaving the mutex. `sqlite3_table_column_metadata()` additionally enters all btrees while loading schema state and leaves them before setting error state and outputs.

`sqlite3_file_control()` resolves a database name to a `Btree`, enters that btree, maps several common opcodes directly to pager data (`SQLITE_FCNTL_FILE_POINTER`, `VFS_POINTER`, `JOURNAL_POINTER`, `DATA_VERSION`, `RESERVE_BYTES`, `RESET_CACHE`), and forwards all other opcodes to `sqlite3OsFileControl()`. It preserves the busy-handler recursion count across the VFS call.

URI filename helpers depend on a precise memory layout: four zero bytes precede the database filename, URI key/value pairs follow the database filename, then journal and WAL filenames follow. `databaseName()` scans backward to find the four-zero sentinel. Passing arbitrary strings to these APIs violates that contract and can corrupt memory.

Unlock notify is a three-state list protocol over `sqlite3.pBlockingConnection`, `pUnlockConnection`, `xUnlockNotify`, and `pUnlockArg`. Registering a callback cancels the prior one, invokes immediately if no blocker remains, detects cycles by following `pUnlockConnection`, or inserts the connection into `sqlite3BlockedList` grouped by callback function. Unlocking a connection clears blockers, batches callback arguments for each callback function, grows the argument array under benign-malloc markers, and falls back to smaller callback batches if allocation fails.

FTS virtual table creation routes both xCreate and xConnect through `fts3InitVtab()`. It parses tokenizer arguments, FTS4 `key=value` options, content-table columns, prefix indexes, compression/uncompression functions, `order=desc`, language ID, and not-indexed columns. It allocates `Fts3Table` as one contiguous object containing column pointers, prefix-index metadata, not-indexed flags, table/database names, and column-name copies.

`fts3BestIndexMethod()` selects among full scan, docid lookup, and MATCH search. MATCH constraints on user columns override rowid lookup to avoid planner shapes that leave MATCH unusable. The method encodes language-ID and docid range constraints in high bits of `idxNum`, assigns argv positions, advertises rowid ordering when possible, and marks docid equality unique on newer SQLite versions.

`fts3FilterMethod()` decodes `idxNum`, clears any previous cursor state, sets docid bounds and scan direction, parses MATCH expressions through the tokenizer, starts FTS expression evaluation, closes segment readers, prepares content-table SELECTs for full scans or docid lookups, and advances to the first row via `fts3NextMethod()`.

FTS content access is lazy for full-text matches. MATCH evaluation identifies the next matching docid and sets `isRequireSeek`; user-column reads, snippet, offsets, and matchinfo call `fts3CursorSeek()` to prepare or reuse a rowid lookup statement and fetch the content row only when needed.

FTS segment lookup descends segment interior nodes using prefix-compressed terms. `fts3ScanInteriorNode()` reconstructs terms, validates prefix/suffix bounds, and identifies child block ranges. `fts3SelectLeaf()` recursively loads interior blocks until it narrows to leaf block IDs that may contain the target term or prefix.

Doclist and position-list logic assumes FTS3 encoding: docids are varint deltas ordered ascending or descending, position lists terminate with `POS_END` (`0`), column switches use `POS_COLUMN` (`1`), and actual positions are delta encoded with `+2`. The merge helpers preserve these encodings while computing OR, exact phrase, NEAR, first-position, prefix, and incremental phrase results.

`fts3TermSelect()` configures a segment filter, iterates merged segment readers, and merges all returned doclists through `TermSelect`. Prefix searches can combine many term doclists pair-wise to limit memory growth. Exact phrases load each token's term doclist and repeatedly apply `fts3DoclistPhraseMerge()` based on token distance.

Phrase evaluation can be full or incremental. `fts3EvalPhraseStart()` chooses incremental loading only when the scan direction matches index order, the phrase has at most four tokens, no incompatible prefix or first-token constraints exist, and at least one token has an incremental segment reader. Otherwise it materializes the full phrase doclist in memory.

Incremental phrase advancement walks each token iterator until all non-ignored tokens agree on one docid, then merges position lists to prove the phrase occurs in that row. Deferred FTS4 tokens are resolved later against row-local deferred token lists and intersected with undeferred phrase positions.

## State and Persistence Behavior

Core connection state mutated here includes collation hashes and callbacks, per-connection client data, `db->autoCommit`, `db->errMask`, `db->pDbData`, collation-needed callbacks, busy-handler counters during file-control, snapshot pager state, test-control global flags, and compile-option readout.

`sqlite3_set_clientdata()` owns destructor calls for replaced or removed values. If allocation of a new entry fails, it calls the destructor for the incoming data before returning `SQLITE_NOMEM`.

Snapshot APIs are transaction-sensitive. They require autocommit to be disabled, reject write transactions, temporarily manipulate pager snapshot state, and may begin or commit read transactions to validate or open snapshot handles.

Unlock-notify state is process-global for the blocked list and connection-local for each wait relationship. All list mutation is protected by `SQLITE_MUTEX_STATIC_MAIN`; each public registration also holds the target connection mutex.

FTS3/FTS4 durable state is stored in shadow tables. Internal-content tables create `%_content`, `%_segments`, `%_segdir`, optional `%_docsize`, and optional `%_stat`. External-content FTS4 tables skip `%_content` and derive columns from the external table when not specified. Destroy and rename methods drop or rename the matching shadow tables.

`Fts3Table` persists across virtual table connections. It owns prepared statements, generated read/write expression strings, tokenizer instance, tokenizer hash references, pending-term hash tables for each prefix index, cached segment metadata, page-size/node-size settings, autoincremental merge settings, transaction/savepoint debug state, and options such as FTS4, docsize/stat presence, descending docid order, external content, language ID, and not-indexed columns.

`Fts3Cursor` persists for a virtual table scan. It owns the prepared content statement, parsed MATCH expression tree, generated doclist buffers, current docid, bounds, scan direction, language ID, deferred tokens, and matchinfo buffer. `fts3ClearCursor()` finalizes or caches statements, frees doclists and expressions, and zeroes all fields past the base cursor.

FTS write state is buffered in pending terms until xSync, savepoint flushing, or explicit flush paths. xSync flushes pending terms, may launch automatic incremental merge based on newly added leaves and max segment level, closes segment caches, and restores the connection's last-insert-rowid.

Transaction hooks keep FTS buffers coherent with SQLite transaction boundaries. xBegin resets merge accounting and resolves legacy `%_stat` presence. xCommit expects pending terms already flushed. xRollback and xRollbackTo clear pending terms when their savepoint boundary requires it. xSavepoint forces a flush by executing an internal `INSERT INTO fts_table(fts_table) VALUES('flush')` command unless savepoint handling is temporarily ignored during rename.

FTS expression state is split between parse-time fields (`Fts3PhraseToken.z/n/isPrefix/bFirst`, `Fts3Phrase.nToken/iColumn`, `Fts3Expr` tree shape) and evaluation fields (`pSegcsr`, `pDeferred`, `doclist`, `bIncr`, `iDoclistToken`, `iDocid`, `bEof`, `bStart`, `bDeferred`, `aMI`).

## Dependencies and Integration Points

The core API section depends on SQLite connection mutexes, schema loading, btree locks, pager/VFS interfaces, UTF conversion, collation lookup, value allocation, SQLite memory allocation, error propagation, WAL snapshot functions, compile-option generation, and optional API armor.

Unlock notify integrates with shared-cache btree locking. Other code calls `sqlite3ConnectionBlocked()` when an operation is blocked by another connection, `sqlite3ConnectionUnlocked()` when a transaction releases locks, and `sqlite3ConnectionClosed()` during connection teardown.

FTS3 depends on many SQLite subsystems: virtual table APIs, SQL preparation/execution, tokenizer modules, module registration/destructors, SQLite memory allocation, varint utilities, btree/pager page-size pragmas, schema metadata, integrity checking, overloaded scalar functions, extension initialization, and test-only hooks.

The FTS shadow tables integrate with the ordinary SQL engine. Constructors issue `CREATE TABLE` for shadow storage; read paths prepare SELECTs against `%_content` or external content tables; savepoint flushes execute SQL against the virtual table itself; rename/destroy use ordinary DDL.

Segment readers are implemented by later/other FTS routines declared in `fts3Int.h`, including `sqlite3Fts3SegReaderStart()`, `sqlite3Fts3SegReaderStep()`, `sqlite3Fts3SegReaderFinish()`, `sqlite3Fts3SegReaderNew()`, `sqlite3Fts3SegReaderPending()`, `sqlite3Fts3AllSegdirs()`, `sqlite3Fts3ReadBlock()`, `sqlite3Fts3MsrIncrStart()`, `sqlite3Fts3MsrIncrNext()`, and `sqlite3Fts3MsrOvfl()`.

Deferred-token support integrates with FTS4 deferred token caches through `sqlite3Fts3DeferToken()`, `sqlite3Fts3CacheDeferredDoclists()`, `sqlite3Fts3DeferredTokenList()`, and cleanup helpers. When `SQLITE_DISABLE_FTS4_DEFERRED` is defined, these paths compile to no-ops or are omitted.

Snippet, offsets, matchinfo, and optimize integrate through the special hidden table-name column: `fts3ColumnMethod()` returns a typed pointer to the active cursor, and overloaded SQL functions retrieve it with `sqlite3_value_pointer(..., "fts3cursor")`.

Within WiredTiger, the integration concern is vendored SQLite test behavior: compile flags, FTS availability, tokenizer selection, corruption handling, and fault/test controls can affect SQLite-backed test scenarios even though WiredTiger does not call these internal functions directly.

## Risks and Edge Cases

- Most public APIs rely on connection mutex discipline. Missing mutex entry or exit would expose connection-local state such as collation callbacks, client data, error state, and attached database metadata to races.
- `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` do not include API-armor checks in this chunk. Null `db` or `zName` misuse would dereference through the connection or call `strcmp()` on a null pointer.
- `sqlite3_table_column_metadata()` treats views as not found, has special rowid alias behavior, and sets output parameters even on errors. Callers must not assume output pointers are untouched after failure.
- `sqlite3_file_control()` trusts `pArg` to match the opcode. Incorrect pointer types for built-in opcodes cause memory corruption at the caller boundary.
- Filename helper APIs require pager-created or `sqlite3_create_filename()`-created strings. `databaseName()` scans backward and cannot validate arbitrary input safely.
- Snapshot APIs contain subtle database index tests (`iDb==0 || iDb>1`) and transaction-state requirements. Invalid database names leave `rc` as `SQLITE_ERROR`; write transactions reject snapshot operations.
- `sqlite3_test_control()` is intentionally broad and can mutate global flags, PRNG seeding, pending-byte layout, parser coverage callbacks, and debug behavior. It is not a stable application-control plane.
- Unlock-notify callback invocation happens while the static main mutex is still held in this implementation path. Callback behavior must avoid operations that would deadlock on mutex ordering.
- Unlock-notify deadlock detection only follows registered unlock wait chains. Incorrect maintenance of `pUnlockConnection` or list grouping would either miss deadlocks or report false `SQLITE_LOCKED`.
- FTS constructor parsing has many option interactions. `content=` disables compression functions; missing only one of `compress=` or `uncompress=` is an error; unknown FTS4 options are errors; `prefix=` parsing can silently drop zero entries; and unresolved `notindexed=` names become constructor errors.
- FTS3 varint encoding differs from SQLite core varints: it is little-endian and can be up to 10 bytes. Reusing core varint assumptions here would corrupt doclists and segment nodes.
- Segment interior scanning validates prefix/suffix lengths, zero suffixes, and height descent. Corrupt segment blobs must return `FTS_CORRUPT_VTAB` rather than overread or loop indefinitely.
- Position-list merge code is pointer-heavy and often edits buffers in place. Padding (`FTS3_BUFFER_PADDING`, `FTS3_VARINT_MAX`) is essential, especially with descending docids where output varints may grow.
- `fts3TermSelectMerge()` sometimes stores a borrowed `aDoclist` pointer from a segment reader in `TermSelect` for pairwise merging. Later merges must not free borrowed buffers unless they were replaced by allocated merge output.
- `fts3CursorSeek()` treats a missing `%_content` row as corruption only for internal-content FTS tables. External-content tables may legitimately miss rows or reflect external table state differently.
- `p->bLock` prevents recursive virtual table operations while preparing or stepping internal SQL. Incorrect increments would either block legitimate operations or permit reentry into the same virtual table.
- xSavepoint flushes pending terms by executing SQL against the FTS table. `bIgnoreSavepoint` is required to prevent recursive savepoint behavior during this internal flush and during rename.
- Incremental phrase loading is limited to short phrases and compatible segment readers. A mistaken `bLookup` setting can cause the evaluator to assume it can incrementally merge doclists that actually require full materialization.
- Deferred-token phrase handling replaces or frees `doclist.pList` based on `bFreeList`. Ownership mistakes here would leak, double-free, or leave the phrase pointing at freed memory.

## Test Signals

Useful validation signals for this chunk include:

- Core API tests for collation registration/destructor behavior, UTF-16 collation names, collation-needed callbacks, client-data replacement/removal destructor calls, autocommit reporting, and extended result-code masking.
- Metadata tests for ordinary columns, rowid aliases, integer primary keys, AUTOINCREMENT, views, missing tables/columns, attached database names, and schema-load errors.
- VFS/file-control tests covering file pointer, VFS pointer, journal pointer, data version, reserve bytes, reset cache, unknown op forwarding, and busy-handler recursion preservation.
- URI filename tests using `sqlite3_create_filename()` and VFS xOpen filenames to validate parameter lookup, boolean/int64 parsing, key enumeration, and database/journal/WAL extraction.
- WAL snapshot tests for get/open/recover/free across autocommit-disabled read transactions, write transaction rejection, invalid database names, active statements, and stale snapshot handling.
- Unlock-notify tests for immediate callback, cancellation, callback replacement, deadlock detection, grouped callback batching, connection close cleanup, malloc-failure fallback during callback array growth, and shared-cache blocked/unlocked transitions.
- FTS virtual table constructor tests for FTS3 vs FTS4, tokenizer selection, prefix indexes, `matchinfo=fts3`, `compress`/`uncompress`, `order=desc`, external `content=`, `languageid=`, `notindexed=`, default column creation, and invalid option diagnostics.
- Shadow-table tests for create, destroy, rename, xShadowName recognition, and external-content behavior where `%_content` is not owned by FTS.
- Query planner tests for MATCH constraints, unusable MATCH constraints, rowid/docid equality and ranges, language-ID constraints, order-by consumption in ascending and descending scans, and estimated row/cost behavior.
- Cursor tests for full scans, docid lookup, MATCH lookup, lazy content seeking, EOF cleanup, rowid/column/langid hidden columns, and content corruption detection.
- FTS doclist tests for varint read/write, bounded varint reads, ascending and descending docid deltas, reverse iteration, OR merge, exact phrase merge, NEAR merge, prefix term merge, first-token filtering, and zero-padding after NEAR trimming.
- Segment-reader tests for pending terms plus persistent segments, prefix-index selection, root-only segments, interior-node leaf narrowing, corrupt interior node detection, and segment cursor cleanup.
- Transaction tests for pending-term flush on xSync and xSavepoint, rollback clearing, rollback-to savepoint boundaries, automatic incremental merge thresholds, last-insert-rowid restoration, and legacy `%_stat` discovery.
- Overloaded function tests for `snippet()`, `offsets()`, `matchinfo()`, and `optimize()` argument validation, cursor pointer extraction, lazy seek behavior, and result/error codes.
- FTS initialization tests for tokenizer hash registration/destruction, built-in tokenizer availability, optional unicode/ICU paths, `fts3_tokenizer` virtual table setup, test-only expression interfaces, and module registration for both `fts3` and `fts4`.
- Deferred and incremental evaluation tests for all-deferred phrases, mixed deferred/undeferred phrases, short phrases eligible for incremental loading, prefix tokens without prefix indexes, `^first` tokens, descending-order scans, and OOM during temporary position-list allocation.

### subset-b-009038: lines 194032-202197

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 194032-202197

## Scope

This chunk covers a dense section of SQLite's vendored FTS3/FTS4 implementation. It begins inside the FTS query evaluator's deferred-token cost analysis and result iteration logic, completes `fts3.c`, then includes `fts3_aux.c`, `fts3_expr.c`, `fts3_hash.c`, `fts3_porter.c`, `fts3_tokenizer.c`, `fts3_tokenizer1.c`, `fts3_tokenize_vtab.c`, and the opening of `fts3_write.c`.

The executable surface spans query matching, NEAR filtering, matchinfo statistics, fts4aux term-stat virtual tables, MATCH-expression parsing, tokenizer registry and tokenizer implementations, tokenizer-inspection virtual tables, pending-term accumulation, segment directory SQL statement management, segment readers, and initial segment-writing helpers.

## Purpose

The first section finishes FTS query evaluation. It decides when expensive token doclists can be deferred, starts segment readers for each query token, advances expression trees through candidate docids, verifies deferred terms and NEAR constraints against loaded row text, maintains phrase position lists, and gathers phrase statistics for `matchinfo()`.

The `fts3_aux.c` section implements the `fts4aux` virtual table. It exposes index vocabulary statistics as rows with `term`, `col`, `documents`, `occurrences`, and hidden `languageid`, using FTS segment readers to scan term doclists and count per-column document and occurrence totals.

The `fts3_expr.c` section is the hand-written parser for the right-hand side of the FTS `MATCH` operator. It supports legacy syntax and optional parenthesized syntax, recognizes phrases, column-qualified tokens, quoted strings, `OR`, `AND`, `NOT`, `NEAR[/N]`, prefix tokens, first-token markers, implicit AND, legacy unary minus, expression balancing, depth checks, and parser test functions.

The `fts3_hash.c` section provides the FTS-local hash table used for tokenizer registries and pending-term maps. It supports string or binary keys, optional key copying, lookup, insertion, replacement, deletion, rehashing, and full cleanup.

The tokenizer sections implement the built-in Porter stemmer tokenizer, the generic tokenizer registry SQL function, the built-in simple tokenizer, and the `fts3tokenize` virtual table used to inspect tokenization output.

The `fts3_write.c` opening defines the data structures and SQL statement cache used by FTS writes and segment maintenance. It starts the logic for pending doclists, language/prefix/level mapping, shadow-table access, block reads, segment readers, and segment writer construction.

## Important APIs, Types, and Functions

- Query evaluation and deferred matching:
  - `fts3EvalAverageDocsize()` reads `%_stat` doctotal data and estimates average document size in pages for deferred-token cost decisions.
  - `fts3EvalSelectDeferred()` chooses tokens in an AND/NEAR cluster to defer based on doclist overflow pages, phrase constraints, estimated row counts, and average document size.
  - `fts3EvalStart()` allocates token readers, performs FTS4 deferred-token selection, and starts readers.
  - `fts3EvalNextRow()` advances `Fts3Expr` trees for PHRASE, AND, OR, NOT, and NEAR nodes in docid order, while intentionally treating NEAR as AND and ignoring deferred tokens at this stage.
  - `sqlite3Fts3EvalTestDeferred()` loads current row content, builds deferred token doclists, evaluates the full expression including NEAR, and frees deferred doclists.
  - `fts3EvalNext()` is the core xNext-style loop for a full-text cursor, repeatedly skipping candidate rows that fail deferred or NEAR checks and enforcing `iMinDocid`/`iMaxDocid`.
  - `sqlite3Fts3EvalPhraseStats()` and `sqlite3Fts3EvalPhrasePoslist()` provide matchinfo/snippet/offset consumers with phrase occurrence totals and per-column position lists.
  - `sqlite3Fts3EvalPhraseCleanup()`, `sqlite3Fts3MsrCancel()`, and `sqlite3_fts3_init()` handle phrase cleanup, multi-segment-reader cancellation, and extension initialization.

- fts4aux virtual table:
  - `Fts3auxTable` stores the virtual table base plus a minimal `Fts3Table` handle for the target FTS table.
  - `Fts3auxCursor` embeds an `Fts3MultiSegReader`, `Fts3SegFilter`, term stop key, language id, rowid, current column, and dynamic per-column stats.
  - `fts3auxConnectMethod()` parses constructor arguments, declares `CREATE TABLE x(term, col, documents, occurrences, languageid HIDDEN)`, and builds a lightweight FTS table descriptor.
  - `fts3auxBestIndexMethod()` recognizes term equality/range constraints and hidden `languageid` equality, marks `ORDER BY term ASC` as consumed, and sets estimated costs.
  - `fts3auxFilterMethod()` initializes a segment-reader cursor for exact or range term scans.
  - `fts3auxNextMethod()` advances term rows and decodes doclists into total and per-column document/occurrence counters.
  - `sqlite3Fts3InitAux()` registers the `fts4aux` module.

- MATCH expression parser:
  - `ParseContext` carries tokenizer, language id, FTS table column names, default column, FTS4 syntax flag, parser nesting depth, and legacy unary-minus state.
  - `sqlite3Fts3OpenTokenizer()` opens tokenizer cursors and applies tokenizer `xLanguageid()` when supported.
  - `getNextToken()` parses a single token expression, including prefix `*`, legacy `-`, and FTS4 first-token `^`.
  - `getNextString()` tokenizes quoted phrases into one allocation containing `Fts3Expr`, `Fts3Phrase`, token array, and token text.
  - `getNextNode()` recognizes operators, quoted strings, parentheses, column prefixes, and regular tokens.
  - `fts3ExprParse()` constructs the expression tree, inserts implicit AND nodes, enforces NEAR operands as phrases, and handles legacy NOT branches.
  - `fts3ExprBalance()` and `fts3ExprCheckDepth()` rebalance AND/OR trees and enforce `SQLITE_FTS3_MAX_EXPR_DEPTH`.
  - `sqlite3Fts3ExprParse()` is the exported parser entry point and generates error messages.
  - `sqlite3Fts3ExprFree()` frees expression trees iteratively to avoid stack overflow.
  - Under `SQLITE_TEST`, `fts3_exprtest` and `fts3_exprtest_rebalance` expose parser output as SQL functions.

- FTS hash and tokenizer registry:
  - `sqlite3Fts3HashInit()`, `sqlite3Fts3HashClear()`, `sqlite3Fts3HashFindElem()`, `sqlite3Fts3HashFind()`, and `sqlite3Fts3HashInsert()` provide the FTS hash-table API.
  - `fts3TokenizerFunc()` implements the scalar `fts3_tokenizer()` registry accessor. Two-argument writes require either `SQLITE_DBCONFIG_ENABLE_FTS3_TOKENIZER` or a bound pointer blob; reads also gate pointer-blob return.
  - `sqlite3Fts3NextToken()` and `sqlite3Fts3InitTokenizer()` parse tokenizer specifications, dequote names/arguments, look up tokenizer modules, and call module `xCreate()`.
  - `sqlite3Fts3InitHashTable()` registers the tokenizer SQL functions and test helpers.

- Built-in tokenizers and tokenizer virtual table:
  - `porter_tokenizer` and `porter_tokenizer_cursor` implement a Porter stemmer tokenizer. `porter_stemmer()` lowercases ASCII terms, falls back for short/long/non-ASCII terms, and applies the standard Porter steps on reversed ASCII buffers.
  - `sqlite3Fts3PorterTokenizerModule()` returns the Porter tokenizer module.
  - `simple_tokenizer` and `simple_tokenizer_cursor` implement ASCII delimiter-based tokenization with lowercasing.
  - `sqlite3Fts3SimpleTokenizerModule()` returns the simple tokenizer module.
  - `Fts3tokTable` and `Fts3tokCursor` implement the `fts3tokenize` virtual table.
  - `fts3tokConnectMethod()` resolves and creates the configured tokenizer, defaulting to `simple`.
  - `fts3tokBestIndexMethod()` requires an `input = ?` constraint for cheap scans.
  - `fts3tokFilterMethod()` opens a tokenizer cursor over the supplied input, and `fts3tokColumnMethod()` returns input, token, byte offsets, and token position.
  - `sqlite3Fts3InitTok()` registers `fts3tokenize` with `sqlite3_create_module_v2()`.

- FTS write and segment primitives:
  - `PendingList`, `Fts3DeferredToken`, `Fts3SegReader`, `SegmentWriter`, and `SegmentNode` define pending doclists, deferred-token state, segment iterators, segment builders, and interior b-tree nodes.
  - `fts3SqlStmt()` caches prepared statements for FTS shadow-table operations, including `%_content`, `%_segments`, `%_segdir`, `%_docsize`, and `%_stat`.
  - `sqlite3Fts3SelectDoctotal()` and `sqlite3Fts3SelectDocsize()` expose validated `%_stat` and `%_docsize` lookups.
  - `fts3Writelock()` forces an early write lock on `%_segdir` before pending writes.
  - `getAbsoluteLevel()` maps language id, prefix-index id, and relative segment level into the absolute `%_segdir.level` namespace.
  - `sqlite3Fts3AllSegdirs()` prepares segment-directory scans for a specific level or all levels for one language/index.
  - `fts3PendingListAppendVarint()`, `fts3PendingListAppend()`, `fts3PendingTermsAddOne()`, `fts3PendingTermsAdd()`, `fts3PendingTermsDocid()`, and `sqlite3Fts3PendingTermsClear()` manage in-memory pending term doclists before flush.
  - `fts3InsertTerms()`, `fts3InsertData()`, `fts3DeleteAll()`, and `fts3DeleteTerms()` begin the insert/delete paths for FTS rows and shadow-table state.
  - `sqlite3Fts3ReadBlock()`, `sqlite3Fts3SegmentsClose()`, `fts3SegReaderIncrRead()`, `fts3SegReaderRequire()`, and `fts3SegReaderNext()` load segment blocks, including incremental reads for large nodes.
  - `sqlite3Fts3MsrOvfl()` estimates segment doclist overflow pages; `sqlite3Fts3SegReaderNew()`, `sqlite3Fts3SegReaderPending()`, `fts3SegReaderFirstDocid()`, and `fts3SegReaderNextDocid()` create and advance segment readers.
  - `fts3SegReaderSort()`, `fts3WriteSegment()`, `sqlite3Fts3MaxLevel()`, `fts3WriteSegdir()`, `fts3PrefixCompress()`, `fts3NodeAddTerm()`, `fts3NodeWrite()`, `fts3SegWriterAdd()`, and `fts3SegWriterFlush()` begin the segment-building and persistence path.

## Control Flow and Data Flow

FTS query execution begins with a parsed `Fts3Expr` tree and token readers. `fts3EvalStart()` allocates readers, optionally estimates token costs for FTS4, defers expensive tokens, and starts all remaining readers. `fts3EvalNext()` then calls `fts3EvalNextRow()` to advance the expression tree to the next candidate docid. AND/NEAR nodes merge left and right docid streams, OR nodes pick the earlier stream, NOT nodes keep the left stream while skipping matching right docids, and phrase nodes advance through phrase doclists. Candidate rows are then verified by `sqlite3Fts3EvalTestDeferred()`, which seeks the content row when necessary, builds deferred doclists, checks the full expression recursively, trims NEAR position lists, and skips false candidates.

NEAR handling is deliberately two-phase. During docid iteration it behaves like AND so that candidate selection can use ordinary docid stream merging. After a row is selected, `fts3EvalNearTest()` walks the NEAR chain, allocates temporary workspace proportional to the involved position lists, and calls `fts3EvalNearTrim()` from both sides to leave only positions that satisfy each NEAR distance. If a NEAR branch fails, its phrase position lists are invalidated so `snippet()`, `offsets()`, and `matchinfo()` do not report highlights from an unmatched NEAR clause.

Phrase statistics are gathered lazily. When `sqlite3Fts3EvalPhraseStats()` needs aggregate occurrence/row counts, `fts3EvalGatherStats()` finds the enclosing NEAR/deferred root, allocates `aMI[]` arrays for phrases, restarts iteration without incremental shortcuts, counts current-row position lists across all matching rows, then restores the cursor and expression root to the original docid. Fully deferred phrases outside NEAR use a conservative synthetic count equal to the table document count.

`fts4aux` scans index terms through a multi-segment reader. `xBestIndex` records whether the scan is exact, lower-bound, upper-bound, or range, plus optional language id. `xFilter` builds an `Fts3SegFilter` with position lists required, starts the reader, and calls `xNext`. `xNext` decodes each term's doclist as a small state machine: docid, initial column-0 or column switch, positions, and next docid separators. It accumulates row counts and occurrence counts for the aggregate `*` row and per-column rows, then emits only columns with nonzero document counts.

The parser uses tokenizer output rather than raw string splitting for terms. `getNextNode()` first strips whitespace and recognizes operators/parentheses/quoted phrases; otherwise it finds optional `column:` prefixes and delegates to `getNextToken()`. `fts3ExprParse()` maintains the previous node and current root, inserts implicit AND operators when two phrases are adjacent, threads operator precedence through `insertBinaryOperator()`, and returns `SQLITE_DONE` internally at end-of-input or close-parenthesis. Public parsing then balances large AND/OR trees to avoid deep recursion in later evaluation.

Pending-write flow starts when an insert or delete sets the active docid with `fts3PendingTermsDocid()`. `fts3PendingTermsAdd()` tokenizes each indexed column, appends docid/column/position varints to the main pending hash, and also adds configured prefix-index entries. Delete entries use column `-1` to encode deletion doclists. Pending data flushes when docids arrive out of order, language id changes, a delete/insert ordering constraint requires it, or the pending memory budget is exceeded.

Segment-reader flow handles three storage sources: pending hashes, root-only segments stored entirely in `%_segdir.root`, and multi-block segments in `%_segments`. `fts3SegReaderNext()` copies pending lists for hash entries, or reads leaf blocks from `%_segments`, optionally retaining a blob handle for incremental chunk loads. It decodes prefix-compressed terms and doclist sizes, validates bounds and terminators, and exposes the current term/doclist to multi-segment readers.

Segment-writer flow builds prefix-compressed leaf blocks and an in-memory interior tree. `fts3SegWriterAdd()` appends term/doclist records until a leaf exceeds node size, writes full leaves to `%_segments`, adds separator terms to `SegmentNode`, and tracks `nLeafData`. `fts3SegWriterFlush()` writes the final leaf and interior nodes, then writes one `%_segdir` record whose root is either the whole segment for root-only segments or the top interior node for multi-block segments.

## State and Persistence Behavior

`Fts3Cursor` state is mutated heavily during evaluation: `iPrevId`, `isEof`, `isRequireSeek`, `isMatchinfoNeeded`, `nDoc`, `nRowAvg`, deferred-token lists, and phrase doclists are all updated as query iteration progresses. Position lists may be edited in place by NEAR trimming and invalidated between rows.

`Fts3Phrase` owns loaded doclists (`aAll`), current-row position lists (`pList`, `nList`, `bFreeList`), incremental-reader flags, OR-position cache fields, and per-phrase matchinfo arrays. Cleanup must free both doclist buffers and token segment cursors.

`Fts3auxCursor` persists the active term scan and its per-column `aStat` array across virtual-table calls. `fts3auxFilterMethod()` explicitly finalizes old segment readers and frees old term/stop/stat allocations before reusing a cursor.

Parser expression trees use single-allocation layouts for phrase nodes and token text where possible. `sqlite3Fts3ExprFree()` is iterative because hostile or generated MATCH expressions may be large enough for recursive free to overflow the C stack.

The FTS hash table owns buckets, elements, and optionally copied keys. In replacement mode it returns old user data to the caller; in delete mode it frees the element and copied key but not caller-owned data. When element count reaches zero it clears buckets as well.

Tokenizer instances and cursors are module-owned but follow the FTS tokenizer ABI. Cursors retain input pointers or copied input buffers and dynamically resized token buffers. The `fts3tokenize` virtual table stores one tokenizer instance per virtual table and one tokenizer cursor per scan.

The write section is the first durable-storage-heavy part of the chunk. Prepared statements are cached in `Fts3Table.aStmt[]`; shadow-table changes target `%_content`, `%_segments`, `%_segdir`, `%_docsize`, and `%_stat`. Pending lists are in-memory until flushed; segment blocks are durable rows in `%_segments`; segment directory metadata is durable in `%_segdir`; doctotal/docsize metadata is durable in `%_stat` and `%_docsize`.

`sqlite3Fts3ReadBlock()` may leave a reusable `sqlite3_blob` handle in `Fts3Table.pSegments`, so callers that reach user-visible virtual-table boundaries must call `sqlite3Fts3SegmentsClose()` to avoid holding locks longer than expected.

## Dependencies and Integration Points

This code depends on SQLite core APIs for memory allocation, prepared statements, virtual table callbacks, SQL scalar functions, blobs, result values, database configuration, and error propagation. It also depends on FTS-internal doclist helpers, segment reader helpers, tokenizer interfaces, varint helpers, `Fts3Table`, `Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3MultiSegReader`, and related macros defined earlier in the amalgamation.

The query evaluator integrates with SQLite's virtual table scan callbacks through FTS cursor state. It supplies phrase position data to `snippet()`, `offsets()`, and `matchinfo()` code outside this chunk, and it uses FTS write/segment helpers to read term doclists.

The tokenizer registry is shared by table creation, MATCH parsing, tokenizer test helpers, and `fts3tokenize`. `sqlite3Fts3InitHashTable()` installs SQL access to the hash table using `SQLITE_DIRECTONLY`, and later initialization code registers built-in modules such as `simple` and `porter`.

`fts4aux` and `fts3tokenize` are read-only virtual tables. They plug into the core virtual table module ABI but are diagnostic/introspection surfaces over existing FTS tables or tokenizer modules, not standalone persistent tables.

The write section links FTS xUpdate paths to shadow-table persistence. It also supplies segment-reader APIs used by query evaluation, so read and write subsystems are intentionally coupled around segment formats, prefix compression, doclist varints, and `%_segdir` metadata.

In this repository, the file is vendored under WiredTiger's third-party SQLite test tree. The relevant integration concern is preserving upstream SQLite behavior for tests that exercise SQLite as embedded code; WiredTiger code should not depend on these private FTS internals directly.

## Risks and Edge Cases

- Deferred-token decisions rely on `%_stat` doctotal data. Missing, empty, or malformed doctotal blobs produce `FTS_CORRUPT_VTAB`; external-content tables disable deferred-token optimization because index and content table consistency is not guaranteed.
- NEAR evaluation edits position lists in place and may zero unused tails. Consumers that assume position lists are immutable after doclist load would report wrong offsets or corrupt iteration.
- `sqlite3Fts3EvalPhrasePoslist()` has special OR-tree handling because the current phrase may have moved past `iPrevId` or the tree may be EOF while a descendant still has an earlier entry. It may force incremental phrases to load full doclists.
- Expression parsing is intentionally syntax-mode dependent. Legacy mode gives OR higher precedence than implicit AND and supports unary `-`; parenthesis mode enables AND/NOT and parentheses but replaces the unary-minus behavior.
- Quoted phrases cannot be column-qualified in this implementation. Only single tokens receive the `column:` prefix handling in `getNextNode()`.
- Parser depth and balancing are security-sensitive. Missing depth checks or broken balancing could allow stack exhaustion from crafted MATCH strings.
- Hash insertion has unusual return semantics: when allocation fails, it returns the new data pointer and may leave the table unchanged. Callers must compare against the inserted pointer where needed.
- The `fts3_tokenizer()` pointer interface is sensitive. The code gates registration and pointer return through database config or bound values to reduce unsafe SQL-level pointer exposure.
- The Porter tokenizer stems only ASCII alphabetic terms. Non-ASCII, digit-containing long tokens, too-short tokens, or too-long tokens fall back to copy/truncate behavior, so token equivalence is not Unicode-aware.
- The simple tokenizer explicitly rejects UTF-8 delimiter configuration and lowercases only ASCII letters.
- `fts3tokBestIndexMethod()` makes unconstrained scans prohibitively expensive and `fts3tokFilterMethod()` returns `SQLITE_ERROR` if no `input = ?` constraint is supplied.
- Pending doclists assume nondecreasing docids within a language id and flush on ordering changes. Incorrect docid ordering or missed flushes would corrupt delta-encoded doclists.
- Segment node and doclist readers rely on padding (`FTS3_NODE_PADDING`) to safely read varints near corrupt node boundaries, but still must validate suffix lengths, doclist sizes, and final terminators.
- `sqlite3Fts3ReadBlock()` reuses blob handles for performance; failing to close them at virtual-table API boundaries can hold database locks.
- Segment writer code treats non-increasing term order as corruption because prefix compression requires strictly increasing terms.

## Test Signals

Useful validation signals for this chunk include:

- FTS3/FTS4 MATCH tests for phrase, prefix, column-qualified, OR, AND, NOT, legacy unary minus, implicit AND, and `NEAR/N` queries in both ascending and descending docid modes.
- Deferred-token tests with FTS4, external-content tables, doctotal corruption, very common terms, multi-token phrases, and NEAR expressions.
- `snippet()`, `offsets()`, and `matchinfo()` tests involving OR branches, unmatched NEAR subexpressions, deferred phrases, and all-deferred phrases.
- `fts4aux` tests for exact term lookup, term range scans, hidden `languageid`, `ORDER BY term ASC`, aggregate `*` rows, per-column rows, and corrupt doclist handling.
- Parser tests using `fts3_exprtest` and `fts3_exprtest_rebalance` under `SQLITE_TEST`, including malformed quotes, mismatched parentheses, maximum depth, NEAR with non-phrase operands, token names that prefix keywords such as `ORacle`, `^` first-token syntax, and tokenizer errors.
- Hash-table tests for string and binary keys, copy-key and non-copy-key modes, insertion, replacement, deletion by NULL data, rehashing, zero-entry clear, and allocation failure.
- Tokenizer tests for `simple`, `porter`, tokenizer arguments, custom tokenizer registration through bound blobs, disabled pointer access, `fts3_tokenizer_internal_test()`, and tokenizer SQL errors.
- `fts3tokenize` virtual-table tests requiring `input = ?`, verifying token text, byte offsets, position values, tokenizer arguments, default tokenizer selection, and cursor reuse.
- Write-path tests for inserts, deletes, delete-all, external-content tables, language id changes, prefix indexes, notindexed columns, pending data flush thresholds, rowid/docid conflict handling, docsize/doctotal validation, and empty-table detection.
- Segment tests for root-only segments, multi-block segments, incremental block reads, descending pending doclists, segment sorting by term/docid/age, corrupt suffix/doclist bounds, blob-handle closure, and segment directory level allocation.

### subset-b-009039: lines 202198-210096

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 202198-210096

Chunk `subset-b-009039` covers the tail of SQLite FTS3/FTS4 write-side segment maintenance, the FTS3 `snippet()`, `offsets()`, and `matchinfo()` helper implementation, the built-in unicode tokenizer and unicode folding tables, and the opening portion of the JSON/JSONB implementation. This is amalgamated third-party SQLite code embedded under WiredTiger tests, so the code is not a WiredTiger storage engine component directly, but it is part of the vendored SQLite test dependency surface.

## Purpose

The first section continues the FTS3 segment reader and writer machinery. It merges sorted segment b-trees, flushes pending terms, optimizes or rebuilds indexes, performs incremental merge work, updates `%_segdir`, `%_segments`, `%_stat`, `%_docsize`, and `%_content`, and exposes special virtual-table commands such as `optimize`, `rebuild`, `integrity-check`, `merge=`, `automerge=`, and `flush`.

The second section implements FTS3 query presentation functions. `sqlite3Fts3Snippet()` selects and renders text fragments with highlighted hits, `sqlite3Fts3Offsets()` returns token offsets for matching terms in the current row, and `sqlite3Fts3Matchinfo()` returns packed `u32` statistics for ranking and query analysis.

The third section implements the `unicode` FTS tokenizer and unicode helper tables. It tokenizes UTF-8 text into folded, optionally diacritic-stripped tokens, with configurable `tokenchars=` and `separators=` exceptions.

The last section begins SQLite's JSON support. It defines JSONB element type codes, parse/string/cache data structures, text escaping helpers, JSON5 whitespace handling, JSON text-to-JSONB conversion, JSONB validation, and initial JSONB-to-text rendering.

## Important APIs, Types, and Functions

FTS segment iteration and merging:

- `sqlite3Fts3SegReaderStart()` and `fts3SegReaderStart()` initialize a `Fts3MultiSegReader` against an optional `Fts3SegFilter`, seeking each segment to the requested term or prefix.
- `sqlite3Fts3MsrIncrStart()` starts an incremental doclist reader for one term, initializes docid positions for matching segment readers, and sorts by docid order according to `Fts3Table.bDescIdx`.
- `sqlite3Fts3MsrIncrRestart()` resets an incremental reader so a later normal segment-reader step can rebuild the full doclist.
- `sqlite3Fts3SegReaderStep()` is the central merge step. It advances segment readers, groups equal terms, merges doclists, applies column filters, honors `FTS3_SEGMENT_IGNORE_EMPTY`, `FTS3_SEGMENT_REQUIRE_POS`, `FTS3_SEGMENT_PREFIX`, `FTS3_SEGMENT_SCAN`, and `FTS3_SEGMENT_FIRST`, and returns `SQLITE_ROW` for each merged term.
- `sqlite3Fts3SegReaderFinish()` frees all segment readers and buffers in a multi-segment cursor.
- `fts3SegmentMerge()` merges pending, one level, or all levels into a new segment using `SegmentWriter`, deletes old segdir rows, flushes the writer, and may promote small higher-level segments.
- `sqlite3Fts3PendingTermsFlush()`, `sqlite3Fts3Optimize()`, `fts3DoOptimize()`, and `fts3DoRebuild()` are the high-level maintenance operations for pending-term flush, full optimize, and rebuild.

Incremental merge support:

- `Blob`, `NodeWriter`, `NodeReader`, and `IncrmergeWriter` model appendable segment construction and node traversal.
- `nodeReaderInit()`, `nodeReaderNext()`, and `nodeReaderRelease()` parse prefix-compressed segment b-tree nodes.
- `fts3IncrmergeWriter()` allocates an appendable output segment by reserving block ranges in `%_segments` and placing a zero-length marker at `end_block`.
- `fts3IncrmergeLoad()` reopens an appendable segment if the next input key sorts after the segment's last key.
- `fts3IncrmergeAppend()`, `fts3IncrmergePush()`, and `fts3IncrmergeRelease()` append leaf terms/doclists, maintain internal nodes, flush blocks, and write a new `%_segdir` record.
- `fts3IncrmergeChomp()`, `fts3TruncateSegment()`, `fts3TruncateNode()`, `fts3RemoveSegdirEntry()`, and `fts3RepackSegdirLevel()` delete or truncate input segments after partial merge progress.
- `sqlite3Fts3Incrmerge()` coordinates repeated incremental merge passes with `%_stat` merge hints via `fts3IncrmergeHintLoad()`, `fts3IncrmergeHintPush()`, `fts3IncrmergeHintPop()`, and `fts3IncrmergeHintStore()`.

FTS update and integrity APIs:

- `sqlite3Fts3UpdateMethod()` is the virtual table `xUpdate` implementation. It handles special command inserts, delete/update/insert paths, conflict handling, `%_content` writes, pending term indexing, docsize writes, and FTS4 doc-total updates.
- `fts3DeleteByRowid()` removes an existing row from the index and subsidiary tables, with a full cleanup path if the table becomes empty.
- `sqlite3Fts3IntegrityCheck()` and `fts3DoIntegrityCheck()` compare a checksum calculated from the FTS index with a checksum calculated by re-tokenizing content rows.
- `fts3SpecialInsert()` dispatches user commands embedded as `INSERT INTO tbl(tbl) VALUES(...)`.

Snippet, offsets, and matchinfo:

- Matchinfo format flags are defined as `p`, `c`, `n`, `a`, `l`, `s`, `x`, `y`, and `b`, with default `"pcx"`.
- `MatchinfoBuffer` caches global matchinfo data with two in-object output slots, reference bits, and fallback heap allocation when both slots are in use.
- `sqlite3Fts3ExprIterate()` walks phrase nodes, excluding the right side of `NOT`.
- `fts3BestSnippet()`, `fts3SnippetNextCandidate()`, `fts3SnippetDetails()`, `fts3SnippetShift()`, and `fts3SnippetText()` select and render highlighted snippet fragments.
- `sqlite3Fts3Offsets()` uses `TermOffset` iterators and tokenization of the current row text to render `"column term start length"` entries.
- `fts3MatchinfoValues()` populates the matchinfo result for global and row-local statistics, delegating to phrase stats, local hit counts, LCS computation, doc totals, and docsize reads.
- `sqlite3Fts3Matchinfo()` applies the default format and closes FTS segment resources after result generation.

Unicode tokenizer:

- `unicode_tokenizer` stores diacritic mode plus sorted exception codepoints.
- `unicode_cursor` stores the input buffer, current byte offset, token index, and reusable output token buffer.
- `unicodeCreate()` parses `remove_diacritics=0|1|2`, `tokenchars=...`, and `separators=...`.
- `unicodeNext()` scans UTF-8, skips separators, folds case through `sqlite3FtsUnicodeFold()`, strips diacritics when configured, and returns token text plus byte offsets and token position.
- `sqlite3Fts3UnicodeTokenizer()` exposes the `sqlite3_tokenizer_module`.
- `sqlite3FtsUnicodeIsalnum()`, `sqlite3FtsUnicodeIsdiacritic()`, `sqlite3FtsUnicodeFold()`, and `remove_diacritic()` implement generated unicode classification and folding tables.

JSON and JSONB startup:

- JSONB type codes `JSONB_NULL` through `JSONB_OBJECT` define binary JSON element tags.
- `JsonCache` caches up to four text-to-JSONB parse translations in `sqlite3_get_auxdata()`.
- `JsonString` is a string accumulator backed by inline space first and `sqlite3RCStr` when it grows.
- `JsonParse` owns or references JSONB blobs, original JSON text, edit state, parse error state, nesting depth, and reference count.
- `jsonCacheInsert()` and `jsonCacheSearch()` manage an LRU parse cache.
- `jsonAppendString()`, `jsonAppendSqlValue()`, `jsonReturnString()`, and `jsonReturnStringAsBlob()` serialize SQL values or generated JSON strings as text JSON or JSONB.
- `json5Whitespace()` recognizes JSON5 whitespace and comments.
- `jsonBlobAppendNode()`, `jsonBlobChangePayloadSize()`, and `jsonbPayloadSize()` encode and decode JSONB node headers.
- `jsonbValidityCheck()` recursively validates JSONB elements, primitive payload syntax, array children, object key/value pairing, and maximum nesting depth.
- `jsonTranslateTextToBlob()` is a recursive descent parser from JSON/JSON5 text to SQLite JSONB; `jsonConvertTextToBlob()` wraps it for complete-input parsing.
- `jsonTranslateBlobToText()` begins rendering JSONB back to canonical JSON text.

## Control Flow

FTS segment reads use a sorted array of `Fts3SegReader` objects. `sqlite3Fts3SegReaderStep()` advances the first `nAdvance` readers, resorts, checks EOF and term filters, identifies all readers on the same term, and either returns a single doclist directly or merges multiple doclists into `Fts3MultiSegReader.aBuffer`. During merging it decodes first docids, sorts readers by current docid, coalesces duplicate docids, applies column filters, checks ascending or descending docid order, and writes varint deltas and optional position lists.

Full segment merge starts by constructing a multi-segment cursor for a level or all segments, selecting a destination absolute level and index, scanning merged terms with `sqlite3Fts3SegReaderStep()`, writing each term/doclist through `fts3SegWriterAdd()`, deleting old segment directory rows, flushing the writer, then optionally promoting small segments into the new level.

Incremental merge is quota based. `sqlite3Fts3Incrmerge()` loads a merge hint, finds a level with enough segments, optionally overrides that level from the hint, opens readers on the oldest segments, starts a filtered merge, appends term/doclist pairs until its leaf-page work quota is reached, then either deletes fully consumed segments or truncates partially consumed input segments at the current term. If input remains, it pushes a hint for the next call. Output segments may be appendable across calls, using reserved block space and persisted `end_block` size metadata.

`sqlite3Fts3UpdateMethod()` first detects special-command inserts and exits through command handlers. Normal updates allocate docsize delta arrays, acquire a write lock, handle rowid conflict policy, delete the old row for delete/update, insert the new content row for insert/update, index terms into pending terms, write `%_docsize` if enabled, and update FTS4 `%_stat` document totals.

Snippet flow is query-position-list driven first, text-tokenizer driven second. `fts3BestSnippet()` loads phrase doclists, finds per-column positions, scores candidate token windows by phrase coverage, and records a fragment. `sqlite3Fts3Snippet()` tries one to four fragments until all seen phrases are covered. `fts3SnippetText()` then retokenizes the row column, shifts the fragment for better surrounding context, emits ellipses and original intervening text, and wraps highlighted tokens.

Matchinfo flow caches global data per cursor/format. `fts3GetMatchinfo()` validates the format string and allocates `MatchinfoBuffer` on first use, computes global fields once, then allocates an output slot for each call and fills row-local fields. `fts3MatchinfoValues()` advances the output pointer after each directive according to `fts3MatchinfoSize()`.

The unicode tokenizer flow is linear over UTF-8 bytes. It skips non-token characters, accumulates token characters and trailing diacritics, expands a reusable output buffer, folds each codepoint, optionally drops standalone diacritic effects, and returns `SQLITE_DONE` at input end.

JSON parsing flow appends placeholder JSONB array/object nodes with maximum possible payload, recursively parses children, then patches payload length with `jsonBlobChangePayloadSize()`. Primitive parsing selects canonical or JSON5-specific JSONB types. Top-level conversion verifies trailing input is only accepted whitespace/comments, and optional debug self-check validates the generated JSONB tree.

## State and Persistence Behavior

FTS persistent state is stored in SQLite shadow tables:

- `%_segments` stores segment b-tree blocks by block id. Incremental merge uses zero-length entries as appendable segment reservation markers.
- `%_segdir` stores segment metadata: level, index, start block, leaves-end block, end block plus optional leaf-data byte count, and root node.
- `%_stat` stores FTS4 document totals, automerge settings, and incremental merge hints.
- `%_docsize` stores per-column token counts for each document as a varint blob.
- `%_content` stores row content for non-external-content tables.

In-memory FTS state includes pending term hashes, segment-reader buffers, incremental writer node buffers, deferred token lists on `Fts3Cursor`, and `MatchinfoBuffer` caches tied to the cursor. Most helpers follow SQLite's prepared-statement reuse pattern through `fts3SqlStmt()` and clear/reuse statements with `sqlite3_reset()`.

JSON persistent state is not written directly in this chunk, but values are returned as SQLite text or BLOB results. Parse cache state is attached to the SQL function context via auxdata and is invalidated by SQLite when appropriate. `JsonParse` reference counting (`nJPRef`) protects cached parse objects while allowing result strings and parse blobs to share RCStr-managed memory.

## Dependencies and Integration Points

This code depends heavily on internal SQLite and FTS3 infrastructure defined elsewhere in the amalgamation: `Fts3Table`, `Fts3Cursor`, `Fts3Expr`, `Fts3Phrase`, `Fts3PhraseToken`, `Fts3MultiSegReader`, `Fts3SegReader`, `Fts3SegFilter`, tokenizer modules, SQL statement identifiers such as `SQL_SELECT_LEVEL`, and helpers such as `fts3SqlStmt()`, `fts3WriteSegment()`, `fts3WriteSegdir()`, `sqlite3Fts3ReadBlock()`, `fts3DeleteSegment()`, `fts3PendingTermsAdd()`, `fts3InsertTerms()`, `sqlite3Fts3EvalPhrasePoslist()`, and `sqlite3Fts3EvalPhraseStats()`.

The FTS virtual table integration points are `sqlite3Fts3UpdateMethod()`, `sqlite3Fts3Optimize()`, `sqlite3Fts3Snippet()`, `sqlite3Fts3Offsets()`, `sqlite3Fts3Matchinfo()`, deferred-token helpers, and `sqlite3Fts3UnicodeTokenizer()`. They interact with SQLite's `sqlite3_context`, `sqlite3_value`, `sqlite3_stmt`, vtab conflict policy, savepoints, SQL result APIs, and tokenizer API.

The JSON code depends on SQLite core allocation, RCStr, auxdata, SQL value/result APIs, charset macros (`SQLITE_ASCII`/`SQLITE_EBCDIC`), numeric formatting, identifier checks, and JSON-related flags supplied as SQL function user data. This chunk introduces core helpers that later JSON functions use for `json()`, `jsonb()`, `json_extract()`, mutation functions, and aggregate construction.

## Risks and Edge Cases

- Segment/doclist corruption is detected through ordering checks, prefix-compression sanity checks, malformed varints, out-of-range child pointers, invalid node heights, bad JSONB sizes, and maximum nesting-depth limits. Many failures map to `FTS_CORRUPT_VTAB` or `SQLITE_CORRUPT_VTAB`.
- `sqlite3Fts3SegReaderStep()` has multiple behavioral modes controlled by flags; regressions here can affect term lookup, prefix scans, column-filtered queries, phrase queries, and optimize/merge output.
- Descending index mode (`bDescIdx`) reverses docid delta expectations. Incorrect comparison or delta encoding can corrupt doclists.
- Incremental merge is persistence-sensitive. Appendable segment reservation, negative `nLeafData` markers during partial merge, merge hints, and segment truncation/repacking must stay consistent across interrupted calls.
- `fts3IncrmergeHintPop()` assumes a well-formed varint tail; corrupt hints intentionally return `FTS_CORRUPT_VTAB`.
- `fts3UpdateDocTotals()` saturates counters to zero on underflow-like cases rather than allowing unsigned wrap. Any change to docsize accounting can affect FTS4 ranking and `matchinfo()`.
- Snippet and offsets retokenize stored text and assume tokenizer position/offset behavior matches indexing. External-content tables can return content that no longer matches the index; some offset EOF cases only become corruption for non-external-content tables.
- Matchinfo buffers use custom ownership callbacks and reference bits. Returning one of the two in-buffer slots requires `fts3MIBufferFree()` to derive the owning object from a stored offset.
- The unicode tokenizer has subtle compatibility behavior around diacritic removal mode `2`, exception inversion, and UTF-8 invalid codepoint handling. Generated unicode tables should be treated as data, not hand-maintained logic.
- JSON parsing accepts JSON5 extensions but canonical output remains JSON. The text parser uses negative internal return codes for delimiters; error-location handling depends on preserving `pParse->iErr`.
- JSONB validation is intentionally structural and not a complete semantic guarantee for all malformed blobs; later rendering may still produce errors or odd output from malformed JSONB.
- JSON string and blob builders rely on careful capacity checks with `u32`/`u64` sizes. OOM flags on `JsonString` and `JsonParse` must be propagated before using partially built buffers.

## Test Signals

Useful behavioral signals for this chunk include:

- FTS3/FTS4 tests that insert, update, delete, rebuild, optimize, flush pending terms, and run `merge=A,B` and `automerge=X`.
- Queries over tables with multiple segment levels, prefix indexes, descending docid indexes, column filters, empty doclists, and external content.
- Integrity-check tests that compare index checksums to content re-tokenization across multiple language ids and prefix indexes.
- Snippet tests for multi-column tables, multi-phrase queries, `NOT` subtrees, negative and positive token counts, NULL columns, punctuation preservation, and fragment ellipsis placement.
- Offsets tests that verify byte offsets from tokenizer output and behavior when incremental doclists must be cancelled.
- Matchinfo tests for all format flags (`pcnalxybs`), FTS3 versus FTS4 restrictions, deferred tokens, docsize/doc-total availability, and global cache reuse across rows.
- Unicode tokenizer tests for UTF-8 decoding, case folding, diacritic stripping modes, custom token/separator exceptions, malformed UTF-8 replacement, and byte offset reporting.
- JSON tests for canonical JSON, JSON5 whitespace/comments/strings/numbers, nesting-depth failure, malformed JSONB, JSONB header length forms, string escaping, SQL BLOB rejection in JSON text builders, and auxdata cache reuse.

## Chunk Boundaries and Cross-References

This chunk begins mid-function after earlier FTS3 segment-reader setup code, so helpers like `fts3SegReaderNext()`, `fts3SegReaderTermCmp()`, `fts3SegReaderSort()`, `fts3SegReaderFirstDocid()`, and the FTS SQL statement enum are defined before the chunk. It ends inside `jsonTranslateBlobToText()`, so JSONB-to-text rendering, path lookup, JSON SQL function entry points, JSON aggregate code, and registration logic continue in later chunks.

### subset-b-009040: lines 210097-218440

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 210097-218440

## Scope

This chunk spans the end of SQLite's amalgamated `json.c` section, the start and main body of `rtree.c`, and the beginning of the optional `geopoly.c` inclusion. It is a large-file chunk, so this document records only the visible behavior in lines 210097-218440 and leaves whole-file synthesis to the later merge lane.

The JSON section covers JSONB-to-text rendering, pretty printing, JSON path lookup and mutation, SQL scalar and aggregate JSON functions, and the `json_each`/`json_tree` table-valued functions. The R-Tree section covers virtual-table state, node serialization, scan planning, priority-queue traversal, insert/delete/rebalance logic, shadow-table persistence, module registration, setup, and integrity checking. The final visible lines begin GeoPoly polygon parsing and scalar functions, guarded by `SQLITE_ENABLE_GEOPOLY`.

## Purpose

- Implement SQLite JSON1/JSONB SQL behavior for extraction, mutation, validation, pretty printing, aggregation, and JSON table-valued scans.
- Maintain JSONB as the internal representation for parsed JSON text, JSONB BLOB input, and editable update targets.
- Register the JSON scalar/aggregate functions and JSON virtual tables with SQLite when JSON support is enabled.
- Implement SQLite's R-Tree virtual table module over three shadow tables: `%_node`, `%_parent`, and `%_rowid`.
- Provide R-Tree query planning and execution for rowid lookup, coordinate constraints, and callback-driven `MATCH` constraints.
- Maintain on-disk R-Tree structure through inserts, deletes, splits, condense/reinsert operations, transaction cleanup, rename/drop, and integrity checks.
- Start optional GeoPoly support, which stores polygons as BLOBs and exposes conversion/rendering/geometry helper SQL functions.

## Important APIs, Types, And Functions

JSON/JSONB:

- `JsonPretty` carries a `JsonParse`, output `JsonString`, indent string, and current indentation depth for `json_pretty()`.
- `jsonTranslateBlobToPrettyText()` renders JSONB recursively with newline and indentation handling for arrays and objects; scalar values delegate to `jsonTranslateBlobToText()`.
- `jsonbArrayCount()` scans a JSONB array payload using `jsonbPayloadSize()` to count elements.
- `jsonBlobOverwrite()`, `jsonBlobEdit()`, and `jsonAfterEditSizeAdjust()` perform in-place JSONB byte edits, including a compact optimization that expands JSONB header encoding to avoid moving surrounding bytes when a replacement is slightly shorter.
- `jsonBytesToBypass()` and `jsonUnescapeOneChar()` implement JSON5-compatible escape handling, including escaped newlines, `\u` surrogate pairs, `\xNN`, `\0`, and legacy compatibility behind `SQLITE_BUG_COMPATIBLE_20250510`.
- `jsonLabelCompare()` and `jsonLabelCompareEscaped()` compare object labels with or without escape decoding.
- `jsonLookupStep()` is the central JSON path engine. It resolves `.` object labels and `[N]`, `[#]`, and `[#-N]` array indices, and it also performs edit actions (`JEDIT_DEL`, `JEDIT_REPL`, `JEDIT_INS`, `JEDIT_SET`) when `pParse->eEdit` is set.
- `jsonCreateEditSubstructure()` constructs missing nested JSONB objects/arrays for inserts such as `json_insert('{}', '$.a.b.c', 123)`.
- `jsonReturnFromBlob()` maps JSONB primitives to SQL values or returns JSON text/JSONB blobs for arrays and objects.
- `jsonFunctionArgToBlob()` converts SQL function arguments to JSONB insert/update payloads, preserving JSON-subtyped text as JSON and treating ordinary text as `JSONB_TEXTRAW`.
- `jsonArgIsJsonb()` detects whether a BLOB is JSONB, using full validation for small ambiguous blobs and a superficial outer-size check for larger blobs.
- `jsonParseFuncArg()` parses/caches function input as `JsonParse`, optionally cloning cached JSONB into editable memory.
- SQL entry points include `jsonQuoteFunc()`, `jsonArrayFunc()`, `jsonArrayLengthFunc()`, `jsonExtractFunc()`, `jsonPatchFunc()`, `jsonObjectFunc()`, `jsonRemoveFunc()`, `jsonReplaceFunc()`, `jsonSetFunc()`, `jsonTypeFunc()`, `jsonPrettyFunc()`, `jsonValidFunc()`, and `jsonErrorFunc()`.
- Aggregate/window handlers `jsonArrayStep()`, `jsonArrayFinal()`, `jsonArrayValue()`, `jsonObjectStep()`, `jsonObjectFinal()`, `jsonObjectValue()`, and `jsonGroupInverse()` build JSON arrays/objects and support window inverse removal.
- `JsonEachCursor`, `JsonParent`, and `JsonEachConnection` back the `json_each` and `json_tree` virtual tables.
- `jsonEachConnect()`, `jsonEachBestIndex()`, `jsonEachFilter()`, `jsonEachNext()`, `jsonEachColumn()`, and related cursor methods implement JSON table-valued function scans.
- `sqlite3RegisterJsonFunctions()` registers JSON scalar and aggregate functions; `sqlite3JsonTableFunctions()` registers `json_each` and `json_tree`.

R-Tree:

- `Rtree` is the virtual-table instance. It stores connection pointers, dimensions, coordinate type, node size, auxiliary column metadata, prepared statements for shadow tables, cached blob handle, node hash table, and transaction/cursor/reference state.
- `RtreeCursor` owns scan constraints, priority queue state, cached nodes, auxiliary-column read statement, and current search point.
- `RtreeNode` is an in-memory node image with reference count, dirty bit, parent pointer, node id, and on-disk byte buffer.
- `RtreeCell` is a deserialized rowid/child id plus up to five-dimensional lower/upper coordinate pairs.
- `RtreeConstraint`, `RtreeGeomCallback`, and `RtreeMatchArg` model coordinate constraints and callback-based `MATCH` searches.
- Serialization helpers `readInt16()`, `readInt64()`, `readCoord()`, `writeInt16()`, `writeInt64()`, and `writeCoord()` read/write big-endian shadow-table node bytes with platform byte-order optimizations.
- Node lifecycle helpers include `nodeAcquire()`, `nodeRelease()`, `nodeWrite()`, `nodeNew()`, `nodeBlobReset()`, `nodeHashLookup()`, `nodeHashInsert()`, and `nodeHashDelete()`.
- Cell helpers include `nodeGetRowid()`, `nodeGetCoord()`, `nodeGetCell()`, `nodeOverwriteCell()`, `nodeInsertCell()`, `nodeDeleteCell()`, `cellArea()`, `cellMargin()`, `cellUnion()`, `cellContains()`, and `cellOverlap()`.
- Search helpers include `rtreeBestIndex()`, `rtreeFilter()`, `rtreeEnqueue()`, `rtreeSearchPointNew()`, `rtreeSearchPointPop()`, `rtreeStepToLeaf()`, `rtreeRowid()`, and `rtreeColumn()`.
- Mutation helpers include `ChooseLeaf()`, `AdjustTree()`, `SplitNode()`, `splitNodeStartree()`, `updateMapping()`, `fixLeafParent()`, `deleteCell()`, `removeNode()`, `fixBoundingBox()`, `rtreeInsertCell()`, `reinsertNodeContent()`, `rtreeDeleteRowid()`, and `rtreeUpdate()`.
- Module lifecycle/setup functions include `rtreeCreate()`, `rtreeConnect()`, `rtreeDisconnect()`, `rtreeDestroy()`, `rtreeOpen()`, `rtreeClose()`, `rtreeBeginTransaction()`, `rtreeEndTransaction()`, `rtreeRollback()`, `rtreeRename()`, `rtreeSavepoint()`, `rtreeSqlInit()`, `getNodeSize()`, and `rtreeInit()`.
- Integrity/debug helpers include `rtreenode()`, `rtreedepth()`, `RtreeCheck`, `rtreeCheckTable()`, `rtreeIntegrity()`, and `rtreecheck()`.

GeoPoly start:

- `GeoPoly` stores polygon vertex count, 4-byte endian/count header, and coordinate array.
- `GeoParse` tracks JSON polygon parsing state.
- `geopolyParseJson()`, `geopolyFuncParam()`, `geopolyBlobFunc()`, `geopolyJsonFunc()`, `geopolySvgFunc()`, `geopolyXformFunc()`, `geopolyArea()`, `geopolyAreaFunc()`, `geopolyCcwFunc()`, `geopolyRegularFunc()`, and the start of `geopolyBBox()` parse, normalize, transform, render, and summarize polygons.

## Control Flow

JSON function calls generally enter through a registered SQL wrapper, parse the first argument with `jsonParseFuncArg()`, resolve paths with `jsonLookupStep()` when needed, then return via `jsonReturnFromBlob()`, `jsonReturnParse()`, or `jsonReturnString()`. JSON text is converted to JSONB for internal operations. JSONB BLOB input is accepted when `jsonArgIsJsonb()` recognizes it; otherwise BLOBs may fall through to text interpretation for legacy compatibility in parse-oriented functions.

JSON path lookup is recursive. At each path segment, `jsonLookupStep()` verifies the current JSONB node type, scans object label/value pairs or array elements, compares labels with escape-aware logic, and recurses into the selected value. If edit mode is active and the target path exists, it replaces or deletes the matching node. If insert/set mode reaches a missing object key or array append point, it builds needed nested substructure and edits bytes into the parent JSONB blob, then bubbles size changes upward with `jsonAfterEditSizeAdjust()`.

JSON scalar functions are thin wrappers around this machinery. `json_extract()` can return a single SQL value, a JSON value, a JSONB blob, or a JSON array of multiple path results depending on arguments and registration flags. `->` and `->>` support abbreviated PostgreSQL-like path arguments by constructing a temporary path string. `json_valid()` chooses text validation or superficial/strict JSONB validation according to the flags argument. `json_patch()` applies the RFC 7396 merge-patch algorithm recursively over JSONB object entries.

`json_each` and `json_tree` are virtual tables. `xBestIndex` requires an equality constraint on hidden `json` and optionally uses hidden `root`. `xFilter` parses the input, resolves the root, initializes cursor path state, and for nonrecursive `json_each` positions the cursor on direct children of an array/object. `xNext` either advances linearly over siblings or, for `json_tree`, maintains a stack of `JsonParent` frames and path prefixes for depth-first traversal. `xColumn` materializes columns such as `key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, and `path`.

R-Tree scans begin in `rtreeBestIndex()`, which prefers direct rowid lookup unless a `MATCH` constraint is present. Otherwise it builds a compact `idxStr` where each two-byte pair identifies a constraint operator and coordinate index. `rtreeFilter()` decodes that plan, initializes `RtreeConstraint` objects, deserializes callback constraints, seeds the root search point, and calls `rtreeStepToLeaf()`.

`rtreeStepToLeaf()` drives traversal with a small optimized first-point slot plus a heap priority queue. It obtains nodes through `nodeAcquire()`, tests each cell against coordinate or callback constraints, pushes qualifying child nodes or leaf entries with their score and level, and stops when the best point is a leaf row ready for `xRowid`/`xColumn`. Callback constraints can update score and within-state through `sqlite3_rtree_query_info`.

R-Tree writes enter `rtreeUpdate()`. It rejects writes while nodes are referenced by active readers, checks coordinate ordering, handles duplicate rowid conflicts and `REPLACE`, deletes any old row, chooses a leaf, inserts the new cell, writes auxiliary columns, and returns the rowid. Insertions update bounding boxes via `AdjustTree()` or split overfull nodes through the R*-Tree split algorithm in `splitNodeStartree()` and `SplitNode()`. Deletions locate the leaf through `%_rowid`, delete the cell, remove underfull nodes, repair bounding boxes, possibly shorten the root, and reinsert removed node contents.

R-Tree setup in `rtreeInit()` declares the virtual schema, validates dimensions and auxiliary columns, determines node size from page size or the existing root node, creates/opens shadow tables, prepares persistent SQL statements, and loads row estimates from `sqlite_stat1`. `rtreeModule` wires these functions into SQLite's virtual-table API, including `xIntegrity` for integrity checks.

The visible GeoPoly code parses either BLOB polygons or GeoJSON-like text, handles endian conversion, outputs BLOB/JSON/SVG representations, applies affine transforms, computes signed area/winding, constructs regular polygons, and begins bounding-box construction.

## State And Persistence Behavior

JSON state is mostly per-function-call and in-memory. `JsonParse` owns or references JSONB bytes, original JSON text, error/OOM flags, edit deltas, cached reference counts, and insertion payloads. `jsonParseFuncArg()` may insert parsed JSON into SQLite's function-argument cache and use reference-counted strings for original JSON text. Edits mutate `pParse->aBlob` in-place after ensuring it is editable, but persistence only occurs if the SQL caller stores the returned text or BLOB.

JSON aggregate state lives in SQLite aggregate context as a `JsonString`. The final/value routines temporarily append the closing delimiter and either return text or JSONB, trimming the delimiter again for window value calls. `jsonGroupInverse()` mutates the aggregate string buffer to drop the first element for sliding-window frames.

`json_each`/`json_tree` cursor state persists for the duration of a virtual-table scan: parsed JSONB, current blob offset, rowid counter, root path, traversal stack, and path string. Cursor reset/close releases parse buffers, parent arrays, and path storage.

R-Tree state is persistent. User-visible virtual tables are represented by three shadow tables:

- `%_node(nodeno INTEGER PRIMARY KEY, data BLOB)` stores fixed-size big-endian node images.
- `%_parent(nodeno INTEGER PRIMARY KEY, parentnode INTEGER)` maps non-root nodes to parents.
- `%_rowid(rowid INTEGER PRIMARY KEY, nodeno INTEGER, ...)` maps user rowids to leaf nodes and stores auxiliary columns.

In-memory `RtreeNode` objects are reference-counted and cached in `Rtree.aHash`. Dirty nodes are written by `nodeWrite()` when their reference count drops to zero. `Rtree.pNodeBlob` caches an incremental blob handle for reading nodes and is closed at transaction end, savepoint boundaries, cursor teardown when safe, rename, destroy, or on corruption/error paths. `Rtree.nNodeRef` prevents updates while read cursors could be invalidated by rebalancing.

R-Tree mutations update both node images and mapping tables. Root depth is stored in the first two bytes of node 1. Node count, parent maps, rowid maps, and auxiliary values must stay synchronized; `rtreecheck()` and `xIntegrity` validate that relationship.

GeoPoly state is transient except for BLOBs returned by functions or stored in GeoPoly/R-Tree tables. The BLOB header records endian marker and vertex count; polygon coordinates are copied into SQLite-managed result BLOBs.

## Dependencies And Integration Points

- The JSON code depends on SQLite core APIs for SQL values/results, function registration, memory allocation, subtype propagation, UTF-8 decoding, numeric conversion, aggregate/window contexts, and virtual-table APIs.
- JSON behavior is controlled by compile-time flags such as `SQLITE_OMIT_JSON`, `SQLITE_DEBUG`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_LEGACY_JSON_VALID`, and `SQLITE_BUG_COMPATIBLE_20250510`.
- JSONB encoding helpers and constants used here (`JSONB_*`, `jsonbPayloadSize()`, `jsonBlobAppendNode()`, `jsonConvertTextToBlob()`, `jsonbValidityCheck()`, `jsonCacheSearch()`, `jsonCacheInsert()`, `jsonReturnString()`, and related `JsonString` helpers) are defined earlier in the same amalgamated file.
- `sqlite3RegisterJsonFunctions()` integrates with SQLite's builtin function registry via `sqlite3InsertBuiltinFuncs()`. `sqlite3JsonTableFunctions()` integrates with virtual-table module registration through `sqlite3_create_module()`.
- R-Tree depends on the SQLite virtual-table API, prepared statements, incremental blob I/O, schema declaration, transaction/savepoint hooks, `sqlite_stat1`, conflict handling, and shadow-table support.
- R-Tree geometry/query callbacks integrate through `sqlite3_rtree_geometry_callback()`/`sqlite3_rtree_query_callback()` data represented by `RtreeMatchArg` and `sqlite3_rtree_query_info`.
- R-Tree is conditionally compiled when building as extension or with `SQLITE_ENABLE_RTREE` and virtual tables enabled. `SQLITE_RTREE_INT_ONLY`, `SQLITE_ENABLE_GEOPOLY`, endian/compiler intrinsic macros, and mutation/coverage flags alter behavior.
- GeoPoly is intentionally included inside `rtree.c` so it can access R-Tree internals and coordinate types.
- Within this repository, the file is vendored under WiredTiger's SQLite third-party test dependency. Changes affect the embedded SQLite behavior used by that test tree rather than application code written directly in this repository.

## Risks And Edge Cases

- This chunk starts mid-function and spans amalgamated component boundaries. Whole-file research must account for definitions before and after this range.
- JSONB editing is byte-offset sensitive. Incorrect payload-size adjustment, stale `delta`, or a missed `jsonAfterEditSizeAdjust()` can corrupt parent container sizes.
- `jsonBlobOverwrite()` is an optimization that intentionally relies on alternate JSONB header encodings. Mistakes there may preserve total byte count but produce noncanonical or malformed JSONB.
- JSON escape handling has compatibility-sensitive behavior. The `\0` digit-following rule changes under `SQLITE_BUG_COMPATIBLE_20250510`, and escaped newline/U+2028/U+2029 handling affects both parsing and object-label comparison.
- `jsonArgIsJsonb()` deliberately uses weaker validation for larger BLOBs. That is a performance/compatibility tradeoff; malformed internal JSONB may be detected later, produce errors, or in some translation paths produce incorrect JSON text.
- `json_each` path building quotes object labels only with simple alphanumeric checks in the visible code. Labels with embedded quotes or escapes rely on earlier JSONB label representation and path consumers; path rendering should be tested for unusual keys.
- `jsonGroupInverse()` removes the first aggregate element by scanning JSON text for commas outside strings/nesting. It depends on aggregate output being well-formed and on escape skipping being correct.
- R-Tree shadow tables are a consistency boundary. Missing nodes, bad parent maps, stale rowid maps, or corrupt node counts lead to `SQLITE_CORRUPT_VTAB` or integrity-check failures.
- R-Tree node memory management is reference-counted and recursive through parents. Incorrect parent reassignment or failure to detect loops can leak nodes or corrupt traversal; this chunk has explicit loop checks in `fixLeafParent()` and `updateMapping()`.
- Writes are refused while `nNodeRef` is nonzero. Any path that leaks node references can cause persistent `SQLITE_LOCKED_VTAB` on updates.
- R-Tree coordinate comparison has integer/float distinctions and explicit rounding for REAL32 inserts. Boundary tests around float rounding, very large integers, and inclusive/exclusive comparisons are important.
- `rtreeBestIndex()` omits some constraints from VDBE rechecking only for selected operators. Planner behavior and `idxStr` encoding must remain synchronized with `rtreeFilter()`.
- R*-Tree split and condense/reinsert logic is algorithmically dense. Off-by-one errors in minimum-cell counts, root-depth updates, or mapping rewrites can make data silently unreachable.
- GeoPoly parsing requires a closed polygon with at least four coordinates and matching first/last points. The visible code returns `SQLITE_OK` for some invalid BLOB-looking values with `p==0`, which callers interpret as NULL rather than necessarily raising an error.
- The optional GeoPoly BLOB format embeds endian state. Cross-platform tests are needed for byte-swapping and stored BLOB portability.

## Test Signals

- JSON scalar tests should cover `json_extract`, `->`, `->>`, `json_type`, `json_array_length`, `json_pretty`, `json_valid`, `json_error_position`, `json_patch`, `json_set`, `json_insert`, `json_replace`, and `json_remove` over both text JSON and JSONB BLOB input.
- JSON path tests should include quoted object labels, escaped labels, empty labels, array append/count forms (`[#]`, `[#-N]`), missing paths, malformed paths, and nested insert creation.
- JSONB mutation tests should validate returned JSON/JSONB after replacement, deletion of object label/value pairs, array insertion, root replacement, root removal, and repeated edits that change payload sizes.
- JSON compatibility tests should cover JSON5 escapes, surrogate pairs, invalid escape sequences, escaped newlines, `\0` followed by digits with and without the compatibility macro, and legacy BLOB-as-text behavior.
- JSON virtual-table tests should verify `json_each` direct-child output and `json_tree` recursive output for all columns (`key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, `path`, hidden `json`, hidden `root`) with root constraints and malformed input.
- JSON aggregate/window tests should compare `json_group_array`/`json_group_object` and JSONB variants for ordinary aggregate and sliding window frames, including nested strings containing commas and escapes.
- R-Tree query tests should exercise rowid lookup, coordinate constraints for all operators, `MATCH` callbacks, `sqlite3_rtree_query_info` scores, auxiliary column reads, and planner estimates after `ANALYZE`.
- R-Tree write tests should cover insert, update, delete, duplicate rowid with and without `REPLACE`, coordinate-order constraint failures, auto-rowid allocation, auxiliary columns, and update rejection while cursors are active.
- R-Tree structural tests should insert enough rows to force splits, root growth, root shrink after deletes, underfull-node removal, reinsertion, and parent/rowid mapping updates.
- R-Tree corruption/integrity tests should tamper with `%_node`, `%_parent`, and `%_rowid` to ensure `rtreecheck()` and `xIntegrity` report missing nodes, bad mappings, bad cell counts, invalid depth, and coordinate bounds violations.
- R-Tree platform tests should cover big-endian/little-endian serialization paths, REAL32 rounding around representability boundaries, and integer-only builds.
- GeoPoly tests should cover valid/invalid JSON polygons, BLOB endian conversion, `geopoly_blob`, `geopoly_json`, `geopoly_svg`, affine transforms, signed area/winding correction, regular polygon construction limits, and bounding-box behavior as continued after this chunk.

### subset-b-009041: lines 218441-226497

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 218441-226497

## Scope

This chunk covers the tail of SQLite's R-tree/geopoly extension, the optional ICU extension and FTS3 ICU tokenizer, and the start through most of the Resumable Bulk Update (RBU) extension implementation. It begins inside `geopolyBBox()` cleanup and continues through Geopoly predicates, Geopoly virtual-table methods, R-tree callback registration, ICU scalar/collation/tokenizer functions, the RBU public header embedded in the amalgamation, RBU handle/object-iterator/state machinery, RBU update/vacuum stepping, RBU state persistence, and the first RBU VFS shim methods through the beginning of `rbuVfsAccess()`.

The range is enabled only under the surrounding compile-time options in the amalgamation: R-tree/Geopoly code is gated by SQLite R-tree/Geopoly options, ICU code by `SQLITE_ENABLE_ICU`/`SQLITE_ENABLE_ICU_COLLATIONS`, FTS3 ICU tokenizer by `SQLITE_ENABLE_FTS3` plus ICU, and RBU by `SQLITE_ENABLE_RBU` or non-core extension builds.

## Purpose

- Finish Geopoly support by exposing SQL geometry functions, aggregate bounding-box calculation, polygon overlap/containment algorithms, and the `geopoly` virtual-table module layered on SQLite's R-tree implementation.
- Register R-tree virtual-table modules (`rtree`, `rtree_i32`) and public R-tree MATCH callback APIs that wrap application geometry/query callbacks into pointer results consumed by R-tree scans.
- Provide ICU-backed SQLite functions for Unicode-aware `LIKE`, `REGEXP`, `upper()`, `lower()`, runtime collation loading, and an FTS3 tokenizer that uses ICU word boundaries.
- Define the public RBU API and implement the early/mid RBU engine: opening handles, stepping resumable updates, applying update rows in sorted b-tree order, creating imposter tables, maintaining resumable state, moving OAL to WAL, running incremental checkpoints, and wrapping VFS methods so RBU can intercept WAL, SHM, locking, and temporary-file behavior.

## Important APIs, Types, And Functions

### Geopoly And R-tree

- `geopolyBBoxFunc()`, `geopolyBBoxStep()`, and `geopolyBBoxFinal()` implement scalar `geopoly_bbox()` and aggregate `geopoly_group_bbox()`, using `GeoBBox` aggregate context to accumulate min/max coordinates and returning a serialized Geopoly blob.
- `pointBeneathLine()` and `geopolyContainsPointFunc()` implement point-in-polygon testing using a ray-crossing count. Boundary hits return SQL integer `1`; interior points return `2`; outside returns `0`.
- `GeoEvent`, `GeoSegment`, `GeoOverlap`, `geopolyAddOneSegment()`, `geopolySortEventsByX()`, `geopolySortSegmentsByYAndC()`, and `geopolyOverlap()` implement a sweep-line style overlap classifier for two polygons. Results distinguish disjoint, overlap, containment by either side, and equality.
- `geopolyWithinFunc()` maps `geopolyOverlap()` classifications into the SQL `geopoly_within()` contract, while `geopolyOverlapFunc()` returns the full classifier.
- `geopolyInit()`, `geopolyCreate()`, and `geopolyConnect()` allocate and initialize an `Rtree` object configured for 2D float coordinates plus `_shape` as an auxiliary not-null column, declare the virtual table schema, initialize node size, and connect underlying R-tree storage tables.
- `geopolyFilter()` converts Geopoly rowid, overlap, and within query plans into R-tree cursor/search constraints. For overlap/within plans it computes the query polygon bounding box and installs four `RtreeConstraint` entries.
- `geopolyBestIndex()` selects direct rowid lookup, R-tree-assisted `geopoly_overlap()`/`geopoly_within()`, or full scan, and advertises cost/row estimates and constraint usage to SQLite.
- `geopolyColumn()` reads `_shape` and auxiliary columns using the R-tree auxiliary read statement and caches the aux row for the cursor.
- `geopolyUpdate()` translates virtual-table inserts/updates/deletes into R-tree cell changes plus auxiliary table updates, including text-to-blob polygon normalization and conflict behavior for duplicate rowids.
- `geopolyFindFunction()` overloads `geopoly_overlap()` and `geopoly_within()` so the virtual-table planner can see function constraints.
- `geopolyModule` wires the Geopoly module to R-tree cursor, transaction, rename, shadow-name, and integrity implementations where possible.
- `sqlite3_geopoly_init()` registers Geopoly scalar/aggregate SQL functions and the `geopoly` module. `sqlite3RtreeInit()` registers R-tree diagnostic functions, `rtree`, `rtree_i32`, and optionally Geopoly.
- `geomCallback()`, `sqlite3_rtree_geometry_callback()`, and `sqlite3_rtree_query_callback()` expose R-tree MATCH extension APIs. They allocate `RtreeGeomCallback`/`RtreeMatchArg` state, duplicate SQL parameters, and return a typed pointer result named `"RtreeMatchArg"`.

### ICU And FTS3 ICU

- `icuFunctionError()` formats ICU API failures into SQLite scalar-function errors.
- `icuLikeCompare()` and `icuLikeFunc()` implement Unicode case-folding `LIKE`, including `%`, `_`, and optional single-character ESCAPE handling. `SQLITE_MAX_LIKE_PATTERN_LENGTH` limits recursive pattern complexity.
- `icuRegexpFunc()` caches compiled `URegularExpression` objects with SQLite auxdata and runs `uregex_matches()` over UTF-16 input.
- `icuCaseFunc16()` implements one- and two-argument `upper()`/`lower()` using ICU `u_strToUpper()`/`u_strToLower()`, reallocating if ICU reports buffer overflow.
- `icuLoadCollation()`, `icuCollationColl()`, and `icuCollationDel()` open ICU collators, optionally apply a named strength, register UTF-16 SQLite collations, and close collators on destruction.
- `sqlite3IcuInit()` registers ICU SQL functions, and `sqlite3_icu_init()` exposes extension entry-point registration for non-core builds.
- `IcuTokenizer` and `IcuCursor` hold the FTS3 tokenizer locale, UTF-16 input copy, UTF-8 offsets, break iterator, output token buffer, and token index.
- `icuCreate()`, `icuOpen()`, `icuNext()`, `icuClose()`, `icuDestroy()`, and `sqlite3Fts3IcuTokenizerModule()` implement an FTS3 tokenizer module using ICU word breaks and case folding.

### RBU Public API And Core State

- The embedded `sqlite3rbu.h` declares public APIs: `sqlite3rbu_open()`, `sqlite3rbu_vacuum()`, `sqlite3rbu_step()`, `sqlite3rbu_savestate()`, `sqlite3rbu_close()`, `sqlite3rbu_progress()`, `sqlite3rbu_bp_progress()`, `sqlite3rbu_state()`, `sqlite3rbu_db()`, `sqlite3rbu_rename_handler()`, `sqlite3rbu_create_vfs()`, and `sqlite3rbu_destroy_vfs()`.
- `RbuState` mirrors persisted `rbu_state` rows such as stage, table, data table, index, row offset, progress, WAL checksum, database cookie, OAL size, and phase-one estimate.
- `RbuObjIter` tracks the current target table/index, source `data_xxx` table, target table columns/types/PK flags/indexed flags, prepared SELECT/INSERT/DELETE/UPDATE statements, imposter-table metadata, and per-table cleanup state.
- `sqlite3rbu` is the main handle. It owns target/RBU database handles, filenames, state database name, error state, progress counters, object iterator, private VFS name, target file descriptors, checkpoint frame list, temp-space accounting, and vacuum-specific state.
- `rbu_vfs` and `rbu_file` implement the RBU VFS wrapper and per-file shim state, including real VFS/file pointers, target/RBU links, open flags, database header cookie/write-version, WAL filename/file association, heap SHM pages, delete-on-close name, and linked-list membership.
- Stage constants distinguish OAL construction, OAL-to-WAL move, checkpoint capture, checkpoint copy, and done states. Operation constants distinguish row insert/delete/replace/update and index insert/delete.

## Control Flow

Geopoly scalar functions first normalize SQL values into `GeoPoly` blobs using helpers defined earlier in the file, then run geometry-specific calculations and return either blobs or integers. The overlap algorithm constructs one event list per non-vertical polygon segment, sorts events by X coordinate, maintains an active Y-sorted segment list, detects crossings between segments from opposite polygons, and records coverage masks to classify containment/equality/disjoint states.

Geopoly virtual-table execution follows the SQLite module lifecycle. `geopolyInit()` constructs an `Rtree`-backed virtual table with one required `_shape` auxiliary column and optional user columns. `geopolyBestIndex()` recognizes rowid and overloaded function constraints. `geopolyFilter()` resets the cursor, turns the chosen strategy into either a leaf lookup or a root R-tree scan with bounding-box constraints, then uses shared R-tree search code to reach candidate leaves. `geopolyUpdate()` rejects writes while nodes are referenced, computes new bounding boxes when shape/rowid changes, deletes old R-tree entries as needed, inserts new R-tree cells, and updates auxiliary row storage.

ICU scalar functions are invoked like normal SQLite functions. `icuLikeFunc()` validates ESCAPE and pattern length before recursing through UTF-8 codepoints. `icuRegexpFunc()` compiles/caches the pattern on argument 0 auxdata, sets the input text, matches, clears the regex text, and returns `1` or `0`. Collation loading is direct: open a `UCollator`, validate optional strength, then transfer ownership to SQLite via `sqlite3_create_collation_v2()`.

The ICU tokenizer lifecycle allocates tokenizer/cursor objects, converts input UTF-8 to folded UTF-16 while preserving original byte offsets, opens an ICU word break iterator, and returns successive non-whitespace word spans converted back to UTF-8.

RBU starts in `sqlite3rbu_open()` or `sqlite3rbu_vacuum()`, both delegating to `openRbuHandle()`. Handle open creates a private RBU VFS, opens target/RBU/state databases, creates or loads `rbu_state`, checks WAL-mode and cookie constraints, initializes phase-one progress estimation from `rbu_count`, starts transactions, and positions `RbuObjIter` at the saved table/index/row if resuming.

During `RBU_STAGE_OAL`, `sqlite3rbu_step()` repeatedly prepares work for the current object via `rbuObjIterPrepareAll()`, advances the source SELECT one row, increments progress, and calls `rbuStep()`. `rbuStep()` decodes `rbu_control` through `rbuStepType()`, then performs delete/insert/replace/index operations with `rbuStepOneOp()` or update operations through cached dynamic `UPDATE` statements from `rbuGetUpdateStmt()`. When a table has indexed columns, temporary triggers populate `rbu_tmp_xxx` with old/new index keys so auxiliary index b-trees can be updated in sorted order.

Object preparation is SQL-generation heavy. `rbuObjIterCacheTableInfo()` discovers target table shape, validates source columns, checks `rbu_rowid` requirements, and marks indexed columns. `rbuCreateImposterTable()` and `rbuCreateImposterTable2()` use `SQLITE_TESTCTRL_IMPOSTER` to create writable aliases for target b-trees and external primary-key indexes. `rbuObjIterGetIndexCols()`, `rbuObjIterGetWhere()`, `rbuObjIterGetSetlist()`, and related helpers generate quoted column lists, PK predicates, index key projections, bind lists, and update SET clauses.

After phase one finishes, RBU saves `RBU_STAGE_MOVE`, increments the schema cookie, commits both DB handles, and moves to `RBU_STAGE_MOVE`. `rbuMoveOalFile()` closes and reopens handles, obtains an exclusive lock, renames `*-oal` to `*-wal` through the registered rename callback, reopens in normal WAL mode, and sets up checkpointing.

Checkpoint setup runs a restart checkpoint in special capture mode so the VFS records WAL frame-to-database-page mappings instead of doing IO. `RBU_STAGE_CKPT` copies frames with `rbuCheckpointFrame()` in sector-aligned groups, syncs the database, updates WAL shared-memory backfill state, and finishes with `SQLITE_DONE`. `sqlite3rbu_savestate()` and `sqlite3rbu_close()` commit/sync as needed and persist resumable state with `rbuSaveState()`.

The RBU VFS methods in this chunk wrap the underlying VFS. `rbuVfsOpen()` substitutes `*-oal` for `*-wal` while building OAL, associates WAL and main DB file handles, optionally opens `rbu_memory=1` targets as delete-on-close temp DBs, and installs RBU IO methods. `rbuVfsRead()`/`rbuVfsWrite()` capture page header cookie/write-version, synthesize the first vacuum target page when needed, track OAL size, track temp file size, and record checkpoint frame/page mappings in capture mode. Lock/SHM methods block unsafe exclusive/checkpoint behavior and substitute heap SHM pages during OAL construction.

## State And Persistence Behavior

Geopoly state is stored as R-tree rows plus an auxiliary `_shape` column. `_shape` text values may be normalized to Geopoly blob format on write. Bounding boxes are persisted in the underlying R-tree coordinate storage, while `_shape` and user auxiliary columns are persisted through R-tree auxiliary tables.

ICU functions and tokenizer state are per-call/per-cursor in memory. ICU collations persist only as registrations on the SQLite connection; compiled regex objects are cached for the lifetime SQLite assigns to auxdata.

RBU has substantial persistent state:

- The RBU input database supplies `data_xxx` tables and optional `rbu_count`.
- `rbu_state` is created in the RBU DB or attached state DB and stores the resumable cursor: stage, table, data table, index, row offset, progress, WAL checksum, database change-counter cookie, OAL size, and phase-one estimate.
- During phase one, writes go to an OAL file (`<database>-oal`) rather than a normal WAL. The target database remains readable by non-RBU clients in rollback-mode semantics until the OAL is moved.
- The move stage renames OAL to WAL under exclusive lock, making the update visible through normal WAL recovery semantics.
- The checkpoint stage copies WAL frames into the database incrementally, saving progress so interruption can resume.
- RBU vacuum mode builds a new target-like database, copies schema and selected pragmas, uses a state database for resumability, and may synthesize file header state while the target temp database is initially empty.

RBU also persists safety decisions in the database header and WAL/shm state. It compares the target database cookie loaded from page 1 against `RBU_STATE_COOKIE` to detect modifications during an RBU update, and compares the saved WAL-index checksum against the current checksum before resuming a checkpoint.

## Dependencies And Integration Points

- Geopoly integrates with the R-tree module's `Rtree`, `RtreeCursor`, `RtreeNode`, search-point queues, SQL statement cache, node management, and transaction helpers defined earlier in `sqlite3.c`.
- Virtual-table integration depends on SQLite module callbacks, `sqlite3_vtab_config()`, `sqlite3_declare_vtab()`, `sqlite3_index_info`, constraint-overload APIs, and `sqlite3_vtab_nochange()`.
- R-tree callback APIs integrate with application-defined `sqlite3_rtree_geometry` and `sqlite3_rtree_query_info` callbacks using typed pointer results and SQLite function destructors.
- ICU integration depends on ICU headers/APIs: `uregex_*`, `u_strToUpper()`, `u_strToLower()`, `u_foldCase()`, `ucol_*`, `ubrk_*`, and UTF macros such as `U8_NEXT`, `U16_APPEND`, and `U16_NEXT`.
- FTS3 ICU tokenizer integrates with the legacy `sqlite3_tokenizer_module` interface.
- RBU integrates tightly with SQLite core internals: file controls (`SQLITE_FCNTL_RBU`, `SQLITE_FCNTL_RBUCNT`, VFS pointer, file pointer, ZIPVFS), `SQLITE_TESTCTRL_IMPOSTER`, SQLite schema pragmas, WAL locks and shared-memory layout, DB header offsets, VFS IO method tables, `sqlite_schema`, temporary triggers, and transaction handling.
- RBU has optional platform integration for WinCE rename via `MoveFileW()` and zipvfs via special file controls. The default rename path uses C `rename()`.

## Risks And Edge Cases

- Geopoly geometry predicates compare floating-point coordinates for exact equality in several places. Boundary, equality, crossing, and containment classifications may be sensitive to precision, degenerate polygons, repeated points, and near-collinear segments.
- `geopolyOverlap()` ignores vertical segments when building the sweep-line event set. Other point-in-polygon code handles vertical boundaries, but overlap classification depends on the algorithm's assumptions about polygon representation and coverage masks.
- `geopolyUpdate()` blocks writes when R-tree nodes are referenced, but callers may still observe `SQLITE_LOCKED_VTAB` in read/write concurrency patterns involving active cursors.
- Geopoly text-to-blob normalization during aux writes means invalid text shapes can fail either bounding-box computation or conversion and produce virtual-table errors.
- ICU `LIKE` uses recursive matching for `%`, bounded by pattern length but still potentially expensive on adversarial patterns near the configured maximum.
- `icuRegexpFunc()` caches compiled patterns as auxdata, so correctness depends on SQLite invalidating auxdata when the pattern changes; ICU errors are surfaced as SQL errors.
- ICU tokenizer offset handling depends on the UTF-8 to folded UTF-16 conversion preserving meaningful token boundaries after case folding; unusual Unicode case-fold expansions or invalid input can produce conversion errors.
- RBU uses extensive dynamic SQL against schema names and `PRAGMA` output. Most identifiers are quoted with `%w`/`%Q`, but logic is still sensitive to unusual schemas, expression indexes, partial indexes, generated/hidden columns, and virtual-table behavior.
- RBU relies on imposter tables through `SQLITE_TESTCTRL_IMPOSTER`, a powerful internal test-control interface. Incorrect rootpage, schema, PK, or collation reconstruction can corrupt target b-trees.
- RBU state commits are not fully atomic with OAL/WAL side effects. The comments explicitly note possible inconsistency after power loss, usually surfacing as constraint errors or restart from saved state.
- RBU refuses targets already in WAL mode during OAL construction and uses VFS tricks to detect/deny WAL presence. Damaged headers, stacked VFSes, or zipvfs setup mistakes can produce hard errors.
- Checkpoint resume is invalidated if another writer appends to WAL, detected by WAL-index checksum mismatch. That avoids unsafe continuation but can mark the operation done rather than continuing the old checkpoint.
- The RBU VFS mutates the WAL filename buffer in `rbuVfsOpen()` by changing the suffix from `-wal` to `-oal`; this assumes SQLite-owned filename buffers are writable and formatted as expected in this code path.
- Locking behavior intentionally blocks exclusive locks before done to prevent automatic checkpointing at close. This can surprise integrations expecting ordinary SQLite close/checkpoint behavior.
- RBU temp-space accounting only applies to delete-on-close files associated with the RBU handle; other temporary allocations or lower VFS behavior may not be reflected in `szTemp`.

## Test Signals

- Geopoly SQL tests should cover `geopoly_bbox()`, `geopoly_group_bbox()`, `geopoly_contains_point()`, `geopoly_overlap()`, `geopoly_within()`, rowid lookup, overlap/within indexed queries, inserts/updates/deletes of `_shape`, malformed polygons, rowid conflicts, and concurrent cursor/write locking.
- R-tree callback tests should register geometry and query callbacks, pass multiple SQL parameter types, verify MATCH receives duplicated parameters, and verify destructor paths.
- ICU tests should exercise Unicode `LIKE` with `%`, `_`, ESCAPE, long pattern rejection, `REGEXP` success/failure and invalid regex errors, locale-sensitive upper/lower behavior, collation loading with valid/invalid strengths, and extension init paths.
- FTS3 ICU tokenizer tests should cover locale-specific word breaks, UTF-8 offset reporting, whitespace skipping, empty/null input, invalid UTF sequences, and buffer growth when converting tokens back to UTF-8.
- RBU open/step/close tests should cover fresh updates, resume after `sqlite3rbu_savestate()`, resume after `sqlite3rbu_close()`, empty updates, update databases with `dataN_table` ordering, and malformed `rbu_control` values.
- RBU table-shape tests should include rowid tables, explicit integer primary keys, external primary keys, WITHOUT ROWID tables, virtual tables, required/prohibited `rbu_rowid`, missing columns, not-null/PK enforcement, expression indexes, partial indexes, unique indexes, and descending PK/index columns.
- RBU operation tests should cover insert, delete, replace, update masks with `x`, no-op `.`, `d` delta, and `f` fossil delta; IPK NULL insert mismatch; non-existing delete/update rows; and index b-tree maintenance via `rbu_tmp_xxx` triggers.
- RBU persistence tests should interrupt in OAL, MOVE, and CKPT stages, verify `rbu_state` fields, verify database cookie mismatch detection, verify OAL size continuation, verify WAL checksum mismatch behavior, and confirm progress APIs return sensible phase-one/phase-two values.
- RBU VFS tests should cover `*-wal` to `*-oal` substitution, heap SHM in OAL stage, denied WAL-mode targets, exclusive checkpoint URI behavior, zipvfs stack detection, temp-size limits, sector-size grouping during checkpoint, 8.3 filename suffix shortening, custom rename handlers, and cleanup of private VFS/file lists.

### subset-b-009042: lines 226498-234635

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 226498-234635

## Scope and Purpose

This chunk covers a late slice of SQLite's amalgamated extension code. It begins in the tail of the RBU VFS implementation, includes the complete `dbstat` and `sqlite_dbpage` virtual table modules, then enters most of the session extension through changeset generation, iteration, apply, changegroup merge, and the main rebase transformation loop. The range ends inside `sessionRebase()` after assigning an owned output buffer, before the local cleanup and public `sqlite3rebaser_*` wrappers in the next lines.

The code is compiled conditionally. RBU requires `!SQLITE_CORE || SQLITE_ENABLE_RBU`; `dbstat` and `dbpage` require their feature flags or test builds and no virtual-table omission; the session module requires both `SQLITE_ENABLE_SESSION` and `SQLITE_ENABLE_PREUPDATE_HOOK`.

Operationally, this chunk exposes low-level database introspection and replication/synchronization primitives:

- RBU VFS wrappers register and destroy a VFS that redirects selected file operations during resumable bulk update.
- `dbstat` scans btree pages and reports per-page or aggregate space usage.
- `sqlite_dbpage` reads and writes raw database pages through the pager.
- The session extension records table changes through preupdate hooks, serializes changesets/patchsets, parses and inverts changesets, applies changes with conflict handling, merges multiple changesets, and starts rebase support.

## RBU VFS Tail

The visible RBU section finishes VFS delegation and lifecycle APIs:

- `rbuVfsAccess()` has special handling for `SQLITE_ACCESS_EXISTS` during `RBU_STAGE_OAL`. It finds the main database wrapper with `rbuFindMaindb()`, detects whether SQLite is checking for the real WAL file while the RBU VFS wants an `*-oal` file, and either returns `SQLITE_CANTOPEN` or synthesizes existence from `rbuVfsFileSize()`.
- `rbuVfsFullPathname()`, dynamic library hooks, randomness, sleep, and current-time hooks are direct pass-throughs to `pRealVfs`.
- `rbuVfsGetLastError()` is a no-op returning 0.
- `sqlite3rbu_create_vfs()` allocates an `rbu_vfs`, copies a `sqlite3_vfs` template, points it at a parent VFS, sizes `szOsFile` to include `rbu_file` plus the parent file object, allocates a recursive mutex, and registers the new VFS as non-default.
- `sqlite3rbu_destroy_vfs()` only frees VFS objects whose `xOpen` is `rbuVfsOpen`, preventing accidental destruction of unrelated VFS registrations.
- `sqlite3rbu_temp_size_limit()` and `sqlite3rbu_temp_size()` expose per-RBU temporary storage accounting.

This code depends on earlier RBU types and functions outside the chunk, especially `rbu_vfs`, `rbu_file`, `sqlite3rbu`, `rbuVfsOpen()`, `rbuVfsDelete()`, `rbuVfsFileSize()`, `rbuFindMaindb()`, and the RBU stage constants.

## DBSTAT Virtual Table

`dbstat` implements a virtual table with schema:

`name, path, pageno, pagetype, ncell, payload, unused, mx_payload, pgoffset, pgsize, schema HIDDEN, aggregate HIDDEN`.

Important types:

- `StatCell` stores per-cell local payload size, child page number, overflow-page list, final overflow bytes, and overflow iteration cursor.
- `StatPage` stores copied page bytes, page number, btree path, parsed flags, cell count, unused bytes, parsed cells, right-child page, and maximum payload.
- `StatCursor` maintains the root-page statement, EOF/aggregate state, active schema, a fixed stack of 32 `StatPage` frames, and the current column values.
- `StatTable` stores the owning `sqlite3*` and default schema index.

Important APIs and methods:

- `statConnect()` resolves the optional schema argument, declares the virtual table, marks it `SQLITE_VTAB_DIRECTONLY`, and stores the default database index.
- `statBestIndex()` recognizes equality constraints on `schema`, `name`, and `aggregate`, refuses unusable constraints so the module remains right-most in joins, advertises natural `(name, path)` ordering, and sets `SQLITE_INDEX_SCAN_HEX`.
- `statOpen()`, `statClose()`, `statResetCsr()`, `statClearPage()`, and `statClearCells()` manage cursor and page/cell allocations.
- `getLocalPayload()` implements SQLite btree local-payload sizing for table leaves versus index/interior pages.
- `statDecodePage()` parses a copied btree page, validates page flags and freeblock chains, decodes cells, calculates unused bytes, local payload, maximum payload, child links, and overflow chains by reading overflow pages through the pager.
- `statGetPage()` obtains a pager page and copies it into a malloc buffer padded by `DBSTAT_PAGE_PADDING_BYTES` to tolerate small overreads while inspecting corrupt pages.
- `statSizeAndOffset()` calculates page size and file offset. It first tries ZIPVFS file-control opcode `230440`, then falls back to normal page-size arithmetic.
- `statNext()` is the main traversal state machine. It steps a root-page query, pushes child pages on `aPage[]`, walks cells and right children depth-first, emits overflow pages as separate rows, or accumulates the whole btree in aggregate mode.
- `statFilter()` builds a query over `sqlite_schema`, optionally constrains by table/index name, optionally orders by name, and starts traversal.
- `statColumn()` returns per-page values or aggregate values depending on `isAgg`.
- `sqlite3DbstatRegister()` registers module name `dbstat`.

Control flow is btree-oriented. `statFilter()` selects root pages, `statNext()` loads a root and decodes a page, then repeatedly emits the current page, its overflow pages, and descendants. In aggregate mode, it suppresses per-page rows and keeps walking until the current btree is exhausted, then returns one accumulated row.

State is cursor-local and read-only against database contents. It uses pager snapshots so WAL/uncommitted pager-visible state is reflected consistently with SQLite internals. Corrupt page structures generally clear parsed cells and label the page as `corrupted` instead of always failing, but impossible traversal depth returns `SQLITE_CORRUPT_BKPT`.

## SQLITE_DBPAGE Virtual Table

`sqlite_dbpage` is an eponymous virtual table for raw page access:

`pgno INTEGER PRIMARY KEY, data BLOB, schema HIDDEN`.

Important types and APIs:

- `DbpageCursor` tracks the current page number, max page number, pager, page-1 reference, schema index, and page size.
- `DbpageTable` stores the database handle plus pending truncate state (`iDbTrunc`, `pgnoTrunc`).
- `dbpageConnect()` declares the table, marks it `SQLITE_VTAB_DIRECTONLY` and `SQLITE_VTAB_USES_ALL_SCHEMAS`.
- `dbpageBestIndex()` plans schema and page-number equality constraints, with unique scan flags for `pgno=?`.
- `dbpageFilter()` resolves the schema, initializes pager/page-size information, bounds scans to one page if `pgno=?`, and pins page 1.
- `dbpageColumn()` returns `pgno`, a transient copy of page data, or schema name. It treats the pending-byte page as a zero blob because asking the pager for it is corrupt.
- `dbpageUpdate()` supports raw page replacement and extension through pager write calls. It rejects writes in defensive mode, rejects deletes, requires BLOB page data exactly equal to the page size, and interprets `INSERT(pgno, NULL)` for `pgno>1` as a pending truncate to `pgno-1`.
- `dbpageBeginTrans()` begins write transactions on all attached btrees because the updated schema may be supplied per row.
- `dbpageSync()` applies a pending truncate just before commit with `sqlite3PagerTruncateImage()`.
- `dbpageRollbackTo()` cancels pending truncation.
- `sqlite3DbpageRegister()` registers module name `sqlite_dbpage`.

This module is intentionally dangerous. It integrates directly with `Btree`, `Pager`, and `DbPage`; it can overwrite raw database pages and truncate the database image. The defensive-mode guard and direct-only virtual table configuration are important safety boundaries.

## Session Core Data Model

The session module begins with stream sizing constants and core structs:

- `sqlite3_session` owns the database handle, attached schema name, recording flags, auto-attach/filter settings, implicit-rowid-PK support, error state, memory accounting, optional max-changeset-size accounting, zero-blob value for `sqlite_stat1`, linked sessions on the same database, attached `SessionTable` list, and a `SessionHook`.
- `SessionHook` abstracts preupdate/diff access through `xOld`, `xNew`, `xCount`, and `xDepth`.
- `SessionBuffer` is a growable byte buffer for SQL strings, records, changesets, rebase blobs, and deferred constraint blobs.
- `SessionInput` abstracts fixed-buffer and streaming input, including current/next offsets and stream-discard policy.
- `sqlite3_changeset_iter` stores the current input stream, decoded table header, patchset/invert/skip-empty flags, current operation, table metadata, old/new value arrays, and optional conflict row statement.
- `SessionTable` stores table metadata, column/default/PK arrays, hidden-column mapping, rowid-PK/stat1 flags, hash-table buckets of `SessionChange`, and default-value statement.
- `SessionChange` stores one accumulated row change: operation, indirect flag, number of serialized fields, maximum output size estimate, serialized old/PK record bytes, and hash-chain link.

The on-disk/over-the-wire record format is explicitly architecture-independent: one type byte per field, varint lengths for text/blob, and big-endian 8-byte integer/float payloads. Changesets use `T` table headers and old/new records; patchsets use `P` headers and omit values not needed for conflict-free application; rebase blobs use table headers plus per-conflict insert/delete records and replace/omit flags.

## Serialization, Hashing, and Table Metadata

Important helper families:

- Varint and endian helpers: `sessionVarintPut()`, `sessionVarintLen()`, `sessionVarintGet()`, `sessionGetI64()`, and `sessionPutI64()`.
- Value serialization: `sessionSerializeValue()`, `sessionAppendValue()`, `sessionAppendCol()`, `sessionReadRecord()`, `sessionSerialLen()`, and `sessionValueSetStr()`.
- Buffer growth and SQL/string construction: `sessionBufferGrow()`, `sessionAppendStr()`, `sessionAppendPrintf()`, `sessionAppendByte()`, `sessionAppendVarint()`, `sessionAppendBlob()`, `sessionAppendInteger()`, and `sessionAppendIdent()`.
- PK hashing/comparison: `sessionPreupdateHash()`, `sessionChangeHash()`, `sessionChangeEqual()`, and `sessionPreupdateEqual()`.
- Record merge/update helpers: `sessionMergeRecord()`, `sessionMergeValue()`, `sessionMergeUpdate()`, `sessionSkipRecord()`, `sessionAppendRecordMerge()`, and `sessionAppendPartialUpdate()`.
- Table introspection: `sessionTableInfo()` reads `PRAGMA table_xinfo()` or synthesizes `sqlite_stat1` metadata; `sessionInitTable()` initializes `SessionTable`; `sessionReinitTable()` detects compatible schema growth; `sessionPrepareDfltStmt()`, `sessionUpdateOneChange()`, and `sessionUpdateChanges()` extend older change records with defaults after `ALTER TABLE ADD COLUMN`.

The hash table key is the row primary key. Tables without primary keys are ignored, unless implicit rowid-PK mode is enabled before attaching tables. `sqlite_stat1` is special: the module treats `(tbl, idx)` as a logical primary key and maps NULL `idx` values to a zero-length blob internally so serialized PK matching remains possible.

## Recording Changes

Session recording is built around SQLite's preupdate hook:

- `sqlite3session_create()` allocates a session, installs `xPreUpdate` as the database preupdate hook, and links the new session into the hook's linked list.
- `sqlite3session_delete()` removes the session from that linked list, restores the hook to the next session if needed, frees the zero blob, tables, changes, and the session object.
- `sqlite3session_attach()` either enables auto-attach (`zName==NULL`) or adds a named table to the session's ordered table list.
- `sqlite3session_table_filter()` configures an auto-attach filter.
- `sqlite3session_enable()` and `sqlite3session_indirect()` toggle recording and indirect-change marking under the database mutex.
- `sqlite3session_isempty()`, `sqlite3session_memory_used()`, `sqlite3session_object_config()`, and `sqlite3session_changeset_size()` expose state and configuration.

`xPreUpdate()` iterates all sessions attached to the connection, filters by enabled state and schema, auto-attaches tables if configured, and calls `sessionPreupdateOneChange()`. For UPDATE, it records both the old row (`SQLITE_UPDATE`) and the new PK identity (`SQLITE_INSERT`) so rowid/PK changes are represented correctly.

`sessionPreupdateOneChange()` initializes table metadata, handles schema growth, grows the per-table hash table, computes the PK hash from old or new values, ignores rows with NULL primary-key columns, finds any existing `SessionChange`, and either creates a serialized baseline record or updates direct/indirect and size-estimate metadata. It carefully separates fatal OOM from non-fatal hash-growth failures and propagates hard errors through `pSession->rc`.

## Diff and Changeset Generation

`sqlite3session_diff()` compares a table in the session database against the same table in another attached database. It installs `SessionDiffCtx` hooks over SELECT statements, checks that source and target schemas/PK layouts match, then records inserts, deletes, and modified rows using generated SQL:

- `sessionExprComparePK()` builds equality predicates for primary keys.
- `sessionExprCompareOther()` builds non-PK difference predicates.
- `sessionSelectFindNew()` and `sessionDiffFindNew()` find rows present in one database and not the other.
- `sessionAllCols()` and `sessionDiffFindModified()` join matching PK rows and record value differences.

`sessionGenerateChangeset()` produces changesets or patchsets. It wraps generation in a `SAVEPOINT changeset`, revalidates table schema, emits table headers with `sessionAppendTableHdr()`, prepares a PK lookup with `sessionSelectStmt()`, binds primary keys with `sessionSelectBind()`, then emits:

- `SQLITE_INSERT` with current full row values when the row still exists and the original op was insert.
- `SQLITE_UPDATE` through `sessionAppendUpdate()` when original values differ from current values.
- `SQLITE_DELETE` through `sessionAppendDelete()` when a previously existing row no longer exists.

Streaming variants call `xOutput` whenever the buffer exceeds `sessions_strm_chunk_size`. Non-streaming variants return an allocated buffer owned by the caller.

Public generation APIs in this chunk include `sqlite3session_changeset()`, `sqlite3session_changeset_strm()`, `sqlite3session_patchset()`, and `sqlite3session_patchset_strm()`.

## Changeset Iteration and Inversion

Iterator creation is centralized in `sessionChangesetStart()`, used by fixed-buffer and streaming public APIs:

- `sqlite3changeset_start()`
- `sqlite3changeset_start_v2()` with `SQLITE_CHANGESETSTART_INVERT`
- `sqlite3changeset_start_strm()`
- `sqlite3changeset_start_v2_strm()`

Input buffering is handled by `sessionInputBuffer()` and `sessionDiscardData()`. Streaming input keeps enough bytes buffered for the current table header or record, while `bNoDiscard` preserves record bytes for callers that need raw slices.

`sessionChangesetNextOne()` is the parser state machine. It reads `T` or `P` table headers, validates operation bytes, decodes old/new records or buffers raw record bytes, supports inverted iteration, shifts patchset UPDATE PK fields into old-value slots, and normalizes questionable changeset UPDATE records that include old non-PK values without corresponding new values. `sessionChangesetNext()` optionally skips empty UPDATEs.

Public iterator APIs include:

- `sqlite3changeset_next()`
- `sqlite3changeset_op()`
- `sqlite3changeset_pk()`
- `sqlite3changeset_old()`
- `sqlite3changeset_new()`
- `sqlite3changeset_conflict()`
- `sqlite3changeset_fk_conflicts()`
- `sqlite3changeset_finalize()`

`sessionChangesetInvert()` constructs an inverse changeset. INSERT and DELETE swap operation codes while preserving records. UPDATE reads old/new records, writes a new old record made from PK columns plus original new non-PK values, then writes a new new record from original old non-PK values with PK columns undefined. Public inversion APIs are `sqlite3changeset_invert()` and `sqlite3changeset_invert_strm()`.

## Applying Changesets

The apply path centers on `SessionApplyCtx`, which stores prepared statements, target schema metadata, cached UPDATE statements, deferred constraint buffers, optional rebase output, and flags for `sqlite_stat1`, deferred constraints, inverted constraint replay, rowid-PK mode, and no-op ignoring.

Statement construction and binding helpers:

- `sessionUpdateFind()` builds and caches UPDATE statements keyed by a bitmask of modified columns; cache size is limited by `SESSION_UPDATE_CACHE_SZ`.
- `sessionUpdateFree()` releases cached UPDATE statements.
- `sessionDeleteRow()` builds DELETE SQL using PK predicates plus optional non-PK data checks.
- `sessionSelectRow()` reuses `sessionSelectStmt()` for target-row lookup.
- `sessionInsertRow()` builds INSERT SQL over all target columns.
- `sessionStat1Sql()` prepares special SQL that maps zero-length-blob sentinel values back to NULL `idx`.
- `sessionBindValue()`, `sessionBindRow()`, and `sessionSeekToRow()` bind changeset values and seek target rows.

Conflict and retry flow:

- `sessionConflictHandler()` invokes the user callback with `SQLITE_CHANGESET_DATA`, `NOTFOUND`, `CONFLICT`, or `CONSTRAINT` depending on operation outcome and whether a matching PK row exists. It can defer constraint conflicts into `constraints`, reject invalid callback returns, and append rebase records through `sessionRebaseAdd()`.
- `sessionApplyOneOp()` attempts DELETE, UPDATE, or INSERT. It detects no-row changes as data/notfound conflicts and constraint failures as conflict/constraint cases.
- `sessionApplyOneWithRetry()` handles `SQLITE_CHANGESET_REPLACE`: retrying UPDATE/DELETE while ignoring data mismatches, or deleting a conflicting row in a `SAVEPOINT replace_op` before retrying INSERT.
- `sessionRetryConstraints()` replays deferred constraint changes until no progress is made or all succeed.
- `sessionChangesetApply()` runs the overall apply transaction. It optionally creates `SAVEPOINT changeset_apply`, enables deferred foreign keys, groups work by table, invokes the table filter, validates target schema and PK compatibility, prepares statements, applies each operation, retries deferred constraints, checks remaining foreign-key violations through the conflict handler, releases or rolls back the savepoint, returns optional rebase data, and restores `SQLITE_FkNoAction` state if requested.

Public apply APIs include `sqlite3changeset_apply_v2()`, `sqlite3changeset_apply()`, `sqlite3changeset_apply_v2_strm()`, and `sqlite3changeset_apply_strm()`.

## Changegroup and Rebase Logic

`sqlite3_changegroup` accumulates multiple changesets or patchsets into per-table hash tables and later serializes a merged result. It stores error state, patchset/changeset mode, a table list, a scratch record buffer, and optional schema database information for extending older records.

Important APIs and merge helpers:

- `sqlite3changegroup_new()` allocates an empty group.
- `sqlite3changegroup_schema()` attaches schema context for compatibility with changesets generated before added columns.
- `sqlite3changegroup_add()` and `sqlite3changegroup_add_strm()` parse input into the group.
- `sqlite3changegroup_add_change()` adds the current iterator entry.
- `sqlite3changegroup_output()` and `sqlite3changegroup_output_strm()` serialize accumulated changes.
- `sqlite3changegroup_delete()` frees all tables, records, schema strings, and scratch buffers.
- `sqlite3changeset_concat()` and `sqlite3changeset_concat_strm()` are convenience wrappers around a changegroup.
- `sessionChangesetFindTable()` finds/creates compatible `SessionTable` objects for incoming changes.
- `sessionChangesetExtendRecord()` appends default or undefined fields when combining changesets with fewer columns than the schema-aware group table.
- `sessionOneChangeToHash()` locates existing changes by PK, removes them, merges them, and reinserts the merged result.
- `sessionChangeMerge()` implements the operation-combination matrix: insert+update stays insert, insert+delete cancels out, update+update merges, update+delete becomes delete, delete+insert becomes update, and unsupported duplicate/out-of-order combinations discard the second operation. In rebase mode, it also uses `0xFF` markers for replaced fields.

`sqlite3_rebaser` is introduced as a wrapper around a `sqlite3_changegroup`. The visible `sessionRebase()` function rebases a local changeset against rebase records already loaded into that group:

- It iterates input changes with raw record access and detects new table headers.
- Patchsets are rejected for rebasing.
- If no rebase record matches the row, it copies the original operation and record.
- If a matching remote rebase change exists, it transforms local INSERT/UPDATE/DELETE according to the remote operation and whether the remote change was indirect.
- It can drop operations made obsolete by remote changes, convert INSERT into UPDATE, convert UPDATE into INSERT, or rewrite old/new records with `sessionAppendPartialUpdate()` and `sessionAppendRecordMerge()`.
- The chunk ends while `sessionRebase()` is transferring `sOut.aBuf` into `*ppOut`/`*pnOut`; cleanup and public `sqlite3rebaser_*` functions are in the following source lines.

## State and Persistence Behavior

RBU VFS state is persisted in the registered VFS object, its parent pointer, mutex, and per-file wrappers. The temp-size limit and current temp usage live on each `sqlite3rbu` handle.

`dbstat` state is transient cursor state. It copies page contents into cursor-owned buffers and frees parsed cell/overflow allocations as pages are popped from the traversal stack. It does not mutate the database.

`sqlite_dbpage` read state is transient, but write state persists through pager writes and commit-time truncation. `pgnoTrunc` is intentionally held on the virtual table object until `xSync` or rollback-to clears it.

Session state is persistent for the lifetime of the `sqlite3_session`: attached table metadata, change hash tables, memory accounting, max-size estimate, and error state remain until deletion or until changesets are generated. Generated changesets, patchsets, rebase blobs, and changegroup outputs are allocated buffers that the public API expects callers to free with SQLite allocation routines. Apply state is temporary and transaction-scoped, protected by savepoints and database mutexes.

Schema changes are handled conservatively. Added non-PK columns may be tolerated by extending existing records with default or undefined values. PK layout changes, removed columns, rowid-PK mode changes, or incompatible table definitions produce `SQLITE_SCHEMA`.

## Dependencies and Integration Points

This chunk depends heavily on SQLite internal APIs:

- Virtual table APIs: `sqlite3_module`, `sqlite3_vtab_config()`, `sqlite3_declare_vtab()`, `sqlite3_create_module()`, `sqlite3_index_info`, and xBestIndex/xFilter/xColumn/xUpdate contracts.
- Pager/btree internals: `Btree`, `Pager`, `DbPage`, `sqlite3BtreePager()`, `sqlite3PagerGet()`, `sqlite3PagerWrite()`, `sqlite3PagerUnref()`, `sqlite3BtreeGetPageSize()`, `sqlite3BtreeLastPage()`, `sqlite3BtreeBeginTrans()`, and related mutex enter/leave calls.
- Preupdate hooks: `sqlite3_preupdate_hook()`, `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and `sqlite3_preupdate_blobwrite()`.
- VDBE/value internals: `sqlite3_value`, `sqlite3ValueNew()`, `sqlite3ValueSetStr()`, `sqlite3ValueFree()`, `sqlite3VdbeMemSetInt64()`, and `sqlite3VdbeMemSetDouble()`.
- SQL compiler/runtime APIs: `sqlite3_prepare_v2()`, `sqlite3_prepare()`, `sqlite3_step()`, `sqlite3_reset()`, `sqlite3_finalize()`, `sqlite3_bind_*()`, `sqlite3_column_*()`, `sqlite3_exec()`, and `sqlite3_db_status()`.
- Core utility APIs: SQLite malloc/realloc/free, `sqlite3_mprintf()`, `sqlite3_str`, varint helpers, identifier quoting through `%w`, and mutex APIs.

Integration points include command-line/diagnostic use of `dbstat`, privileged raw-page tooling through `sqlite_dbpage`, application-level replication/synchronization through the session extension, conflict handlers supplied by callers of changeset apply, and optional streaming callbacks for large changesets.

## Risks and Edge Cases

- The chunk starts inside `rbuVfsAccess()`, so preceding RBU open/delete/file-wrapper logic must be reconciled with earlier chunks.
- The chunk ends inside `sessionRebase()`, so the final cleanup and public rebaser wrapper APIs must be reconciled with the next chunk.
- `dbstat` uses a fixed 32-entry page stack. Extremely deep or corrupt btrees can trigger `SQLITE_CORRUPT_BKPT`.
- `dbstat` intentionally tolerates some corrupt page content by reporting `pagetype='corrupted'`; consumers should not interpret every row as proof of healthy btree structure.
- `statDecodePage()` reads overflow chains through the pager. Bad overflow pointers surface as pager errors or corrupt-state behavior.
- `sqlite_dbpage` can corrupt databases by writing arbitrary page images. `SQLITE_Defensive`, direct-only registration, page-size checks, and transaction boundaries are essential controls.
- `dbpageUpdate()` begins write transactions on all attached databases because schema is row data; this can increase lock scope.
- Changes for rows with NULL primary-key values are ignored by the session module because they cannot be matched reliably.
- Tables without primary keys are ignored unless implicit rowid-PK mode is enabled before tables are attached.
- `sqlite_stat1` requires special NULL/sentinel handling; mistakes there would break apply/merge behavior for statistics rows.
- Record parsing is defensive against negative/oversized lengths and malformed table headers, returning `SQLITE_CORRUPT_BKPT`.
- Streaming input discards old data unless `bNoDiscard` is set. Code paths that retain raw record pointers must enable no-discard behavior.
- Conflict callback return values are strictly validated. Returning `REPLACE` in unsupported contexts becomes `SQLITE_MISUSE`.
- Apply temporarily changes foreign-key behavior and can defer constraint conflicts. Failure paths must roll back savepoints and restore flags to avoid leaking changed connection state.
- Changeset concatenation order matters because the merge matrix is directional.
- Size and memory accounting rely on `sqlite3_msize()` and can diverge if allocations are not made through the session wrappers.

## Test Signals

Useful validation signals for this chunk:

- RBU VFS tests that create/destroy custom VFS names, use a parent VFS, enter OAL stage, and verify WAL/OAL access redirection and temp-size limits.
- `dbstat` tests over normal tables, indexes, overflow payloads, empty databases, aggregate mode, `schema=?`, `name=?`, `ORDER BY name,path`, attached databases, ZIPVFS file-control behavior, and deliberately corrupt btree pages.
- `sqlite_dbpage` tests for full scan, `pgno=?`, attached schema selection, pending-byte page reads, exact page-size BLOB writes, defensive-mode write rejection, NULL insert truncation, rollback cancellation, and commit-time truncation.
- Session recording tests for attach, auto-attach filters, enable/disable, indirect changes, UPDATE with changed PK, DELETE/INSERT cancellation, rowid implicit-PK mode, tables without PK, NULL PK values, and schema changes after recording starts.
- Changeset/patchset generation tests for inserts, deletes, updates, no-op updates, large streaming output, `sqlite_stat1`, UTF-8 conversion OOM paths, and max changeset size accounting.
- Iterator tests for fixed-buffer and streaming input, corrupt headers, corrupt record lengths, inversion flag behavior, patchset UPDATE PK movement, `old/new/op/pk/conflict/fk_conflicts` API misuse cases, and finalize error propagation.
- Apply tests for DATA, NOTFOUND, CONFLICT, CONSTRAINT, and FOREIGN_KEY conflict callbacks; `OMIT`, `ABORT`, and `REPLACE` outcomes; deferred constraints; no-op ignore; invert apply; no-savepoint mode; rebase output; schema mismatch logging; and `SQLITE_CHANGESETAPPLY_FKNOACTION`.
- Changegroup and concat tests for all merge matrix cases, patchset versus changeset mismatch, schema-aware extension of old records, streaming add/output, adding a single iterator change, and order preservation by table.
- Rebase tests for local INSERT/UPDATE/DELETE against remote insert/delete/update rebase records, indirect versus direct remote records, partial update field removal, generated empty updates, patchset rejection, and streaming threshold output.

## Cross-Chunk Notes

This is one chunk of the amalgamated `sqlite3.c` file. Adjacent chunks are needed to recover the start of `rbuVfsAccess()` and the definitions of RBU structures used here, plus the cleanup tail of `sessionRebase()` and public `sqlite3rebaser_*` APIs immediately after line 234635.

### subset-b-009043: lines 234636-242624

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 234636-242624

## Purpose

This chunk bridges the end of SQLite's session extension rebaser implementation into the beginning and early middle of the FTS5 amalgamated module. In the vendored SQLite source used by WiredTiger tests, it covers:

- The public `sqlite3rebaser_*()` API and `sqlite3session_config()` tail from `sqlite3session.c`.
- The FTS5 public extension header (`fts5.h`): auxiliary-function APIs, tokenizer APIs, synonym semantics, and the `fts5_api` registration surface.
- The FTS5 internal interface header (`fts5Int.h`): shared types, constants, and prototypes connecting config, buffer, index, hash, storage, expression, tokenizer, vocab, and unicode modules.
- The generated Lemon parser for FTS5 MATCH expressions.
- Built-in FTS5 auxiliary functions: `highlight()`, `snippet()`, `bm25()`, and `fts5_get_locale()`.
- Shared FTS5 buffer, position-list, malloc/string, and term-set helpers.
- FTS5 table configuration parsing and loading from `%_config`.
- The first large section of the FTS5 expression engine: MATCH tokenization/parsing, phrase/NEAR/column-set structures, iterator initialization, rowid set logic for TERM/STRING/AND/OR/NOT nodes, and parser construction of phrases and colsets.

This is not WiredTiger storage-engine code directly. It is a third-party SQLite amalgamation under `test/3rdparty`, so its main role in this repository is preserving SQLite behavior for tests or tools that compile this copy.

## Important APIs, Types, and Functions

Session/rebaser tail:

- `sqlite3rebaser_create()` allocates and zeroes a `sqlite3_rebaser`.
- `sqlite3rebaser_configure()` reads a rebase changeset with `sqlite3changeset_start()` and folds it into `p->grp` with `sessionChangesetToHash()`.
- `sqlite3rebaser_rebase()` and `sqlite3rebaser_rebase_strm()` run `sessionRebase()` over memory-backed or streaming changeset input.
- `sqlite3rebaser_delete()` releases table metadata, record buffers, and the rebaser itself.
- `sqlite3session_config()` currently handles `SQLITE_SESSION_CONFIG_STRMSIZE`, updating and returning `sessions_strm_chunk_size`; unknown operations return `SQLITE_MISUSE`.

FTS5 public extension API:

- `Fts5ExtensionApi` is the auxiliary-function callback table. It exposes query/row metadata (`xColumnCount`, `xRowCount`, `xColumnTotalSize`, `xColumnSize`, `xColumnText`, `xRowid`), match detail APIs (`xPhraseCount`, `xPhraseSize`, `xInstCount`, `xInst`, phrase iterators), query re-execution (`xQueryPhrase`), auxdata (`xSetAuxdata`, `xGetAuxdata`), token access (`xQueryToken`, `xInstToken`), locale lookup (`xColumnLocale`), and locale-aware tokenization (`xTokenize_v2`).
- `Fts5PhraseIter` stores opaque position-list iteration pointers for phrase/column iteration APIs.
- `fts5_extension_function` is the ABI for custom FTS5 auxiliary functions.
- `fts5_tokenizer_v2` is the modern tokenizer ABI, including locale parameters in `xTokenize()`. `fts5_tokenizer` is the older ABI without locale support.
- `FTS5_TOKENIZE_QUERY`, `FTS5_TOKENIZE_PREFIX`, `FTS5_TOKENIZE_DOCUMENT`, `FTS5_TOKENIZE_AUX`, and `FTS5_TOKEN_COLOCATED` define tokenizer request and synonym-output flags.
- `fts5_api` registers or looks up tokenizers and auxiliary functions, including v2 tokenizer variants.

FTS5 internal shared types and constants:

- `Fts5Config` captures parsed `CREATE VIRTUAL TABLE` options and loaded `%_config` values: database/table names, columns, unindexed flags, prefix indexes, content mode, content rowid, columnsize, tokendata, locale, detail mode, tokenizer config, rank config, automerge/crisismerge/usermerge/hashsize/page-size settings, secure-delete, delete-merge, and prefix-insttoken.
- `Fts5TokenizerConfig` stores the tokenizer object/API, tokenizer arguments, trigram pattern mode, and current locale.
- `Fts5Colset` is an ordered set of searchable columns used by expression evaluation and index queries.
- `Fts5Buffer` is the module's growable byte buffer used by config SQL strings, position lists, and serialized data.
- `Fts5PoslistReader`, `Fts5PoslistWriter`, and `Fts5LookaheadReader` decode and encode FTS5 position lists.
- `Fts5IndexIter` exposes an index iterator's current rowid, position-list blob, size, and EOF flag.
- `Fts5Table` binds the virtual table shell to an `Fts5Config` and `Fts5Index`.
- `Fts5Expr`, `Fts5ExprNode`, `Fts5ExprTerm`, `Fts5ExprPhrase`, `Fts5ExprNearset`, and `Fts5Parse` define parsed MATCH expressions and their runtime iterator state.

Key FTS5 helper functions in this chunk:

- Parser entry points: `sqlite3Fts5ExprNew()`, `sqlite3Fts5ExprPattern()`, `sqlite3Fts5ExprAnd()`, `sqlite3Fts5ExprFree()`, `sqlite3Fts5ExprClonePhrase()`.
- Expression iteration: `sqlite3Fts5ExprFirst()`, `sqlite3Fts5ExprNext()`, `sqlite3Fts5ExprEof()`, `sqlite3Fts5ExprRowid()`, `fts5ExprNodeFirst()`, `fts5ExprNodeNext_TERM()`, `fts5ExprNodeNext_STRING()`, `fts5ExprNodeNext_OR()`, `fts5ExprNodeNext_AND()`, `fts5ExprNodeNext_NOT()`.
- Phrase and NEAR matching: `fts5ExprPhraseIsMatch()`, `fts5ExprNearIsMatch()`, `fts5ExprNearTest()`, `fts5ExprNearInitAll()`, `fts5ExprSynonymList()`, `fts5ExprSynonymRowid()`, `fts5ExprSynonymAdvanceto()`.
- Parse actions/helpers: `fts5ExprGetToken()`, `sqlite3Fts5ParseTerm()`, `fts5ParseTokenize()`, `sqlite3Fts5ParseNearset()`, `sqlite3Fts5ParseSetCaret()`, `sqlite3Fts5ParseNear()`, `sqlite3Fts5ParseSetDistance()`, `sqlite3Fts5ParseColset()`, `sqlite3Fts5ParseColsetInvert()`, `sqlite3Fts5ParseSetColset()`.
- Config parsing/loading: `sqlite3Fts5ConfigParse()`, `fts5ConfigParseSpecial()`, `fts5ConfigParseColumn()`, `fts5ConfigMakeExprlist()`, `sqlite3Fts5ConfigDeclareVtab()`, `sqlite3Fts5Tokenize()`, `sqlite3Fts5ConfigParseRank()`, `sqlite3Fts5ConfigSetValue()`, `sqlite3Fts5ConfigLoad()`, `sqlite3Fts5ConfigErrmsg()`, `sqlite3Fts5ConfigFree()`.
- Built-ins: `fts5HighlightFunction()`, `fts5SnippetFunction()`, `fts5Bm25Function()`, `fts5GetLocaleFunction()`, and `sqlite3Fts5AuxInit()`.
- Buffer/poslist utilities: `sqlite3Fts5BufferSize()`, `sqlite3Fts5BufferAppendVarint()`, `sqlite3Fts5BufferAppendBlob()`, `sqlite3Fts5BufferAppendString()`, `sqlite3Fts5BufferAppendPrintf()`, `sqlite3Fts5Mprintf()`, `sqlite3Fts5BufferFree()`, `sqlite3Fts5BufferSet()`, `sqlite3Fts5PoslistNext64()`, `sqlite3Fts5PoslistReaderInit()`, `sqlite3Fts5PoslistWriterAppend()`, `sqlite3Fts5PoslistSafeAppend()`, `sqlite3Fts5MallocZero()`, and `sqlite3Fts5Strndup()`.
- Term-set integrity support: `sqlite3Fts5TermsetNew()`, `sqlite3Fts5TermsetAdd()`, and `sqlite3Fts5TermsetFree()`.

The final line in this assigned range is the opening of `fts5ExprAssignXNext()`. Its switch body and downstream parse-node construction continue in the following chunk.

## Control Flow

The session rebaser path is short and linear. A rebaser is allocated zero-filled, configured by converting a rebase changeset into a hash/group representation, then used to transform an input changeset through `sessionRebase()`. The streaming variant substitutes `sqlite3changeset_start_strm()` and an output callback. All iterator paths finalize the changeset iterator when initialization succeeded.

FTS5 module initialization begins by exposing the public extension ABI, then declaring internal cross-module contracts. The code in this chunk is organized by amalgamated source file: public API declarations, internal declarations, generated parser code, built-in auxiliary functions, generic helpers, config parsing, and expression evaluation.

The generated Lemon parser takes tokens from `fts5ExprGetToken()` and reduces them into expression nodes, nearsets, phrases, colsets, and prefix flags. Important grammar actions include:

- `expr AND expr`, `expr OR expr`, and `expr NOT expr` reduce into internal expression nodes via `sqlite3Fts5ParseNode()`.
- Adjacent `exprlist cnearset` reduces through `sqlite3Fts5ParseImplicitAnd()`.
- `colset : expr` or `colset : nearset` applies a column filter through `sqlite3Fts5ParseSetColset()`.
- `NEAR(...)` validates the `NEAR` keyword, parses optional distance, and stores it on a nearset.
- `phrase PLUS STRING star_opt` appends a tokenized term to an existing phrase.
- `STRING star_opt` creates a new phrase, optionally marking its final term as a prefix query.

`sqlite3Fts5ExprNew()` owns MATCH expression compilation. It allocates a Lemon parser, feeds tokens until `FTS5_EOF` or parse error, applies an implicit left-hand-column filter when `iCol` names a real table column, and wraps the parse tree and phrase array into an `Fts5Expr`.

`sqlite3Fts5ExprPattern()` is a special trigram-tokenizer path for LIKE/GLOB planning. It extracts literal spans of at least three UTF-8 characters from the pattern, quotes them into a generated MATCH expression, and compiles that expression as a superset filter. For reduced-detail tables it may force phrase-to-AND behavior or disable the column filter.

Expression iteration is tree-driven:

- `sqlite3Fts5ExprFirst()` binds an `Fts5Index`, records rowid order, initializes all expression-node iterators with `fts5ExprNodeFirst()`, optionally seeks to `iFirst`, then skips `bNomatch` pseudo-matches.
- `sqlite3Fts5ExprNext()` advances the root with its `xNext` method until a real match or EOF, then enforces the caller's rowid boundary.
- TERM nodes use a single index iterator and can point phrase position lists directly at index iterator data in `detail=full`.
- STRING nodes coordinate multiple term iterators, synonyms, phrase adjacency, first-token constraints, NEAR distance, and column filters before admitting a row.
- OR nodes choose the earliest child in iteration order, preferring real matches over `bNomatch` rows for equal rowids.
- AND nodes repeatedly advance lagging children until all children land on the same rowid, carrying child `bNomatch` state.
- NOT nodes advance the right child to the left child's rowid and skip left-side rows suppressed by a matching right side.

The auxiliary functions run through the `Fts5ExtensionApi` rather than direct internal structures. `highlight()` obtains column text, locale, and coalesced match instances, then re-tokenizes the column to splice open/close markers around token ranges. `snippet()` scores possible windows around phrase instances and sentence starts, then reuses the highlight callback over the chosen window. `bm25()` lazily allocates per-query data in FTS5 auxdata, computes row count, total token count, per-phrase document frequency through `xQueryPhrase()`, then scores each row using per-column weights. `fts5_get_locale()` validates a single integer column argument and returns `xColumnLocale()` output.

Config parsing is also staged. `sqlite3Fts5ConfigParse()` allocates a config object, pre-allocates column/unindexed arrays, parses each virtual-table argument as either an option (`name=value`) or a column declaration, applies option-specific validators, enforces cross-option constraints, fills default content table/rowid names, and builds `zContentExprlist`. `sqlite3Fts5ConfigLoad()` later reads runtime options from `%_config`, applies defaults before scanning rows, validates the FTS5 file-format version, and stores an `iCookie` snapshot.

## State and Persistence Behavior

The rebaser stores persistent-in-object state in `sqlite3_rebaser.grp`: configured table records and a reusable record buffer. `sqlite3rebaser_configure()` can be called more than once, merging changeset conflict/rebase data into that group until `sqlite3rebaser_delete()` frees it.

FTS5 configuration state is split between parse-time virtual-table schema options and persisted `%_config` table values. Parse-time options determine columns, content mode, tokenizer arguments, prefix indexes, locale/tokendata/detail behavior, content rowid, and generated content select lists. `%_config` values determine mutable runtime/index settings such as page size, automerge, usermerge, crisismerge, hashsize, rank function, secure-delete, delete-merge, and insttoken behavior. `sqlite3Fts5ConfigLoad()` resets defaults before loading persisted values, so missing keys use compile-time defaults.

FTS5 content persistence is represented in this chunk by names and SQL fragments, not by the table creation code itself. `zContent` may identify `%_content`, `%_docsize`, an external content table, or no content table depending on `content=`, `columnsize=`, and contentless options. `zContentExprlist` is built as a SQL expression list selecting rowid and columns from alias `T`, with `NULL` placeholders for non-stored columns and locale columns when appropriate.

Expression state is mostly in-memory and iterator-local:

- Each `Fts5ExprTerm` owns token text, prefix/first flags, optional synonym list, and an `Fts5IndexIter`.
- Each `Fts5ExprPhrase` owns a current-row position-list buffer unless it can alias index iterator data for simple TERM matches.
- Each `Fts5ExprNearset` owns phrase pointers, a NEAR distance, and optional colset.
- Each `Fts5ExprNode` owns rowid/EOF/nomatch state plus its child pointers or nearset.
- `Fts5Expr` owns the parse root and phrase pointer array.

Position lists are delta-varint encoded with column markers. `sqlite3Fts5PoslistNext64()` decodes entries into `(column << 32) + offset`, treating certain malformed records as EOF/corruption-tolerant stop points. Writers preserve sorted order and column transitions through `sqlite3Fts5PoslistSafeAppend()`.

Auxiliary-function state may persist for the duration of one MATCH query through FTS5 auxdata. `bm25()` uses `xGetAuxdata()`/`xSetAuxdata()` to cache `Fts5Bm25Data`, including IDF values and reusable frequency storage. `highlight()` and `snippet()` allocate only per-call buffers and free them before returning.

Memory ownership is explicit throughout. Parse helpers transfer phrase/nearset ownership into expression nodes, free both old and new objects on OOM where appropriate, and close term iterators in `fts5ExprPhraseFree()`. Config teardown deletes tokenizer instances with the matching v1/v2 `xDelete()` API, then frees all strings and arrays.

## Dependencies and Integration Points

This code integrates with several SQLite subsystems:

- Session extension internals: `sqlite3_changeset_iter`, `sqlite3changeset_start()`, `sqlite3changeset_start_strm()`, `sqlite3changeset_finalize()`, `sessionChangesetToHash()`, `sessionRebase()`, `sessionDeleteTable()`, and session-global stream chunk sizing.
- SQLite public memory and value APIs: `sqlite3_malloc*()`, `sqlite3_realloc*()`, `sqlite3_free()`, `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_value_*()`, `sqlite3_result_*()`, and SQLite result/error codes.
- SQLite virtual table API: `sqlite3_declare_vtab()` is used by `sqlite3Fts5ConfigDeclareVtab()` to declare visible columns plus hidden table-name and rank columns.
- FTS5 index module: expression evaluation opens and advances index iterators with `sqlite3Fts5IndexQuery()`, `sqlite3Fts5IterNext()`, `sqlite3Fts5IterNextFrom()`, `sqlite3Fts5IterClose()`, and optionally `sqlite3Fts5IterToken()`.
- FTS5 storage module: declared prototypes connect config and expression behavior to `%_content`, `%_docsize`, `%_config`, rebuild, optimize, merge, reset, and integrity operations implemented later in the amalgamation.
- FTS5 tokenizer module: config parsing stores tokenizer arguments, while `sqlite3Fts5Tokenize()` loads the tokenizer lazily and dispatches through either legacy `fts5_tokenizer` or `fts5_tokenizer_v2` with locale.
- FTS5 hash/index/write path: constants and prototypes define how document tokens are written, hashed, scanned, and queried, though implementations mostly appear outside this chunk.
- Generated Lemon parser mechanics: the hand-written expression code depends on `sqlite3Fts5ParserAlloc()`, `sqlite3Fts5Parser()`, and `sqlite3Fts5ParserFree()` from the generated parser in this same range.
- Optional build flags: `SQLITE_ENABLE_FTS5`, `SQLITE_CORE`, `NDEBUG`, `SQLITE_DEBUG`, `SQLITE_COVERAGE_TEST`, `SQLITE_MUTATION_TEST`, `SQLITE_OMIT_AUXILIARY_SAFETY_CHECKS`, and `SQLITE_FTS5_MAX_EXPR_DEPTH` affect declarations, assertions, parser tracing, and safety macros.

For WiredTiger, the practical integration point is build/test linkage against this vendored amalgamation. Local changes here would be high risk because they can silently change SQLite's FTS5 query semantics or extension ABI.

## Risks and Edge Cases

- The chunk crosses source-file boundaries. The first few lines belong to `sqlite3session.c`; the rest begins `fts5.c`. Research and future edits must not assume one coherent subsystem across the entire slice.
- The assigned range ends at the start of `fts5ExprAssignXNext()`, so parse-node finalization and later expression APIs are incomplete here and continue in the next chunk.
- FTS5 ABI structures are public. Reordering or changing `Fts5ExtensionApi`, `fts5_tokenizer_v2`, `fts5_tokenizer`, or `fts5_api` fields would break extensions.
- The tokenizer contract is subtle. `FTS5_TOKEN_COLOCATED` must not be returned for the first token and drives synonym handling differently for query and document tokenization. Prefix and tokendata behavior depend on exact `nQueryTerm` versus `nFullTerm` handling.
- In `fts5ParseTokenize()`, tokendata mode computes `nQueryTerm` with `strlen()` after setting `pTerm`/`pSyn` text. This intentionally treats embedded zero bytes as a query-term boundary, while `nFullTerm` retains full tokenizer output.
- `sqlite3Fts5ExprNew()` must clean up parser output correctly across parse errors, OOM, and implicit colset allocation. Leaking `apPhrase`, double-freeing phrase ownership, or keeping `sParse.pExpr` after error would be serious.
- Column filters are disallowed for `detail=none`. `sqlite3Fts5ParseSetColset()` converts such attempts into parse errors; changing this would alter documented query behavior.
- `fts5ParseSetColset()` intersects nested colsets. If the intersection becomes empty, it rewrites the node to `FTS5_EOF` and clears `xNext`, which affects later iterator initialization.
- The config parser accepts abbreviations through prefix comparisons in option and enum parsing. Ambiguous or partial option names can be accepted or rejected based on matching behavior; this is observable SQL syntax.
- `contentless_delete=1` is accepted only for contentless tables and rejected with `columnsize=0`. `contentless_unindexed=1` also requires contentless mode. These cross-option validations are user-visible.
- `fts5ConfigSkipLiteral()` validates only a constrained subset of SQL literal syntax for config/rank parsing. Accepted values here determine what can be stored in rank arguments and tokenizer directives.
- `sqlite3Fts5ConfigLoad()` rejects unknown file format versions unless they match current or secure-delete format versions. This protects against reading newer FTS5 data with older code.
- Position-list decoding deliberately stops on some corrupt encodings instead of reading past bounds. Assertion-only `assert_nc()` conditions distinguish trusted invariants from corruption-sensitive invariants.
- Simple TERM nodes alias position-list data owned by the index iterator in `detail=full`, while more complex expressions synthesize buffers. Lifetime changes around iterator advancement can invalidate those aliases.
- `detail!=full` paths do not have full position information. `fts5ExprNearTest()` reduces matching to presence checks, and auxiliary APIs are documented as slower or less informative for such tables.
- `highlight()` and `snippet()` rely on tokenizer byte offsets to splice original column text. Tokenizers that return inconsistent offsets can produce malformed output.
- `snippet()` scoring allocates an `aSeen` array sized by phrase count and a sentence-start array that grows by doubling. OOM must propagate through SQLite result errors.
- `bm25()` asserts row count is positive after `xRowCount()` succeeds and caches IDF values in auxdata. Edge behavior for empty tables is normally avoided because the function runs only for matched rows.
- `fts5ExprNodeNext_STRING()` has special synonym advancement logic for `iFrom` seeks and descending order. Comparator mistakes can skip rows or loop indefinitely.
- The generated Lemon parser uses a fixed stack depth of 100 unless configured otherwise, while `SQLITE_FTS5_MAX_EXPR_DEPTH` guards expression tree depth later. Parser stack overflow and deep expression handling are distinct concerns.

## Test Signals

Useful test signals visible in this chunk include:

- Public API error paths: `sqlite3rebaser_create()` returning `SQLITE_NOMEM`, `sqlite3session_config()` returning `SQLITE_MISUSE`, rebase iterator start/finalize behavior, and streaming versus non-streaming rebase equivalence.
- FTS5 extension ABI tests: registering custom auxiliary functions/tokenizers, v1/v2 tokenizer lookup compatibility, locale propagation, synonym handling with `FTS5_TOKEN_COLOCATED`, prefix query behavior, and tokendata token boundaries.
- Built-in auxiliary tests: `highlight()` argument count, out-of-range column behavior, overlapping phrase coalescing, locale-aware retokenization, `snippet()` ellipsis/window selection, sentence-start bonus scoring, `bm25()` weighting and auxdata caching, and `fts5_get_locale()` argument validation.
- Config parser tests: duplicate `tokenize=`, `content=`, and `content_rowid=` directives; malformed boolean options; invalid/too-many prefix indexes; reserved column/table names (`rank`, `rowid`); invalid `detail=` values; contentless option incompatibilities; default `%_content` versus `%_docsize` selection; and SQL declaration of hidden columns.
- `%_config` loading tests: defaults for missing keys, valid ranges for `pgsz`, `hashsize`, `automerge`, `usermerge`, `crisismerge`, `deletemerge`, `secure-delete`, and `insttoken`; invalid rank specs; invalid file-format version error text.
- MATCH parser tests: unterminated quoted strings, bareword syntax errors, implicit AND, explicit AND/OR/NOT, `NEAR()` spelling and distance parsing, prefix `*`, caret first-token constraints, column filters, inverse colsets, empty quoted phrases, phrase concatenation with `+`, and `detail=none` column-query rejection.
- Expression iterator tests: ascending and descending rowid order, `iFirst`/`iLast` boundaries, TERM fast path, multi-term phrase adjacency, synonym merging, NEAR trimming, AND/OR/NOT row alignment, `bNomatch` propagation, EOF propagation, and prefix-index selection flags.
- Debug/test instrumentation: `assert()`, `assert_nc()`, `ALWAYS()`/`NEVER()`, parser trace hooks under non-`NDEBUG`, and generated-parser coverage tables provide signals for internal invariant and coverage testing.

### subset-b-009044: lines 242625-251111

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 242625-251111

## Scope

This chunk covers a large slice of SQLite FTS5 internals inside the amalgamated `sqlite3.c` vendored under WiredTiger test third-party sources. It starts near the end of the FTS5 expression parser/evaluator support code, then covers the in-memory FTS5 hash accumulator and the opening/middle of the low-level FTS5 index backend. It ends just after `sqlite3Fts5IndexOpen()` begins `sqlite3Fts5IndexClose()` cleanup.

The main subsystems in this range are:

- FTS5 expression-tree construction helpers, debug/test expression-printing UDFs, phrase/position-list introspection, and position-list population for `detail=column` and `detail=none` tables.
- The in-memory `Fts5Hash` table that accumulates term-to-doclist updates before flushing them into level-0 index segments.
- The FTS5 `%_data` and `%_idx` storage format definitions, rowid packing macros, structure-record decode/write logic, segment metadata, page writers, doclist-index writers, tombstone arrays, segment iterators, and multi-segment merge iterators.
- Index read paths that seek segments by term, scan hash or disk segments, merge duplicate rowids, filter by column sets, skip tombstones/deleted entries, and expose current rowid/position-list outputs.
- Index write paths that flush hash contents to new segments, write leaf pages and `%_idx` btree separators, maintain doclist-index records, split large position lists across pages, and perform automerge/crisismerge/optimize work.
- Secure-delete and contentless-delete support, including tombstone-aware merge selection and physical removal of term/rowid entries from existing segment pages.
- Prefix-query setup and tokendata mapping for `xInstToken()` support.
- Public-ish FTS5 index lifecycle entry points for begin-write, sync, rollback, reinit, open, optimize, and merge operations.

Within WiredTiger this is third-party SQLite code used by tests or embedded tooling, not WiredTiger storage engine implementation. Its behavior still matters because any test binary using this amalgamation inherits SQLite FTS5 indexing, merge, and query semantics exactly.

## Purpose

The purpose of this chunk is to bridge FTS5 query expressions and tokenized document updates to the persistent full-text index stored in SQLite shadow tables. The expression support maps parsed MATCH terms and phrases to rowid/position-list state. The hash layer batches index updates in memory. The index layer serializes those updates into SQLite `%_data` segment pages, maintains `%_idx` accelerators, reads and merges segment iterators for queries, and incrementally compacts segments over time.

The code is performance-critical and corruption-facing. It manipulates compact varint encodings, page headers, prefix-compressed terms, delta-encoded rowids, position-list payloads, and reference-counted in-memory structures. It also supports multiple FTS5 detail modes (`full`, `columns`, `none`), prefix indexes, tokendata mode, secure-delete mode, contentless-delete tombstones, reverse rowid scans, and column-restricted queries.

## Important APIs, Types, and Functions

### Expression Helpers

The chunk begins after `fts5ExprAssignXNext()` has selected per-node iterator callbacks. `fts5ExprAddChildren()` flattens adjacent `AND` or `OR` nodes so expression trees avoid unnecessary nesting, while preserving `NOT` binary shape. `fts5ParsePhraseToAnd()` rewrites trigram LIKE/GLOB phrases into an `AND` tree when `bPhraseToAnd` is set, turning a phrase such as `abc + def + ghi` into independent term nodes.

`sqlite3Fts5ParseNode()` is the main expression node allocator for `FTS5_STRING`, `FTS5_AND`, `FTS5_OR`, and `FTS5_NOT`. It handles null child elision, phrase-to-AND rewrites, term-node simplification, `detail!=full` query restrictions, phrase/node back-pointers, EOF marking for empty phrases, and maximum expression-depth enforcement. `sqlite3Fts5ParseImplicitAnd()` combines adjacent terms during parsing and includes special handling for EOF placeholder nodes so empty-string terms do not leave invalid phrase-array entries behind.

Under `SQLITE_TEST` or `SQLITE_FTS5_DEBUG`, `fts5ExprTermPrint()`, `fts5ExprPrintTcl()`, `fts5ExprPrint()`, and `fts5ExprFunction()` implement debug scalar functions `fts5_expr()`, `fts5_expr_tcl()`, `fts5_isalnum()`, and `fts5_fold()`. These parse expressions using a synthetic FTS5 config and render them in human-readable or Tcl-readable form. `sqlite3Fts5ExprInit()` registers those debug-only UDFs and references parser trace/fallback symbols to avoid unused warnings.

Expression accessors include `sqlite3Fts5ExprPhraseCount()`, `sqlite3Fts5ExprPhraseSize()`, `sqlite3Fts5ExprPoslist()`, `sqlite3Fts5ExprPhraseCollist()`, `sqlite3Fts5ExprQueryToken()`, `sqlite3Fts5ExprInstToken()`, and `sqlite3Fts5ExprClearTokens()`. They expose phrase counts, phrase terms, current position/collist data, query-token bytes, original instance-token bytes for tokendata/prefix cases, and per-term token-data caches.

For `detail=columns` and `detail=none`, the expression layer may rebuild position lists by retokenizing row text. `sqlite3Fts5ExprClearPoslists()` allocates `Fts5PoslistPopulator` state and clears or marks phrase misses. `sqlite3Fts5ExprPopulatePoslists()` configures per-phrase column eligibility and calls `sqlite3Fts5Tokenize()` with `fts5ExprPopulatePoslistsCb()`, which matches document tokens against expression terms/synonyms/prefixes, appends encoded offsets, and optionally records tokendata back into index iterators. `sqlite3Fts5ExprCheckPoslists()` then recursively validates `AND`, `OR`, and `NOT` nodes against populated lists.

### In-Memory FTS5 Hash

`Fts5Hash` and `Fts5HashEntry` implement the pending update table. A hash entry stores the key and current doclist in one allocation: the key is a one-byte index identifier followed by term bytes, and the data area contains delta-encoded rowids and position-list encodings similar to on-disk doclists.

Key functions:

- `sqlite3Fts5HashNew()`, `sqlite3Fts5HashFree()`, and `sqlite3Fts5HashClear()` allocate, free, and empty the hash. The object updates the caller's byte counter through `pnByte`.
- `fts5HashKey()`, `fts5HashKey2()`, and `fts5HashResize()` hash term keys and double slot count when the load factor approaches 0.5.
- `sqlite3Fts5HashWrite()` appends a token occurrence or delete marker. It creates or grows `Fts5HashEntry` allocations, starts new rowid records, handles `detail=full`, `detail=columns`, and `detail=none` encodings, tracks column/position ordering, and updates delete/content flags.
- `fts5HashAddPoslistSize()` finalizes the pending position-list size field. This may rewrite a reserved one-byte field into a multi-byte varint and shifts following bytes.
- `fts5HashEntryMerge()` and `fts5HashEntrySort()` produce sorted scan lists for flushes and prefix scans without removing entries from hash buckets.
- `sqlite3Fts5HashQuery()`, `sqlite3Fts5HashScanInit()`, `sqlite3Fts5HashScanNext()`, `sqlite3Fts5HashScanEof()`, and `sqlite3Fts5HashScanEntry()` expose point lookups or ordered scans of pending doclists to the segment iterator layer.

A notable state transition is that hash scans finalize position-list size fields, after which those entries are no longer safely appendable. `fts5SegIterHashInit()` clears `Fts5Index.bDelete` after scan initialization to avoid appending to finalized delete-related data.

### FTS5 Index Storage Structures

The index backend defines the `%_data` table record classes and rowid layout. `FTS5_AVERAGES_ROWID` and `FTS5_STRUCTURE_ROWID` identify global records. `FTS5_SEGMENT_ROWID()`, `FTS5_DLIDX_ROWID()`, and `FTS5_TOMBSTONE_ROWID()` pack segment id, doclist-index bit, height, and page number into shadow-table rowids using `fts5_dri()`.

Core types introduced here include:

- `Fts5Data`: an owned `%_data` blob plus `nn` and `szLeaf`.
- `Fts5Index`: the backend handle, holding config, prepared statements, pending hash, reader blob, cached structure, flush/error state, data-version, and counters.
- `Fts5Structure`, `Fts5StructureLevel`, and `Fts5StructureSegment`: in-memory decoded structure records. V2 structures add contentless-delete origin counters, tombstone page counts, tombstone entry counts, and segment entry counts.
- `Fts5PageWriter`, `Fts5DlidxWriter`, and `Fts5SegWriter`: segment output builders for leaf pages, doclist-index pages, separator terms, and `%_idx` rows.
- `Fts5SegIter`, `Fts5DlidxIter`, and `Fts5Iter`: single-segment, doclist-index, and multi-segment iterators.
- `Fts5TombstoneArray`: lazily loaded, reference-counted tombstone hash pages for contentless-delete filtering.
- `Fts5DoclistIter`, `PrefixMerger`, `Fts5TokenDataMap`, and `Fts5TokenDataIter`: helper structures for prefix-query doclist construction and tokendata instance-token lookup.

Endian helpers (`fts5PutU16()`, `fts5GetU16()`, `fts5GetU32()`, `fts5GetU64()`, `fts5PutU32()`, `fts5PutU64()`), buffer append macros, leaf header macros, and constants such as `FTS5_DATA_PADDING`, `FTS5_DATA_ZERO_PADDING`, `FTS5_WORK_UNIT`, `FTS5_OPT_WORK_UNIT`, and `FTS5_MIN_DLIDX_SIZE` define the low-level binary contract.

### Data IO and Structure Records

`fts5DataRead()` uses a reusable read-only `sqlite3_blob` handle to read records from `%_data`. It reopens the blob for a requested rowid, maps `SQLITE_ERROR` to `FTS5_CORRUPT`, allocates padded `Fts5Data`, reads the blob, and initializes `szLeaf`. `fts5LeafRead()` adds leaf sanity checks. `fts5DataWrite()`, `fts5DataDelete()`, and `fts5DataRemoveSegment()` write/replace data rows, delete rowid ranges, remove segment/tombstone records, and clean corresponding `%_idx` rows.

`fts5IndexPrepareStmt()` prepares persistent statements with `SQLITE_PREPARE_NO_VTAB` and maps missing/modified shadow tables to corruption. `fts5IndexCloseReader()` closes the blob reader and records close errors in `Fts5Index.rc`.

`fts5StructureDecode()` parses the structure record, including legacy and `FTS5_STRUCTURE_V2` formats. It validates level/segment counts, merge counts, segment page ranges, V2 tombstone/origin metadata, and total segment count. `fts5StructureWrite()` serializes the structure with the current configuration cookie and V2 extension fields when needed. `fts5StructureRead()`, `fts5StructureReadUncached()`, `fts5IndexDataVersion()`, and `fts5StructureInvalidate()` implement a cached structure object keyed by SQLite `PRAGMA data_version`.

Reference and copy-on-write helpers (`fts5StructureRef()`, `fts5StructureRelease()`, `sqlite3Fts5StructureRef()`, `sqlite3Fts5StructureRelease()`, `sqlite3Fts5StructureTest()`, and `fts5StructureMakeWritable()`) allow callers to hold structure snapshots safely while merge/write logic edits writable copies.

Structure editing and merge policy helpers include `fts5StructureAddLevel()`, `fts5StructureExtendLevel()`, `fts5StructurePromoteTo()`, `fts5StructurePromote()`, `fts5AllocateSegid()`, `fts5IndexDiscardData()`, `fts5IndexFindDeleteMerge()`, `fts5IndexMerge()`, `fts5IndexAutomerge()`, `fts5IndexCrisismerge()`, `fts5IndexOptimizeStruct()`, `sqlite3Fts5IndexOptimize()`, and `sqlite3Fts5IndexMerge()`.

### Segment and Doclist Iterators

Doclist-index iteration is handled by `fts5DlidxLvlNext()`, `fts5DlidxIterNextR()`, `fts5DlidxIterNext()`, `fts5DlidxIterFirst()`, `fts5DlidxIterEof()`, `fts5DlidxIterLast()`, `fts5DlidxLvlPrev()`, `fts5DlidxIterPrevR()`, `fts5DlidxIterPrev()`, `fts5DlidxIterFree()`, `fts5DlidxIterInit()`, `fts5DlidxIterRowid()`, and `fts5DlidxIterPgno()`. These traverse one or more levels of doclist-index pages and are used to skip directly to pages likely to contain a target rowid.

Single-segment iteration is initialized by `fts5SegIterInit()` for full scans, `fts5SegIterSeekInit()` for term lookups, `fts5SegIterNextInit()` for finding the next term after a token, and `fts5SegIterHashInit()` for pending in-memory hash data. `fts5SegIterSetNext()` chooses between forward, reverse, and `detail=none` next callbacks.

Important iterator helpers include:

- `fts5SegIterNextPage()`, `fts5SegIterLoadTerm()`, `fts5SegIterLoadRowid()`, `fts5SegIterLoadNPos()`, and `fts5GetPoslistSize()` decode leaf pages, terms, rowids, delete flags, and position-list sizes.
- `fts5LeafSeek()` finds a term on a leaf using prefix-compressed terms and page indexes.
- `fts5SegIterLoadDlidx()`, `fts5SegIterReverse()`, `fts5SegIterReverseInitPage()`, and `fts5SegIterReverseNewPage()` support descending rowid scans of a single term.
- `fts5SegIterNext()`, `fts5SegIterNext_None()`, and `fts5SegIterNext_Reverse()` advance iterators through regular, `detail=none`, and reverse encodings.
- `fts5SegIterNextFrom()` uses doclist-index pages to advance an oneterm iterator to or past a target rowid.
- `fts5SegIterClear()` frees term buffers, leaf buffers, next-leaf prefetch, tombstone arrays, doclist iterators, and reverse offset arrays.

Multi-segment iteration uses a tournament tree in `Fts5Iter.aFirst`. `fts5MultiIterAlloc()` sizes the iterator to a power-of-two segment count. `fts5MultiIterDoCompare()`, `fts5MultiIterAdvanced()`, `fts5MultiIterAdvanceRowid()`, `fts5MultiIterSetEof()`, and `fts5MultiIterFinishSetup()` maintain the winner tree, detect duplicate term/rowid entries from lower-priority segments, and choose the visible current entry. `fts5MultiIterNext()`, `fts5MultiIterNext2()`, `fts5MultiIterNextFrom()`, `fts5MultiIterEof()`, `fts5MultiIterRowid()`, and `fts5MultiIterTerm()` expose traversal operations.

Delete/tombstone filtering is split by mode. Ordinary delete markers are zero-length or flagged position lists, detected by `fts5MultiIterIsEmpty()`. Contentless-delete tombstones are checked by `fts5MultiIterIsDeleted()` using `Fts5TombstoneArray` and `fts5IndexTombstoneQuery()`.

### Position-List Outputs and Column Filtering

`fts5ChunkIterate()` streams a position list to a callback, following overflow onto subsequent segment pages when required. `fts5SegiterPoslist()` copies or filters position-list data into an output buffer. `fts5PoslistCallback()`, `fts5PoslistFilterCallback()`, and `fts5PoslistOffsetsCallback()` implement raw copy, `detail=full` column filtering, and `detail=columns` offset filtering.

`fts5IndexExtractColset()` can avoid copying when a single-column filter corresponds to a contiguous subset of a full position list. Output callbacks selected by `fts5IterSetOutputCb()` populate `Fts5IndexIter.base` fields for different configurations:

- `fts5IterSetOutputs_None()` for `detail=none`.
- `fts5IterSetOutputs_Nocolset()` for full/columns detail with no filter.
- `fts5IterSetOutputs_ZeroColset()` for an empty column set.
- `fts5IterSetOutputs_Col()` and `fts5IterSetOutputs_Col100()` for `detail=columns`.
- `fts5IterSetOutputs_Full()` for `detail=full` with column restrictions.

### Segment Writing, Flush, and Merge

Segment output starts with `fts5WriteInit()`, which prepares the `%_idx` writer, initializes a leaf page buffer with a four-byte header, allocates page/pgidx buffers, and ensures doclist-index writer storage. `fts5WriteAppendTerm()` writes prefix-compressed terms and page-index entries, and records split keys through `fts5WriteBtreeTerm()` when a new leaf starts. `fts5WriteAppendRowid()` writes first or delta rowids and updates the doclist-index via `fts5WriteDlidxAppend()`. `fts5WriteAppendPoslistData()` streams large position lists across page boundaries without splitting varints.

`fts5WriteFlushLeaf()` finalizes `szLeaf`, appends pgidx data if the page contains terms, writes the leaf row to `%_data`, resets page buffers, and increments leaf counters. `fts5WriteBtreeNoTerm()`, `fts5WriteFlushDlidx()`, `fts5WriteDlidxClear()`, `fts5WriteDlidxGrow()`, `fts5DlidxExtractFirstRowid()`, and `fts5WriteFlushBtree()` maintain optional doclist-index pages and `%_idx` entries for large doclists. `fts5WriteFinish()` flushes final pages, writes btree separators, frees writer buffers, and reports leaf count.

`fts5TrimSegments()` updates input segments after partial incremental merges. `fts5MergeChunkCallback()` copies position-list chunks into a segment writer during merge. `fts5IndexMergeLevel()` merges input segments from a level into a higher-level segment, writes non-deleted doclists, removes fully merged old segments, trims partially consumed segments, updates structure metadata, and decrements remaining work-page budget. `fts5IndexMerge()` chooses ongoing merge levels, levels with too many segments, or contentless-delete tombstone-heavy levels.

`fts5FlushOneHash()` is the central pending-data flush path. It reads and invalidates the current structure, allocates a segment id, scans sorted hash entries, writes each term/doclist into a new level-0 segment, performs secure-delete physical removal when configured, appends the new segment to level 0, promotes segments when appropriate, runs automerge and crisismerge, writes the updated structure, and releases it. `fts5IndexFlush()` calls this when pending data or contentless-delete work exists and preserves `flushRc` if a failed flush must be retried/reported.

### Secure Delete and Contentless Delete

Secure-delete code physically removes token traces instead of just appending delete markers. `fts5SecureDeleteIdxEntry()` deletes `%_idx` separator entries for pages whose last term was removed. `fts5SecureDeleteOverflow()` rewrites pages that held overflow portions of a deleted position list, shifting leaf bodies and pgidx data. `fts5DoSecureDelete()` removes the current rowid/position-list entry from a segment page, adjusts following rowid deltas, removes entire terms when their last rowid disappears, updates page headers and footers, and handles cases where the doclist spans multiple pages. `fts5FlushSecureDelete()` ensures the FTS5 version is upgraded to secure-delete format, seeks the target term/rowid in existing segments with hash skipped, and calls `fts5DoSecureDelete()`.

Contentless-delete state is stored in V2 structure records through segment origins, tombstone page counts, tombstone entry counts, and entry counts. `fts5IndexFindDeleteMerge()` selects merge candidates when tombstones exceed the configured delete-merge percentage. Query iterators lazily load tombstone pages and suppress tombstoned rowids.

### Prefix Query and Tokendata Setup

`fts5VisitEntries()` scans all index entries matching a full token or prefix and invokes a callback for each visible rowid entry. It uses a no-output multi-iterator initially, then selects output callbacks and filters by column set.

Prefix query setup accumulates a synthetic doclist from all terms with the requested prefix. `fts5DoclistIterNext()`, `fts5DoclistIterInit()`, `fts5MergeRowidLists()`, `fts5MergePrefixLists()`, `fts5PrefixMergerInsertByRowid()`, `fts5PrefixMergerInsertByPosition()`, `fts5AppendRowid()`, `fts5AppendPoslist()`, and `prefixIterSetupCb()` merge rowid-only or full position-list doclists while preserving rowid order and merged positions. `fts5SetupPrefixIter()` chooses the merge strategy based on detail mode, optionally combines main-index and prefix-index data, builds an in-memory `Fts5Data` doclist, and returns an `Fts5Iter` over it.

Tokendata support adds `Fts5TokenDataMap` and `Fts5TokenDataIter`. `prefixIterSetupTokendataCb()` records rowid/position-to-term mappings for prefix queries. `fts5TokendataIterAppendMap()`, `fts5TokendataMerge()`, `fts5TokendataIterSortMap()`, and `fts5TokendataIterDelete()` allocate, sort, and free these mappings. These structures support APIs that need to recover the original matched token for an instance.

### Lifecycle Entry Points

The chunk ends with higher-level index lifecycle functions:

- `sqlite3Fts5IndexBeginWrite()` allocates the hash table on demand, flushes if rowid ordering or hash-size limits require it, sets write rowid/delete mode, and increments pending-row counts for inserts.
- `sqlite3Fts5IndexSync()` flushes pending data and closes the blob reader.
- `sqlite3Fts5IndexRollback()` closes readers, discards pending hash data, invalidates cached structures, and returns the backend to a clean state.
- `sqlite3Fts5IndexReinit()` initializes empty `%_data` storage with averages and structure records, including initial contentless-delete origin state.
- `sqlite3Fts5IndexOpen()` allocates `Fts5Index`, creates `%_data` and `%_idx` shadow tables when requested, and reinitializes them.
- `sqlite3Fts5IndexClose()` begins at the end of the chunk and starts finalizing prepared statements after invalidating cached structure state.

## Control Flow and State Behavior

The normal write path starts when table-level FTS5 code calls `sqlite3Fts5IndexBeginWrite()` for a rowid. Token writes are accumulated in `Fts5Hash` through `sqlite3Fts5HashWrite()` elsewhere in the amalgamation. The hash preserves rowid order assumptions and tracks memory through `nPendingData`. When rowid order changes, a delete/insert conflict occurs, or the hash exceeds `nHashSize`, `fts5IndexFlush()` writes pending entries to disk.

Flush control flow is:

1. Read and invalidate the cached structure.
2. If hash is non-empty, allocate a free segment id.
3. Initialize `Fts5SegWriter` and scan hash entries in term order.
4. For each term, either append its doclist directly if it fits or iterate rowid/poslist records and split them across leaves.
5. In secure-delete mode, delete markers may trigger in-place edits of existing segments instead of writing new delete entries.
6. Finish the writer, append a level-0 segment if pages were produced, update V2 origin/entry metadata when needed, promote small segments, run automerge/crisismerge, write the structure, and clear hash state.

The query path builds one or more `Fts5SegIter` objects from the pending hash and from every relevant disk segment in the current structure. Each segment iterator decodes its current term, rowid, delete flag, and position list. `Fts5Iter` merges them using `aFirst[]`, with lower array indexes representing higher-priority/newer sources. Duplicate term/rowid entries from older segments are advanced or skipped. Empty delete entries and contentless-delete tombstones are filtered before output callbacks expose rowid and position-list data.

Persistent state lives mainly in SQLite shadow tables:

- `%_data` stores the averages record, structure record, segment leaf pages, doclist-index pages, and tombstone hash pages.
- `%_idx` stores per-segment term-to-page separators and flags indicating whether a doclist-index exists.
- `%_config` may be updated by secure-delete upgrade code to set the FTS5 version.

In-memory state includes:

- Pending term/doclist data in `Fts5Hash`.
- Cached `Fts5Structure` snapshots with reference counts and `data_version`.
- Reusable prepared statements for `%_data`, `%_idx`, and config access.
- A reusable blob reader, invalidated on rollback/sync/close.
- Segment iterator buffers, next-leaf prefetch, doclist-index iterators, reverse rowid offset arrays, and tombstone arrays.
- Writer buffers for leaf page body, page index, previous term, doclist-index levels, and pending `%_idx` term.

Error propagation is centralized through `Fts5Index.rc`. Most helpers are no-ops when `rc` is already non-OK. Corruption-facing decoders set `FTS5_CORRUPT` or `SQLITE_CORRUPT_VTAB`; allocation failures set `SQLITE_NOMEM`; public entry points usually return through `fts5IndexReturn()`, which resets `p->rc` to `SQLITE_OK` after reporting it.

## Dependencies and Integration Points

This code depends on SQLite internals defined earlier or later in the amalgamation:

- FTS5 parser/config/expression types such as `Fts5Parse`, `Fts5Expr`, `Fts5ExprNode`, `Fts5ExprNearset`, `Fts5ExprPhrase`, `Fts5ExprTerm`, `Fts5Colset`, `Fts5Config`, `Fts5Global`, and `Fts5Buffer`.
- SQLite core allocation, varint, buffer, and string helpers including `sqlite3_malloc64()`, `sqlite3_realloc64()`, `sqlite3_free()`, `sqlite3Fts5MallocZero()`, `sqlite3Fts5BufferSize()`, `fts5BufferAppendVarint()`, `fts5BufferAppendBlob()`, `sqlite3Fts5PutVarint()`, `sqlite3Fts5GetVarint()`, `fts5GetVarint32()`, and `fts5FastGetVarint32()`.
- SQLite SQL APIs for shadow-table IO: `sqlite3_prepare_v3()`, `sqlite3_bind_*()`, `sqlite3_step()`, `sqlite3_reset()`, `sqlite3_finalize()`, `sqlite3_blob_open()`, `sqlite3_blob_reopen()`, `sqlite3_blob_read()`, and `sqlite3_blob_close()`.
- FTS5 tokenizer and Unicode helpers used by expression debug and poslist population: `sqlite3Fts5Tokenize()`, `sqlite3Fts5UnicodeCatParse()`, `sqlite3Fts5UnicodeCategory()`, and `sqlite3Fts5UnicodeFold()`.
- FTS5 index APIs outside this chunk, such as token writes, query entry points, iterator close/free wrappers, averages handling, tombstone creation, and table-level virtual table methods.

Integration points inside SQLite include MATCH expression parsing, FTS5 virtual table updates, query execution, phrase APIs, `xQueryToken()`/`xInstToken()`, optimize/merge special commands, rollback/sync hooks, and shadow-table creation. For the repository, the integration is indirect: WiredTiger tests that embed this SQLite amalgamation may exercise FTS5 behavior, but this code should generally be treated as vendored SQLite source.

## Risks

- The binary formats are compact and hand-decoded. Off-by-one errors in `szLeaf`, pgidx offsets, rowid offsets, position-list sizes, or varint boundaries can cause corruption reports, bad query results, or unsafe memory reads.
- Hash entries are append-oriented until scans finalize position-list size fields. Appending after `fts5HashAddPoslistSize()` has rewritten an entry would corrupt pending doclists, so the `bDelete`/scan interaction is fragile.
- Detail modes use different encodings. `detail=none` uses special zero-byte delete/content markers, `detail=columns` stores column lists, and `detail=full` stores full positions. Code paths that assume the wrong mode will misread doclists.
- Rowid ordering is assumed in many write paths. `sqlite3Fts5IndexBeginWrite()` must flush when rowids move backward or delete/insert ordering would make a hash entry unappendable.
- Segment merge priority determines visible results. Bugs in `fts5MultiIterDoCompare()`, duplicate advancement, tombstone filtering, or empty-delete skipping can resurrect deleted rows or hide live rows.
- Secure-delete physically rewrites pages and `%_idx` rows. It must update rowid deltas, page headers, term footers, overflow pages, and separator entries consistently; a small mistake can damage an entire segment.
- Structure-record V2 support adds compatibility risk. Origin counters, tombstone metadata, and version upgrade writes must remain synchronized with `contentless_delete` and secure-delete behavior.
- Blob-reader caching interacts with savepoints and rollback. `SQLITE_ABORT` from `sqlite3_blob_reopen()` is deliberately handled by reopening later; missing invalidation would read stale or invalid shadow-table pages.
- Prefix-query materialization can allocate large temporary doclists and tokendata maps. Incorrect merge buffering or map sorting affects prefix MATCH results and `xInstToken()` output.
- This is amalgamated third-party code. Local modifications are hard to maintain unless they come from the exact upstream SQLite version expected by the test suite.

## Test and Validation Signals

Useful test signals for this chunk include:

- FTS5 MATCH queries over inserted, deleted, and updated rows, including `AND`, `OR`, `NOT`, implicit `AND`, empty phrases, NEAR/phrase restrictions, trigram LIKE/GLOB phrase-to-AND rewrites, and column filters.
- Tables using `detail=full`, `detail=columns`, and `detail=none`, with phrase APIs and position/collist access checked where supported.
- Prefix index queries, both with and without `tokendata=1`, including `xInstToken()` expectations for prefix matches.
- Update workloads that force hash flushes because of rowid order changes, pending hash size, deletes followed by inserts for the same rowid, and explicit sync/rollback boundaries.
- Optimize and merge commands, automerge thresholds, crisismerge thresholds, and incremental merge continuation after partial work.
- Contentless-delete tables with tombstone-heavy levels and configured `deletemerge`, verifying that tombstoned rowids are hidden and later merge work compacts them.
- Secure-delete mode tests that remove all instances of a term and verify `%_data`/`%_idx` no longer retain the term, including entries spanning overflow leaf pages.
- Corruption tests for malformed `%_data` leaves, invalid structure records, bad page offsets, out-of-range segment metadata, and truncated doclists.
- Debug/test builds exercising `fts5_expr()`, `fts5_expr_tcl()`, `fts5_isalnum()`, `fts5_fold()`, `assert()` invariants, and `FTS5_CORRUPT` paths.

No tests were run for this research chunk; this document is based on static reading of `sqlite3.c` lines 242625-251111.

### subset-b-009045: lines 251112-259629

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 251112-259629

## Scope

This chunk covers the tail of the FTS5 index implementation, the main FTS5 virtual-table module, most of the FTS5 storage layer, and the start of the built-in tokenizer implementations in the SQLite amalgamation vendored under WiredTiger tests. It begins after earlier FTS5 index setup/destruction code and ends partway through `fts5UnicodeTokenize()`, so several types and helpers are defined in neighboring chunks.

## Purpose

The code implements the runtime machinery for SQLite FTS5 tables:

- Writing tokens and prefix tokens into the FTS index.
- Opening and advancing term/rowid iterators, including `tokendata=1` token mapping for `xInstToken()`.
- Maintaining contentless-delete tombstone hash tables in segment metadata.
- Running index and storage integrity checks.
- Registering FTS5 debug helpers, the `fts5` virtual table module, extension APIs, tokenizers, and scalar functions.
- Managing FTS5 virtual table queries, updates, transactions, savepoints, ranking, locale-aware text extraction, shadow storage tables, docsize/totals records, and rebuild/optimize/merge commands.
- Starting the ASCII and Unicode tokenizer implementations used by FTS5 indexing and querying.

## Important Types And State

- `Fts5Index` is the index backend handle. This chunk uses its persistent error field `p->rc`, `pHash`, `iWriteRowid`, `bDelete`, `pConfig`, `pStruct`, `nRead`, `nContentlessDelete`, and structure/version state.
- `Fts5Iter`, `Fts5IndexIter`, `Fts5SegIter`, `Fts5TokenDataIter`, and `Fts5TokenDataMap` model index scans. A normal iterator owns segment iterators; a `tokendata=1` wrapper iterator has `nSeg==0` and merges multiple child iterators through `pTokenDataIter`.
- `Fts5Structure`, `Fts5StructureLevel`, and `Fts5StructureSegment` describe on-disk FTS segment layout, including leaf page ranges, origin ranges, tombstone page counts, and tombstone entry counts.
- `Fts5Global` is per-database module state. It owns the public `fts5_api`, registered auxiliary functions, tokenizer modules, default tokenizer, open cursor list, cursor-id allocator, and the per-connection randomized locale blob header.
- `Fts5FullTable` extends the public `Fts5Table` with `Fts5Storage`, global context, sort cursor state, savepoint tracking, and debug transaction state.
- `Fts5Cursor` is the virtual table cursor. It tracks query plan, rowid bounds, content lookup statement, expression tree, optional rank sorter, cache flags, rank function/arguments, auxiliary data, and cached phrase-instance arrays.
- `Fts5Storage` owns shadow-table prepared statements, cached totals (`nTotalRow`, `aTotalSize`), saved-row statement state for updates using `sqlite3_value_nochange()`, and references to `Fts5Config` and `Fts5Index`.
- `AsciiTokenizer`, `Unicode61Tokenizer`, and `Fts5TokenizerModule` hold tokenizer configuration and bridge v1/v2 tokenizer APIs.

Persistent state is stored in FTS5 shadow tables:

- `%_data` stores segment pages, averages, structure, and tombstone pages.
- `%_idx` stores segment b-tree split keys and doclist-index markers.
- `%_config` stores configuration key/value records, including version.
- `%_docsize` stores per-row token counts and, for `contentless_delete=1`, origin values.
- `%_content` stores content for normal or unindexed-content modes.

## Index Write And Query Flow

`sqlite3Fts5IndexCharlenToBytelen()` and `fts5IndexCharlen()` count UTF-8 character boundaries for prefix indexing. `sqlite3Fts5IndexWrite()` writes the main token record through `sqlite3Fts5HashWrite()` and then writes configured prefix-index entries after translating prefix character counts to byte lengths. Delete calls are represented by negative `iCol` and must match `p->bDelete`.

`sqlite3Fts5IndexQuery()` is the primary index query entry point. It builds an encoded term with a leading index selector byte, chooses between main index, exact prefix index, prefix scan, or `tokendata=1` special handling, opens a multi-iterator, and closes index readers on error. Prefix queries may be satisfied by a configured prefix index or by scanning main-index terms, with debug-only `FTS5INDEX_QUERY_TEST_NOIDX` exercising the scan path.

For `tokendata=1`, `fts5SetupTokendataIter()` scans all terms sharing a token-data prefix and appends one iterator per matching term. `fts5IterSetOutputsTokendata()` merges child iterators by lowest rowid, optionally merges multiple position lists, and builds maps from rowid/position back to the child term iterator. `sqlite3Fts5IterToken()` then uses that map to answer `xInstToken()` lookups, either from the exact child term or from prefix-token storage built by `fts5SetupPrefixIterTokendata()` / `sqlite3Fts5IndexIterWriteTokendata()`.

Iterator APIs in this chunk include `sqlite3Fts5IterNext()`, `sqlite3Fts5IterNextScan()`, `sqlite3Fts5IterNextFrom()`, `sqlite3Fts5IterTerm()`, `sqlite3Fts5IndexIterClearTokendata()`, and `sqlite3Fts5IterClose()`. They delegate to normal multi-iterator movement or tokendata merge movement based on whether `nSeg==0`.

## Tombstones And Contentless Deletes

`sqlite3Fts5IndexContentlessDelete()` loads the structure and finds all segments whose origin range contains the deleted row origin. The first matching segment increments `nEntryTombstone`; all matching segments receive the rowid in their tombstone hash via `fts5IndexTombstoneAdd()`.

Tombstones are persisted as hash-table pages in `%_data` using `FTS5_TOMBSTONE_ROWID(segid,page)`. `fts5IndexTombstoneAddToPage()` handles 4-byte or 8-byte keys, a special rowid-zero flag, open-addressed insertion, and half-full refusal unless forced. `fts5IndexTombstoneRebuild()` and `fts5IndexTombstoneRehash()` grow or rebuild the table when a page is full or the key width must expand from 4 to 8 bytes. Successful rebuild writes all pages and updates `pSeg->nPgTombstone` plus the structure record.

Risks here are data-structure correctness and corruption detection: bad page sizing, key-width mismatches, origin-range errors, or missed structure writes could leave deletes invisible to queries. The code mitigates with rebuild retries, explicit `FTS5_CORRUPT` paths elsewhere, and decode/debug tooling.

## Integrity And Debug Tooling

The integrity-check section computes checksums with `sqlite3Fts5IndexEntryCksum()`. Debug-only helpers compare forward and reverse doclist-index traversal (`fts5TestDlidxReverse()`), query terms in ascending and descending order (`fts5QueryCksum()`), validate UTF-8 prefixes (`fts5TestUtf8()`), and compare prefix-index results against main-index scans (`fts5TestTerm()`).

`fts5IndexIntegrityCheckSegment()` verifies `%_idx` entries against segment leaves, checks split-key ordering, page indexes, empty pages, doclist-index pointers, and secure-delete edge cases. `sqlite3Fts5IndexIntegrityCheck()` walks all segments, scans all terms to build a checksum, and compares it with a checksum derived from content when requested.

Under `SQLITE_TEST` or `SQLITE_FTS5_DEBUG`, this chunk registers:

- `fts5_decode(rowid, blob)` and `fts5_decode_none()` for human-readable decoding of structure, averages, segment leaves, doclist indexes, tombstone pages, and rowid lists.
- `fts5_rowid('segment', segid, pgno)` for deriving segment rowids.
- `fts5_structure(struct)` as a table-valued view over decoded `Fts5Structure` records.

These are important test signals for corruption triage because they expose the exact encoded storage records that normal queries consume.

## Virtual Table Module And Query Planning

`fts5InitVtab()` implements both `xCreate` and `xConnect`: parse configuration, load tokenizer if needed, open index and storage subsystems, declare the virtual-table schema, load configuration, and enable constraint support/innocuous mode. `fts5FreeVtab()`, `fts5DisconnectMethod()`, and `fts5DestroyMethod()` close index, storage, config, and shadow tables.

`fts5BestIndexMethod()` builds an `idxStr` program and `idxNum` flags for `xFilter()`. It recognizes table-column MATCH, rank MATCH, column-specific MATCH, LIKE/GLOB pattern support when the tokenizer advertises it, rowid equality/ranges, and `ORDER BY rank` or `ORDER BY rowid`. It rejects unusable MATCH constraints, suppresses duplicate rank/equality constraints, marks rowid equality scans unique, blocks recursively defined content tables through `pConfig->bLock`, and estimates costs based on match and rowid constraint combinations.

`fts5FilterMethod()` decodes `idxStr`, extracts locale-wrapped expressions with `fts5ExtractExprText()`, handles `fts5_insttoken()` subtype requests, builds combined FTS expressions, handles pattern expressions, sets rowid bounds according to sort order, loads index configuration, and selects one of:

- `FTS5_PLAN_MATCH` for normal MATCH.
- `FTS5_PLAN_SORTED_MATCH` plus an internal `FTS5_PLAN_SOURCE` cursor for `ORDER BY rank`.
- `FTS5_PLAN_SPECIAL` for internal `MATCH '*reads'` and `MATCH '*id'`.
- `FTS5_PLAN_ROWID` or `FTS5_PLAN_SCAN` using storage statements.

Cursor movement uses `fts5NextMethod()`, `fts5CursorFirst()`, `fts5SorterNext()`, and `fts5CursorReseek()`. Writes call `fts5TripCursors()` to mark active MATCH cursors for reseek so readers do not continue using stale index iterator state.

## Cursor Columns, Rank, And Extension API

`fts5ColumnMethod()` returns user columns, the hidden table-name column (cursor id), or the hidden rank column. For rank sorting, `fts5PoslistBlob()` serializes phrase position lists for internal source cursors. For ordinary rank evaluation, `fts5FindRankFunction()` resolves the configured auxiliary rank function and optional parsed rank arguments.

The extension API table `sFts5Api` is version 4 in this chunk and exposes user data, column count/text/size/locale, row count, column total size, tokenization with and without locale, phrase metadata, instance enumeration, phrase iterators, query-token, instance-token, auxiliary data, and phrase subquery support. `fts5ApiCallback()` looks up a cursor id and invokes the registered auxiliary function with the current cursor context.

Position-list and instance APIs are lazy. `fts5CsrPoslist()` returns index-provided position lists for `detail=full`, or repopulates them by retokenizing row content for lower-detail modes when content is available. `fts5CacheInstArray()` merges phrase position readers into sorted `(phrase,column,offset)` triples and flags corrupt column numbers. `fts5ApiInstToken()` depends on the tokendata mapping implemented earlier in the chunk.

Locale support flows through `fts5_locale()`, `sqlite3Fts5IsLocaleValue()`, `sqlite3Fts5DecodeLocaleValue()`, `sqlite3Fts5SetLocale()`, `fts5TextFromStmt()`, and `fts5ApiColumnLocale()`. The randomized per-connection header in `Fts5Global.aLocaleHdr` identifies internal locale blobs while reducing accidental collision with user blobs.

## Updates, Transactions, And Special Commands

`fts5UpdateMethod()` handles virtual-table insert, update, delete, and special insert directives. It loads config if needed, sets error-message routing, trips open cursors, validates `fts5_locale()` usage against `locale=1`, honors conflict mode for normal/contentless-delete tables, and distinguishes:

- `DELETE` by rowid.
- `INSERT`, including `REPLACE` conflict handling.
- `UPDATE` with unchanged rowid.
- `UPDATE` with modified rowid, carefully detecting conflicts before irreversible changes.
- Special insert directives: `delete-all`, `rebuild`, `optimize`, `merge`, `integrity-check`, debug `prefix-index`, `flush`, and config key/value updates.
- Special contentless delete command for contentless external/content tables without `contentless_delete=1`.

`fts5ContentlessUpdate()` enforces contentless update rules: updating only unindexed columns can be content-only; otherwise, `contentless_delete=1` requires all indexed columns to be modified, not a subset.

Transaction callbacks are thin but important. `xSync` flushes pending index/storage state to disk, `xCommit` is a no-op after sync, `xRollback` discards pending storage/index state and resets page-size config, `xSavepoint` flushes and tracks the active savepoint, `xRelease` may flush when releasing below the last flushed savepoint, and `xRollbackTo` trips cursors and rolls back pending storage when needed. Debug builds track expected transaction state with `fts5CheckTransactionState()`.

## Module Registration

`fts5Init()` creates `Fts5Global`, initializes the public `fts5_api` methods, randomizes the locale header, registers the `fts5` module with `sqlite3_create_module_v2()`, initializes index debug helpers, expression support, built-in auxiliaries, tokenizers, vocab support, and scalar functions:

- `fts5(pointer)` returns the API pointer.
- `fts5_source_id()` returns the FTS5 source id string.
- `fts5_locale(locale,text)` wraps text with locale metadata.
- `fts5_insttoken(expr)` returns its argument with a subtype requesting prefix instance-token support.

The module advertises `xShadowName` for `config`, `content`, `data`, `docsize`, and `idx` shadow tables, and `xIntegrity` delegates to storage integrity checking while producing user-facing corruption messages.

Loadable-extension entry points `sqlite3_fts_init()` and `sqlite3_fts5_init()` are present when not building into SQLite core; otherwise `sqlite3Fts5Init()` calls the same initializer.

## Storage Layer Flow

`fts5StorageGetStmt()` lazily prepares and caches statements for scans, lookups, content insert/replace/delete, docsize insert/delete/lookup, config replace, and full content scans. It builds SQL according to content mode, unindexed columns, locale columns, and contentless-delete origin columns. Internal shadow-table statement failures are converted to corruption for missing internal tables.

Creation and schema management:

- `sqlite3Fts5StorageOpen()` allocates storage state, creates `%_content` for normal/unindexed content modes, `%_docsize` if column sizes are enabled, `%_config`, and writes the initial version.
- `sqlite3Fts5DropAll()` drops FTS5 shadow tables.
- `sqlite3Fts5StorageRename()` flushes then renames shadow tables.
- `sqlite3Fts5CreateTable()` centralizes shadow table creation and error messages.

Insert/update/delete storage flow:

- `sqlite3Fts5StorageContentInsert()` writes content rows or allocates rowids for external/contentless tables through `%_docsize` when possible.
- `sqlite3Fts5StorageIndexInsert()` tokenizes indexed column values, writes terms to the index with `sqlite3Fts5IndexWrite()`, accumulates per-column token counts, updates totals, and writes `%_docsize`.
- `sqlite3Fts5StorageDelete()` begins a delete write, either adds contentless tombstones or tokenizes old content into delete markers, then removes `%_docsize` and `%_content` rows as appropriate.
- `sqlite3Fts5StorageFindDeleteRow()` and `sqlite3Fts5StorageReleaseDeleteRow()` manage the saved lookup statement used to preserve old values and locale metadata across rowid-changing updates and `sqlite3_value_nochange()` columns.

Totals and docsize behavior:

- `fts5StorageLoadTotals()` reads the averages record through the index.
- `fts5StorageSaveTotals()` serializes row count and per-column totals back to the averages record.
- `sqlite3Fts5StorageSync()` saves totals, syncs the index, and preserves `last_insert_rowid`.
- `sqlite3Fts5StorageDocsize()`, `sqlite3Fts5StorageSize()`, and `sqlite3Fts5StorageRowCount()` back extension APIs and corruption checks.

Maintenance operations:

- `sqlite3Fts5StorageDeleteAll()` deletes data/index/docsize/content rows and reinitializes the index.
- `sqlite3Fts5StorageRebuild()` scans content, retokenizes every indexed column, rebuilds index/docsize/totals, and respects locale metadata.
- `sqlite3Fts5StorageOptimize()`, `sqlite3Fts5StorageMerge()`, and `sqlite3Fts5StorageReset()` delegate to index maintenance/reset.
- `sqlite3Fts5StorageIntegrity()` recomputes checksums from content, verifies docsize and totals, validates shadow row counts, then delegates to `sqlite3Fts5IndexIntegrityCheck()`.

## Tokenizers In This Chunk

The ASCII tokenizer defines an ASCII alphanumeric token table plus `tokenchars` and `separators` exceptions. `fts5AsciiTokenize()` scans separator runs, folds ASCII uppercase to lowercase, grows a temporary fold buffer when needed, and calls the tokenizer callback for each token. Non-ASCII bytes are treated as token bytes by the ASCII tokenizer scan loop.

The Unicode tokenizer starts with UTF-8 read/write helpers when not using amalgamation-provided macros, `Unicode61Tokenizer` state, diacritic-removal constants, category parsing, exception insertion, deletion, creation, token-character testing, and the start of `fts5UnicodeTokenize()`. It supports `categories`, `remove_diacritics`, `tokenchars`, and `separators` options. The tokenizer uses Unicode category tables and a sorted exception list; non-ASCII tokenization and folding continue beyond this chunk.

## Dependencies And Integration Points

This chunk depends heavily on earlier and later FTS5 code in the same amalgamation:

- Index primitives: `fts5DataRead()`, `fts5DataWrite()`, `fts5StructureRead()`, `fts5StructureWrite()`, segment iterators, doclist-index iterators, buffer helpers, varint helpers, tombstone macros, rowid macros, and index sync/rollback/optimize/merge/reinit.
- Expression layer: `sqlite3Fts5ExprNew()`, `sqlite3Fts5ExprAnd()`, `sqlite3Fts5ExprFirst/Next()`, phrase and token APIs, poslist population, and pattern matching.
- Config layer: `sqlite3Fts5ConfigParse()`, `DeclareVtab`, `Load`, `SetValue`, rank parsing, tokenizer config, content mode, locale mode, unindexed columns, prefix indexes, and error routing.
- Tokenizer/Unicode helpers: `sqlite3Fts5Tokenize()`, `sqlite3Fts5TokenizerPattern()`, `sqlite3Fts5UnicodeCategory()`, `sqlite3Fts5UnicodeIsdiacritic()`, category parsing, and fold/remove-diacritic routines beyond this range.
- SQLite core APIs: virtual table callbacks, prepared statements, blobs, scalar functions, modules, value subtypes, `sqlite3_value_nochange()`, `sqlite3_vtab_config()`, `sqlite3_vtab_on_conflict()`, `sqlite3_randomness()`, and extension entry-point macros.

WiredTiger itself is not integrated directly here; the file is a vendored SQLite amalgamation used by tests. Behavioral changes in this chunk affect the embedded SQLite/FTS5 behavior available to those tests.

## Risks And Edge Cases

- `fts5BestIndexMethod()` manipulates `idxStr` while also using `iIdxStr`; this is intentional in SQLite code but brittle if modified without preserving pointer/index invariants.
- Locale blobs depend on a per-connection randomized header; stored values are interpreted only in contexts using the same `Fts5Global` header.
- Contentless-delete tombstones require origin metadata in `%_docsize`; missing or zero origins make deletes no-ops.
- Rank sorting prepares recursive SQL against the same virtual table and uses `pSortCsr` to avoid circular ownership and route source-cursor state; changes can easily reintroduce recursion or lifetime bugs.
- For `detail!=full`, instance and phrase position APIs may retokenize content. Contentless tables return empty position lists, so auxiliary functions must handle missing details.
- `sqlite3_value_nochange()` update handling relies on `pSavedRow` not being reset too early, especially with locale columns.
- Integrity checking can be expensive because it scans content and index structures and may retokenize all indexed columns.
- The storage statement cache temporarily transfers statements to cursors; release paths must return or finalize them to avoid leaks or use-after-reset behavior.
- Tokenizers resize fold buffers during tokenization; OOM must abort cleanly and convert `SQLITE_DONE` callback status back to `SQLITE_OK`.

## Test Signals

Good test coverage for this chunk includes:

- FTS5 MATCH queries with rowid bounds, ascending/descending rowid order, rank sorting, rank MATCH arguments, LIKE/GLOB pattern matching, and special `*reads`/`*id` queries.
- `tokendata=1` tables using `xInstToken()` and prefix inst-token paths, including multiple token-data terms mapping to the same rowid.
- Insert/update/delete cases for normal, external-content, contentless, `contentless_delete=1`, and `contentless_unindexed=1` tables, including REPLACE conflict handling and rowid-changing updates with no-change columns.
- Locale tests using `fts5_locale()`, `xColumnLocale()`, external content locale blobs, normal-content locale side columns, and rejection when `locale=1` is absent.
- Maintenance commands: `delete-all`, `rebuild`, `optimize`, `merge`, `flush`, config updates, and `integrity-check`.
- Corruption tests for missing shadow tables, bad `%_docsize` blobs, mismatched totals, broken `%_idx` split keys, bad doclist-index links, malformed tombstone pages, and stale structure cookies.
- Debug/test builds exercising `fts5_decode`, `fts5_decode_none`, `fts5_rowid`, `fts5_structure`, debug prefix-index comparisons, and doclist reverse checks.
- Tokenizer tests for ASCII `tokenchars`/`separators`, Unicode `categories`, `remove_diacritics`, non-ASCII exceptions, UTF-8 boundary handling, and callback early termination.

## Boundary Notes

The chunk starts after FTS5 index open/close setup code, so definitions for many index structs and helpers are outside this report. It ends inside `fts5UnicodeTokenize()`, before the Unicode tokenizer's full folding, diacritic-removal, callback, and registration logic. The final per-file synthesis should merge this report with adjacent chunks to describe complete FTS5 tokenizer behavior and whole-file SQLite integration.

### subset-b-009046: lines 259630-262899

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.c lines 259630-262899

## Scope

This chunk is the end of SQLite's amalgamated FTS5 implementation and the beginning/end of two auxiliary virtual table extensions. It starts inside the tail of FTS5 tokenizer code, then covers the complete built-in Porter tokenizer wrapper, trigram tokenizer, generated Unicode folding/category tables, FTS5 varint helpers, the `fts5vocab` virtual table module, the `sqlite_stmt` virtual table module, and the final `sqlite3_sourceid()` export.

The code is compiled conditionally as part of `sqlite3.c`: the FTS5 portion is guarded by the surrounding `!defined(SQLITE_CORE) || defined(SQLITE_ENABLE_FTS5)` block, and the statement virtual table is guarded by `!defined(SQLITE_CORE) || defined(SQLITE_ENABLE_STMTVTAB)` plus `!SQLITE_OMIT_VIRTUALTABLE`.

## Purpose

The FTS5 tokenizer code provides built-in tokenization services for full text search:

- The Porter tokenizer wraps an underlying tokenizer, usually `unicode61`, and stems each token before passing it to FTS5.
- The trigram tokenizer emits overlapping three-codepoint tokens for substring-oriented indexing and can advertise LIKE/GLOB pattern support.
- The Unicode helpers fold case, optionally remove diacritics, classify Unicode codepoints, and derive ASCII token-character tables for the `unicode61` tokenizer.

The varint helpers serialize and deserialize SQLite-style variable-length integers for FTS5 internal index records.

The `fts5vocab` module exposes an existing FTS5 index through virtual tables with `col`, `row`, or `instance` views. It reads FTS5 index iterators directly and converts term/doc/position-list data into SQL-visible rows.

The `sqlite_stmt` module exposes prepared statements on a connection as an eponymous virtual table, reporting SQL text and statement status counters.

## Important APIs, Types, and Functions

### Porter tokenizer

- `FTS5_PORTER_MAX_TOKEN` limits tokens subject to stemming to 64 bytes. Larger or very short tokens are passed through unchanged.
- `PorterTokenizer` stores the v2 tokenizer interface copied from the wrapped tokenizer, the wrapped `Fts5Tokenizer`, and a reusable stemming buffer.
- `fts5PorterCreate()` resolves the base tokenizer with `fts5_api.xFindTokenizer_v2()`, defaults to `unicode61`, forwards remaining arguments to the base tokenizer, and copies the tokenizer v2 method table.
- `fts5PorterDelete()` delegates destruction to the wrapped tokenizer's `xDelete()` before freeing its own object.
- `PorterContext` carries the caller's token callback and buffer through the wrapper.
- `fts5PorterCb()` implements the actual stemming pipeline and forwards either the stemmed token or the original token.
- Generated rule functions `fts5PorterStep1B()`, `fts5PorterStep1B2()`, `fts5PorterStep2()`, `fts5PorterStep3()`, and `fts5PorterStep4()` apply suffix rewrites. Hand-written helpers implement Step 1A, Step 1C, Step 5a, and Step 5b.
- Condition helpers `fts5Porter_MGt0()`, `fts5Porter_MGt1()`, `fts5Porter_MEq1()`, `fts5Porter_Ostar()`, `fts5Porter_Vowel()`, and `fts5Porter_MGt1_and_S_or_T()` implement Porter algorithm predicates over a mutable byte buffer.

### Trigram tokenizer and tokenizer registration

- `TrigramTokenizer` contains `bFold` and `iFoldParam`, controlling case folding and diacritic removal.
- `fts5TriCreate()` parses option pairs: `case_sensitive` must be `0` or `1`, and `remove_diacritics` must be `0`, `1`, or `2`. Diacritic removal is rejected when `case_sensitive=1`.
- `fts5TriTokenize()` reads UTF-8 codepoints, optionally folds/removes diacritics via `sqlite3Fts5UnicodeFold()`, skips folded-away diacritic marks, and emits overlapping 3-character tokens with input byte offsets.
- `sqlite3Fts5TokenizerPattern()` identifies trigram tokenizer support for pattern pushdown: folded trigrams support LIKE, case-sensitive trigrams support GLOB, and diacritic-removing trigrams do not advertise pattern support.
- `sqlite3Fts5TokenizerPreload()` detects tokenizer configs whose first argument is `trigram`, so planning can load the tokenizer before `xBestIndex()`.
- `sqlite3Fts5TokenizerInit()` registers `unicode61`, `ascii`, `trigram`, and the v2 `porter` tokenizer with the `fts5_api`.

### Unicode helpers

- `fts5_remove_diacritic()` maps many lowercase diacritic codepoints to ASCII letters using generated `aDia[]` and `aChar[]` tables. The `bComplex` argument controls whether complex mappings marked with the high bit are allowed.
- `sqlite3Fts5UnicodeIsdiacritic()` recognizes combining diacritical marks in the 768-817 range using bitmasks.
- `sqlite3Fts5UnicodeFold()` lowercases ASCII, many BMP ranges from generated case-folding tables, one non-BMP range, and optionally removes diacritics.
- `sqlite3Fts5UnicodeCatParse()` parses two-letter Unicode category selectors such as `Ll`, `Nd`, `P*`, or `L*` into a 32-entry category mask array.
- `aFts5UnicodeBlock`, `aFts5UnicodeMap`, and `aFts5UnicodeData` are generated compressed Unicode category tables.
- `sqlite3Fts5UnicodeCategory()` binary-searches the generated maps to return a compact category code for a codepoint under `1<<20`.
- `sqlite3Fts5UnicodeAscii()` populates a 128-byte ASCII token-character table from a category mask.

### FTS5 varints

- `sqlite3Fts5GetVarint32()` decodes one-, two-, and three-byte varints inline, falling back to `sqlite3Fts5GetVarint()` for larger encodings, then masks to 31 bits.
- `sqlite3Fts5GetVarint()` decodes 64-bit varints in one to nine bytes, with hand-unrolled cases and precomputed masks `SLOT_2_0` and `SLOT_4_2_0`.
- `fts5PutVarint64()` is the noinline slow path for serializing values larger than 14 bits.
- `sqlite3Fts5PutVarint()` fast-paths one- and two-byte writes and delegates larger values.
- `sqlite3Fts5GetVarintLen()` returns the encoded length for values known to be at least 128.

### fts5vocab virtual table

- `Fts5VocabTable` is the vtab object. It stores the target FTS5 table/database names, database handle, `Fts5Global`, vocabulary type, and a recursion guard `bBusy`.
- `Fts5VocabCursor` is the cursor object. It owns the lock-holding statement, `Fts5Table`, index iterator, referenced FTS5 structure, optional upper-bound term, selected columns mask, per-column count/doc arrays, rowid, current term buffer, and instance-position state.
- `FTS5_VOCAB_COL`, `FTS5_VOCAB_ROW`, and `FTS5_VOCAB_INSTANCE` select output schema and iteration behavior.
- `fts5VocabTableType()` dequotes and validates `col`, `row`, or `instance`.
- `fts5VocabInitVtab()` implements both create/connect. It validates arguments, declares the schema, allocates one object containing both table and database names, dequotes identifiers, and stores global state.
- `fts5VocabBestIndexMethod()` recognizes term equality and range constraints, records them in `idxNum`, assigns argument indexes, estimates cost, and consumes ascending `ORDER BY term`.
- `fts5VocabOpenMethod()` resolves the target FTS5 table by preparing a synthetic `MATCH '*id'` query, stepping it to obtain a cursor id, translating that id through `sqlite3Fts5TableFromCsrid()`, flushing pending FTS5 data to disk, and allocating per-column count arrays.
- `fts5VocabFilterMethod()` resets cursor state, extracts term equality/lower/upper constraints, starts an `sqlite3Fts5IndexQuery()`, references the current FTS5 structure for change detection, and positions the cursor.
- `fts5VocabNextMethod()` advances through terms and rowids, accumulates document and occurrence counts from position lists, respects `detail=full`, `detail=columns`, and `detail=none`, and handles the `col`, `row`, and `instance` table variants.
- `fts5VocabColumnMethod()` materializes SQL-visible values for term, column name, document counts, instance rowids, and offsets.
- `sqlite3Fts5VocabInit()` registers the module as `fts5vocab` with `sqlite3_create_module_v2()`.

### sqlite_stmt virtual table

- `StmtRow` stores a snapshot row: rowid, SQL text, integer columns, and next pointer.
- `stmt_vtab` stores the owning `sqlite3*`; `stmt_cursor` stores the same connection and current linked-list row.
- `stmtConnect()` declares schema `sql,ncol,ro,busy,nscan,nsort,naidx,nstep,reprep,run,mem` and stores the connection.
- `stmtFilter()` snapshots all prepared statements reachable from `sqlite3_next_stmt()`, copies SQL text, and reads statement counters using `sqlite3_stmt_status()`.
- `stmtNext()`, `stmtColumn()`, `stmtRowid()`, and `stmtEof()` scan the linked-list snapshot.
- `sqlite3StmtVtabInit()` registers the `sqlite_stmt` module.
- `sqlite3_stmt_init()` is the extension entry point when built outside `SQLITE_CORE`.
- `sqlite3_sourceid()` returns the amalgamation's `SQLITE_SOURCE_ID`.

## Control Flow

Porter tokenization is a wrapper around another tokenizer. `fts5PorterTokenize()` builds a `PorterContext` and calls the wrapped tokenizer's `xTokenize()`, substituting `fts5PorterCb()` as the callback. For each emitted token, `fts5PorterCb()` copies eligible tokens into the local buffer, runs Porter steps in sequence, and calls the original callback with the resulting stem. Tokens shorter than 3 bytes or longer than `FTS5_PORTER_MAX_TOKEN` bypass stemming.

Trigram tokenization is a sliding window over UTF-8 codepoints. `fts5TriTokenize()` fills a three-codepoint buffer, records byte offsets for each codepoint, emits the current trigram, then removes the first codepoint and appends the next folded codepoint. Combining marks that fold to zero are skipped. End-of-input stops after the last complete trigram has been emitted.

Unicode classification and folding are table-driven. Folding lowercases ASCII directly; for BMP characters it binary-searches generated case-fold ranges, computes the lower-case mapping by offset, and optionally passes the result through diacritic removal. Category lookup similarly binary-searches block/map arrays and decodes packed category/range data.

FTS5 varint decoding uses fast-path unrolled branches. The first clear high bit determines the number of bytes. The 32-bit routine inlines the common first three cases and calls the 64-bit routine only for rare longer encodings. The put routine serializes from least significant groups into a temporary buffer for the general case, then reverses into output.

`fts5vocab` query execution starts with virtual table connect/create, where the target FTS5 table name and type are captured. Opening a cursor resolves the live FTS5 table by using an internal MATCH query and cursor id lookup, then flushes pending index changes. Filtering starts an index scan for equality, lower-bound, or full scan. The next method groups consecutive index rows with the same term for `row` and `col` modes, while `instance` mode walks individual position-list entries.

`sqlite_stmt` execution snapshots state at filter time. The cursor owns a linked list of `StmtRow` objects created by walking `sqlite3_next_stmt()`. Subsequent `xNext()` calls free consumed rows, so the output is stable for the scan and cleanup is incremental.

## State and Persistence Behavior

The tokenizer objects are per-tokenizer-instance heap allocations. `PorterTokenizer` owns the wrapped tokenizer instance and a reusable buffer; `TrigramTokenizer` owns only option flags. Neither persists data to disk.

Unicode tables are static read-only generated data embedded in the amalgamation. They are process-local constants and have no runtime persistence.

The FTS5 varint functions operate on caller-provided memory and do not own state.

`fts5vocab` is read-only but observes persistent FTS5 index state. `fts5VocabOpenMethod()` explicitly calls `sqlite3Fts5FlushToDisk()` after resolving the target FTS5 table, so pending in-memory FTS5 changes are flushed before vocabulary scanning. The cursor also stores a referenced FTS5 structure pointer and `fts5VocabNextMethod()` calls `sqlite3Fts5StructureTest()` before advancing, detecting index structure changes while the scan is active. The `pStmt` member is kept open to hold the target table/cursor relationship for the lifetime of the vocab cursor.

`sqlite_stmt` is read-only and snapshots transient prepared-statement metadata into heap rows. Counters are read without reset by passing zero to `sqlite3_stmt_status()`. The snapshot rows are freed as the scan advances or when the cursor closes.

## Dependencies and Integration Points

This chunk depends heavily on surrounding SQLite and FTS5 internals:

- SQLite allocator and utility APIs: `sqlite3_malloc`, `sqlite3_malloc64`, `sqlite3_free`, `sqlite3_mprintf`, `sqlite3_stricmp`, `sqlite3_declare_vtab`, `sqlite3_create_module`, `sqlite3_create_module_v2`, `sqlite3_prepare_v2`, `sqlite3_step`, `sqlite3_finalize`, `sqlite3_value_text`, `sqlite3_value_bytes`, and result APIs.
- FTS5 tokenizer APIs: `fts5_api`, `fts5_tokenizer`, `fts5_tokenizer_v2`, `Fts5Tokenizer`, `Fts5TokenizerConfig`, and the `xCreateTokenizer`/`xCreateTokenizer_v2` registration path.
- FTS5 internals: `Fts5Global`, `Fts5Table`, `Fts5Index`, `Fts5IndexIter`, `Fts5Buffer`, `Fts5Config`, `sqlite3Fts5IndexQuery()`, `sqlite3Fts5IterNextScan()`, `sqlite3Fts5IterTerm()`, `sqlite3Fts5IterEof()`, `sqlite3Fts5StructureRef()`, `sqlite3Fts5StructureRelease()`, `sqlite3Fts5StructureTest()`, `sqlite3Fts5BufferSet()`, `sqlite3Fts5BufferFree()`, and `sqlite3Fts5FlushToDisk()`.
- UTF-8 and FTS5 macros: `READ_UTF8`, `WRITE_UTF8`, `FTS5_SKIP_UTF8`, `FTS5_POS2COLUMN`, `FTS5_POS2OFFSET`, `MIN`, `ArraySize`, `UNUSED_PARAM`, and `UNUSED_PARAM2`.
- Statement inspection APIs: `sqlite3_next_stmt`, `sqlite3_sql`, `sqlite3_column_count`, `sqlite3_stmt_readonly`, `sqlite3_stmt_busy`, and `sqlite3_stmt_status`.

The chunk is integrated into SQLite by module registration functions. `sqlite3Fts5TokenizerInit()` and `sqlite3Fts5VocabInit()` are called from the surrounding FTS5 initialization path; `sqlite3StmtVtabInit()` is called by core or extension initialization; `sqlite3_stmt_init()` is the external extension entry point for loadable builds.

## Risks and Edge Cases

- Porter stemming assumes lowercase ASCII-like token bytes from the base tokenizer. It operates byte-wise, not Unicode-aware. If a non-lowercase or multi-byte token reaches it, suffix rules may not behave linguistically, but the wrapper normally uses tokenizers that fold first.
- `fts5PorterCb()` uses a fixed buffer in `PorterTokenizer`; the max-token guard avoids overflow. Tokens over 64 bytes are not stemmed, so behavior differs for long terms.
- Many generated Porter step functions index `aBuf[nBuf-2]`; the caller only invokes them after the minimum token-length guard and prior transformations that maintain non-empty buffers.
- `fts5TriTokenize()` emits only complete three-codepoint windows. Inputs with fewer than three non-diacritic folded codepoints produce no tokens, which is intentional but important for MATCH behavior.
- Trigram options deliberately reject `remove_diacritics` with `case_sensitive=1`; changing this could break LIKE/GLOB pattern compatibility assumptions.
- Unicode folding/category data is generated. Table corruption or regeneration mismatches would affect token boundaries and index compatibility across SQLite versions.
- `sqlite3Fts5UnicodeCategory()` returns category 0 for codepoints at or above `1<<20`, so tokenization for very high codepoints is intentionally conservative in this table.
- Varint functions assume sufficient readable/writable bytes supplied by callers. They are low-level helpers without bounds parameters.
- `fts5vocab` depends on the internal `MATCH '*id'` mechanism and cursor-id lookup. If the target table cannot be resolved, it reports `no such fts5 table`.
- `fts5vocab` uses `bBusy` to prevent recursive resolution of the target table; recursive definitions return an error.
- `fts5vocab` count semantics vary with FTS5 detail mode. With `detail=none`, column names and offsets are not available, and instance iteration stops early.
- Position-list decoding can detect impossible column indexes and return `FTS5_CORRUPT`.
- `stmtFilter()` materializes all prepared statements at once. A connection with many large SQL strings can allocate noticeable memory during a scan.
- `sqlite_stmt` reports live statement status counters at snapshot time. Values may change after snapshot but before the caller reads all rows; the virtual table intentionally reports the snapshot, not a live view.

## Test Signals

Useful tests for this chunk include:

- FTS5 tokenizer creation tests for `porter`, with default `unicode61` and explicit wrapped tokenizer arguments.
- Porter stemming golden cases for Step 1A through Step 5, including pass-through behavior for tokens shorter than 3 bytes and longer than 64 bytes.
- Trigram tokenizer tests for ASCII text, UTF-8 multibyte text, folded case, diacritic removal, short input, and byte-offset correctness.
- Planner tests confirming `sqlite3Fts5TokenizerPattern()` enables LIKE for folded trigrams, GLOB for case-sensitive trigrams, and no pattern support when diacritic removal is active.
- Unicode folding/category tests against known codepoints, combining diacritic handling, ASCII table generation, and invalid/very high codepoints.
- FTS5 varint round-trip tests around 1-, 2-, 3-, 4-, 5-, and 9-byte boundaries, plus `sqlite3Fts5GetVarint32()` fallback paths.
- `fts5vocab` SQL tests for `col`, `row`, and `instance` schemas; term equality/range constraints; `ORDER BY term`; and all FTS5 detail modes.
- `fts5vocab` corruption or defensive tests for invalid position-list column values and index-structure changes during a cursor scan.
- `sqlite_stmt` tests that prepare several statements and verify SQL text, column counts, read-only flags, busy status, and statement counters exposed by the virtual table.
- Extension-build tests for `sqlite3_stmt_init()` and core-build tests for `sqlite3StmtVtabInit()` registration.

## Chunk Boundaries and Follow-up for Merge

The first lines of this chunk continue from earlier `unicode61` tokenization logic, so the merged per-file report should connect this chunk to the preceding tokenizer definitions and tokenizer config parsing. The FTS5 section ends here with `sqlite3Fts5VocabInit()` and the composite-file trailer. The following code starts and completes `stmt.c`, then closes the amalgamation with `sqlite3_sourceid()`.
