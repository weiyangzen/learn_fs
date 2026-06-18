# Research: sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009047`: lines 1-5212, `Docs/researches/chunks/subset-b-009047_research.md`
- `subset-b-009048`: lines 5213-10675, `Docs/researches/chunks/subset-b-009048_research.md`
- `subset-b-009049`: lines 10676-13775, `Docs/researches/chunks/subset-b-009049_research.md`

## Chunk Research

### subset-b-009047: lines 1-5212

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.h lines 1-5212

## Chunk Scope

This chunk covers the first 5,212 lines of the bundled SQLite public C API header used under WiredTiger test third-party sources. The file identifies itself as the authoritative API surface for SQLite clients and as generated from `sqlite.h.in`. This chunk starts at the include guard and version metadata and ends in the opening documentation for `sqlite3_data_count()`, immediately after the `sqlite3_step()` declaration.

## Purpose

The covered range defines the public ABI and behavioral contracts for core SQLite library use:

- compile/runtime version checks, compile-option diagnostics, and thread-safety discovery;
- opaque handle types for database connections, statements, values, contexts, VFS files, mutexes, and extension API tables;
- primary database lifecycle calls, including initialization, shutdown, open, close, and one-shot execution;
- result-code, open-flag, device-capability, lock-level, sync, file-control, configuration, DB configuration, authorizer, trace, prepare, bind, and limit constants;
- VFS and file I/O method tables that allow SQLite to run on custom storage or OS layers;
- memory allocation and formatted string APIs that callers must pair with SQLite's allocator;
- prepared-statement construction, SQL text access, parameter binding, result-column metadata, and statement stepping.

As a header, this chunk does not implement behavior itself. Its comments are part of the public API contract and are used by SQLite to generate official C API documentation.

## Important APIs, Types, and Constants

### Linkage, Version, and Diagnostics

- `SQLITE_EXTERN`, `SQLITE_API`, `SQLITE_CDECL`, `SQLITE_APICALL`, `SQLITE_STDCALL`, `SQLITE_CALLBACK`, and `SQLITE_SYSAPI` parameterize linkage and calling conventions.
- `SQLITE_DEPRECATED` and `SQLITE_EXPERIMENTAL` are no-op markers for API stability classification.
- Version identity is fixed in this header as `SQLITE_VERSION "3.50.4"`, `SQLITE_VERSION_NUMBER 3050004`, and a Fossil-derived `SQLITE_SOURCE_ID`.
- `sqlite3_version[]`, `sqlite3_libversion()`, `sqlite3_sourceid()`, and `sqlite3_libversion_number()` expose runtime version identity. The comments recommend asserting that runtime values match the compile-time macros.
- `sqlite3_compileoption_used()` and `sqlite3_compileoption_get()` expose compile-time build options unless `SQLITE_OMIT_COMPILEOPTION_DIAGS` replaces them with inert macros.
- `sqlite3_threadsafe()` reports the compile-time mutex setting only, not runtime changes made through `sqlite3_config()`.

### Core Opaque Handles and Integer Types

- `typedef struct sqlite3 sqlite3;` is the database connection handle.
- `sqlite_int64`, `sqlite_uint64`, `sqlite3_int64`, and `sqlite3_uint64` normalize 64-bit integer types across compilers.
- `typedef struct sqlite3_stmt sqlite3_stmt;` is the prepared-statement handle.
- `typedef struct sqlite3_value sqlite3_value;` represents dynamically typed SQL values. The comments distinguish protected and unprotected values by mutex ownership.
- `typedef struct sqlite3_context sqlite3_context;` is passed to application-defined SQL functions.
- `sqlite3_file`, `sqlite3_io_methods`, and `sqlite3_vfs` define the OS/VFS abstraction.

### Connection and Execution APIs

- `sqlite3_close()` and `sqlite3_close_v2()` destroy or eventually destroy a connection. `sqlite3_close()` returns `SQLITE_BUSY` if statements, BLOBs, or backups are still outstanding; `sqlite3_close_v2()` allows a zombie connection that is freed later.
- `sqlite3_exec()` wraps prepare, step, and finalize for semicolon-separated UTF-8 SQL and invokes an optional row callback.
- `sqlite3_open()`, `sqlite3_open16()`, and `sqlite3_open_v2()` construct database connections. `sqlite3_open_v2()` accepts open flags and an optional VFS name.
- `sqlite3_extended_result_codes()` enables extended result-code reporting for a connection.
- `sqlite3_complete()` and `sqlite3_complete16()` test whether a SQL string appears complete for command-line input.
- `sqlite3_interrupt()` and `sqlite3_is_interrupted()` coordinate cancellation of running statements on a connection.

### Result Codes and Flags

The chunk defines the primary SQLite result-code namespace:

- success and row lifecycle codes: `SQLITE_OK`, `SQLITE_ROW`, `SQLITE_DONE`;
- general failures: `SQLITE_ERROR`, `SQLITE_INTERNAL`, `SQLITE_PERM`, `SQLITE_ABORT`, `SQLITE_BUSY`, `SQLITE_LOCKED`, `SQLITE_NOMEM`, `SQLITE_READONLY`, `SQLITE_INTERRUPT`, `SQLITE_IOERR`, `SQLITE_CORRUPT`, `SQLITE_FULL`, `SQLITE_CANTOPEN`, `SQLITE_SCHEMA`, `SQLITE_CONSTRAINT`, `SQLITE_MISUSE`, and related values;
- extended codes built by OR-ing a primary code with a shifted detail, including `SQLITE_IOERR_*`, `SQLITE_LOCKED_*`, `SQLITE_BUSY_*`, `SQLITE_CANTOPEN_*`, `SQLITE_CORRUPT_*`, `SQLITE_READONLY_*`, `SQLITE_CONSTRAINT_*`, `SQLITE_NOTICE_*`, `SQLITE_WARNING_AUTOINDEX`, `SQLITE_AUTH_USER`, `SQLITE_OK_LOAD_PERMANENTLY`, and `SQLITE_OK_SYMLINK`.

Open flags cover both public `sqlite3_open_v2()` bits and VFS-only bits:

- public open bits include `SQLITE_OPEN_READONLY`, `SQLITE_OPEN_READWRITE`, `SQLITE_OPEN_CREATE`, `SQLITE_OPEN_URI`, `SQLITE_OPEN_MEMORY`, `SQLITE_OPEN_NOMUTEX`, `SQLITE_OPEN_FULLMUTEX`, `SQLITE_OPEN_SHAREDCACHE`, `SQLITE_OPEN_PRIVATECACHE`, `SQLITE_OPEN_NOFOLLOW`, and `SQLITE_OPEN_EXRESCODE`;
- VFS-only bits include journal/temp/transient object kinds, `SQLITE_OPEN_DELETEONCLOSE`, `SQLITE_OPEN_EXCLUSIVE`, `SQLITE_OPEN_WAL`, and legacy `SQLITE_OPEN_MASTER_JOURNAL`.

Device, lock, sync, shared-memory, and access constants include:

- `SQLITE_IOCAP_*` for atomicity, safe append, sequential writes, powersafe overwrite, immutable media, batch atomic writes, and subpage reads;
- `SQLITE_LOCK_NONE`, `SQLITE_LOCK_SHARED`, `SQLITE_LOCK_RESERVED`, `SQLITE_LOCK_PENDING`, and `SQLITE_LOCK_EXCLUSIVE`;
- `SQLITE_SYNC_NORMAL`, `SQLITE_SYNC_FULL`, and `SQLITE_SYNC_DATAONLY`;
- `SQLITE_ACCESS_EXISTS`, `SQLITE_ACCESS_READWRITE`, and `SQLITE_ACCESS_READ`;
- `SQLITE_SHM_UNLOCK`, `SQLITE_SHM_LOCK`, `SQLITE_SHM_SHARED`, `SQLITE_SHM_EXCLUSIVE`, and `SQLITE_SHM_NLOCK`.

### VFS and File I/O Interfaces

`sqlite3_file` contains a pointer to an `sqlite3_io_methods` table. The method table defines the file-handle operations SQLite expects:

- version 1: close, read, write, truncate, sync, file size, lock/unlock, reserved-lock check, file-control, sector size, and device characteristics;
- version 2: shared-memory map, lock, barrier, and unmap methods used by WAL;
- version 3: memory-map fetch and unfetch methods.

The comments specify critical invariants. A VFS must set `sqlite3_file.pMethods` to either a valid method table or `NULL`, including on failed opens. Short reads returning `SQLITE_IOERR_SHORT_READ` must zero-fill unread bytes to avoid corruption. Lock calls only upgrade or downgrade according to the documented lock-order model.

`SQLITE_FCNTL_*` opcodes define the generic file-control channel shared by `sqlite3_file_control()` and `xFileControl()`. This range includes opcodes for lock-state debugging, file-size hints and limits, file and journal pointers, sync and commit-phase signals, Windows retry/handle controls, WAL persistence and blocking, powersafe-overwrite control, pragma interception, busy-handler access, temp filename generation, mmap size, VFS stack discovery, batch atomic write begin/commit/rollback, lock timeout, data version, checkpoint start/done notifications, external-reader detection, checksum VFS, reset cache, null I/O, and block-on-connect behavior.

`sqlite3_vfs` defines the virtual filesystem object. Version 1 fields cover file open/delete/access/full-pathname, dynamic library operations, randomness, sleep, current time, and last error. Version 2 adds `xCurrentTimeInt64()`. Version 3 adds system-call override/lookup/enumeration hooks used by some VFSes for testing.

### Initialization and Configuration

- `sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_os_init()`, and `sqlite3_os_end()` define process-level setup and teardown. Applications should call only initialize/shutdown; OS init/end are called internally or supplied for custom OS builds.
- `sqlite3_config()` controls global configuration and is generally valid only before initialization or after shutdown, except for documented anytime options.
- `sqlite3_db_config()` controls per-connection settings.
- `sqlite3_mem_methods` defines a replacement allocator with `xMalloc`, `xFree`, `xRealloc`, `xSize`, `xRoundup`, `xInit`, `xShutdown`, and `pAppData`.

Global `SQLITE_CONFIG_*` options in this chunk include threading modes, allocator/memory status/page cache/static heap/mutex/lookaside/page-cache replacement/logging/URI/covering-index scan/SQL log/mmap/Windows heap/page-cache header size/sorter PMA/statement journal spill/small malloc/sorter reference size/memory DB max size/rowid-in-view options.

Per-connection `SQLITE_DBCONFIG_*` options include main DB name, lookaside, foreign keys, triggers, FTS3 tokenizer, load extension, no checkpoint on close, QPSG, trigger EQP, reset database, defensive mode, writable schema, legacy alter table and file format, double-quoted string handling, views, trusted schema, statement scan status, reverse scan order, ATTACH create/write controls, SQL comments, and `SQLITE_DBCONFIG_MAX`.

### Connection State APIs

- `sqlite3_last_insert_rowid()` and `sqlite3_set_last_insert_rowid()` expose and override the most recent rowid state for a connection.
- `sqlite3_changes()`/`sqlite3_changes64()` report rows modified by the most recent qualifying statement, excluding triggers, foreign-key side effects, REPLACE side effects, and view changes intercepted by INSTEAD OF triggers.
- `sqlite3_total_changes()`/`sqlite3_total_changes64()` report cumulative direct and trigger changes since the connection opened, with caveats for foreign-key actions and REPLACE.
- `sqlite3_busy_handler()`, `sqlite3_busy_timeout()`, and `sqlite3_setlk_timeout()` configure lock contention behavior. `SQLITE_SETLK_BLOCK_ON_CONNECT` controls blocking connection behavior for WAL-mode blocking locks in supported builds.

### Utility, Memory, and Authorization APIs

- `sqlite3_get_table()` and `sqlite3_free_table()` are legacy result-table helpers built around `sqlite3_exec()`.
- `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_snprintf()`, and `sqlite3_vsnprintf()` provide SQLite-managed formatting utilities.
- `sqlite3_malloc()`, `sqlite3_malloc64()`, `sqlite3_realloc()`, `sqlite3_realloc64()`, `sqlite3_free()`, and `sqlite3_msize()` expose SQLite allocator calls. Returned memory must be managed through SQLite, not the system allocator.
- `sqlite3_memory_used()` and `sqlite3_memory_highwater()` expose allocator statistics when memory status is enabled.
- `sqlite3_randomness()` exposes the internal PRNG and seeds from the default VFS randomness method when needed.
- `sqlite3_set_authorizer()` registers a compile-time SQL authorization callback. `SQLITE_DENY`, `SQLITE_IGNORE`, and many `SQLITE_*` action codes define callback behavior for schema changes, DML, PRAGMA, reads, transactions, attach/detach, virtual tables, functions, savepoints, and recursion.

### Trace, Progress, and Open/URI APIs

- Deprecated `sqlite3_trace()` and `sqlite3_profile()` are retained for compatibility.
- `SQLITE_TRACE_STMT`, `SQLITE_TRACE_PROFILE`, `SQLITE_TRACE_ROW`, and `SQLITE_TRACE_CLOSE` classify `sqlite3_trace_v2()` callbacks.
- `sqlite3_trace_v2()` registers the preferred tracing hook for one connection; only one trace callback may be active per connection.
- `sqlite3_progress_handler()` registers a periodic callback during long `sqlite3_step()` or prepare activity; a nonzero return interrupts the operation.
- URI helpers `sqlite3_uri_parameter()`, `sqlite3_uri_boolean()`, `sqlite3_uri_int64()`, `sqlite3_uri_key()`, `sqlite3_filename_database()`, `sqlite3_filename_journal()`, `sqlite3_filename_wal()`, `sqlite3_database_file_object()`, `sqlite3_create_filename()`, and `sqlite3_free_filename()` support VFS and VFS-shim interpretation of filenames and associated journal/WAL names.
- Error APIs `sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_errmsg()`, `sqlite3_errmsg16()`, `sqlite3_errstr()`, and `sqlite3_error_offset()` report the latest connection error, error text, or SQL token offset.

### Prepared Statements, Limits, Binding, and Columns

Prepared statement lifecycle in this range is:

1. construct using `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, or `sqlite3_prepare16_v3()`;
2. bind values with `sqlite3_bind_*()`;
3. run with `sqlite3_step()`;
4. reset with `sqlite3_reset()` in later header sections, then optionally rebind and step again;
5. destroy with `sqlite3_finalize()` in later header sections.

This chunk defines `sqlite3_limit()` plus `SQLITE_LIMIT_*` categories for string/blob/row length, SQL length, column count, expression depth, compound select terms, VDBE op count, function arguments, attached DB count, LIKE/GLOB pattern length, variable number, trigger depth, and worker threads.

Prepare flags include `SQLITE_PREPARE_PERSISTENT`, `SQLITE_PREPARE_NORMALIZE`, `SQLITE_PREPARE_NO_VTAB`, and `SQLITE_PREPARE_DONT_LOG`.

Statement-inspection APIs include `sqlite3_sql()`, `sqlite3_expanded_sql()`, optional `sqlite3_normalized_sql()`, `sqlite3_stmt_readonly()`, `sqlite3_stmt_isexplain()`, `sqlite3_stmt_explain()`, and `sqlite3_stmt_busy()`.

Binding APIs include blob, blob64, double, int, int64, null, text, text16, text64, value, pointer, zeroblob, and zeroblob64 variants. Parameter metadata helpers are `sqlite3_bind_parameter_count()`, `sqlite3_bind_parameter_name()`, `sqlite3_bind_parameter_index()`, and `sqlite3_clear_bindings()`.

Column/result metadata covered before the chunk boundary includes `sqlite3_column_count()`, `sqlite3_column_name()`, `sqlite3_column_name16()`, the optional origin metadata family `sqlite3_column_database_name*`, `sqlite3_column_table_name*`, `sqlite3_column_origin_name*`, and declared-type APIs `sqlite3_column_decltype()` and `sqlite3_column_decltype16()`.

The chunk ends after `sqlite3_step()` and at the start of `sqlite3_data_count()` documentation, so row-value extraction APIs are expected to continue in the next chunk.

## Control Flow and Lifecycle Contracts

The most important control flows are API lifecycles rather than in-file executable control flow:

- Library lifecycle: optional `sqlite3_initialize()` establishes static resources and OS/VFS setup; `sqlite3_shutdown()` deallocates resources after all connections and other SQLite objects are gone. Many APIs auto-initialize unless `SQLITE_OMIT_AUTOINIT` is used.
- Connection lifecycle: `sqlite3_open*()` creates a connection, `sqlite3_db_config()` and other connection methods mutate connection settings, and `sqlite3_close()`/`sqlite3_close_v2()` release it. Open transactions are rolled back on connection destruction.
- SQL execution via `sqlite3_exec()`: prepare each statement, step rows, call user callback for each row, stop on callback abort or error, then finalize. Error messages returned through the output pointer must be released with `sqlite3_free()`.
- Prepared statement lifecycle: prepare creates a bytecode program; bind attaches parameter values; step returns `SQLITE_ROW`, `SQLITE_DONE`, `SQLITE_BUSY`, `SQLITE_ERROR`, `SQLITE_MISUSE`, or extended result codes; reset/finalize handling is described across this and later chunks.
- VFS lifecycle: SQLite calls `sqlite3_vfs.xOpen()` to populate a caller-allocated `sqlite3_file`; thereafter core code dispatches through `sqlite3_io_methods` for I/O, locking, sync, WAL shared-memory, mmap, and file-control operations.
- Busy handling: lock contention may invoke a connection-specific busy callback repeatedly, but SQLite may bypass it to avoid deadlock.
- Authorization and tracing: authorizer callbacks run during prepare/reprepare, while trace/progress callbacks run around statement execution and, in recent versions, sometimes during prepare.

## State and Persistence Behavior

This header chunk names several state layers:

- process-global state: initialization status, global threading mode, global allocator/mutex/page-cache/log/URI/mmap settings, compile options, PRNG seed, memory statistics, registered VFS chain, and optional system-call override tables inside VFS implementations;
- connection state: open database handles, attached schema names, busy handler, authorizer, trace/progress callbacks, last-insert rowid, change counters, interrupt flag, extended result-code mode, DB config flags, connection-specific limits, and error state;
- statement state: saved SQL text for v2/v3 prepare APIs, current bindings, busy/active state, explain mode, result-column metadata, and automatic reprepare behavior;
- file-system persistence: VFS device characteristics, lock state, WAL/journal file handling, persistent WAL mode, checkpoint behavior, mmap size, atomic-write controls, powersafe-overwrite settings, and URI-driven read/write/memory/cache/immutable/nolock modes.

Several contracts are persistence-critical:

- failed or short VFS reads must obey zero-fill requirements to avoid database corruption;
- file locking flags and busy/setlk behavior coordinate interprocess consistency;
- `immutable=1` disables locking and change detection and is only correct for truly immutable files;
- `nolock=1` can corrupt databases when multiple writers access the same file;
- `SQLITE_DBCONFIG_RESET_DATABASE` is intentionally multi-step and destructive;
- close-on-last-WAL-connection may checkpoint and delete WAL files unless disabled or changed by related controls;
- `SQLITE_FCNTL_DATA_VERSION` and `PRAGMA data_version` integrate with cross-connection change detection.

## Dependencies and Integration Points

- The only direct C standard include in this slice is `<stdarg.h>` for `va_list`.
- The header is C++ compatible through `extern "C"`.
- Most APIs depend on definitions implemented in the SQLite library or amalgamation source, not in this header.
- WiredTiger test code can include this header to compile against the bundled SQLite API without depending on a system SQLite install.
- Custom storage integration happens through `sqlite3_vfs`, `sqlite3_file`, `sqlite3_io_methods`, `SQLITE_OPEN_*`, `SQLITE_IOCAP_*`, `SQLITE_FCNTL_*`, and URI helper APIs.
- Extension integration is signaled by `sqlite3_api_routines`, pointer binding, authorizer/action codes, trace APIs, SQL function context/value types, and the explicit load-extension DB config option.
- Memory integration uses `sqlite3_mem_methods`, global allocator configuration, and SQLite-owned allocation/free APIs.
- Threading integration is controlled by compile-time `SQLITE_THREADSAFE`, global `SQLITE_CONFIG_*` threading modes, per-open mutex flags, protected/unprotected value rules, and documented per-connection threading hazards.

## Risks and Edge Cases

- Header/library mismatch is a concrete ABI risk; the comments recommend runtime assertions against `SQLITE_VERSION_NUMBER`, `SQLITE_SOURCE_ID`, and `SQLITE_VERSION`.
- Many varargs APIs (`sqlite3_config()`, `sqlite3_db_config()`, formatting functions) rely on exact argument shapes implied by integer opcodes; wrong types are undefined behavior in C.
- `sqlite3_close_v2()` can leave zombie connections alive until statements/BLOBs/backups finish, which can hide lifecycle bugs in host-language bindings.
- `sqlite3_exec()` callback pointers and result strings are transient; retaining them after callback return is unsafe.
- `sqlite3_get_table()` result storage must be released with `sqlite3_free_table()`, not `sqlite3_free()`.
- `sqlite3_malloc()` memory must be released with SQLite allocation APIs. Passing foreign or already-freed pointers to `sqlite3_free()`, `sqlite3_realloc()`, or `sqlite3_msize()` is explicitly dangerous.
- Busy handlers, authorizers, progress handlers, and log callbacks have reentrancy restrictions and must not modify or close the invoking connection/statement.
- Shared-cache mode is discouraged and may be omitted from builds.
- URI parameters such as `immutable` and `nolock` trade correctness checks for performance or unusual filesystem support and can yield corruption or stale results if misused.
- Legacy prepare APIs produce less specific `sqlite3_step()` errors and are discouraged; v2/v3 APIs store SQL text and enable automatic reprepare.
- Binding APIs contain lifetime traps: `SQLITE_STATIC` requires caller storage to outlive the binding, `SQLITE_TRANSIENT` copies before return, and destructors are invoked under specific error/NULL/negative-length exceptions.
- Some APIs are conditional on compile options, including compile-option diagnostics, column metadata, statement scan status, normalization, setlk timeout, SQL logging, and memory statistics.
- Several APIs state undefined behavior for invalid handles, finalized statements, invalid filenames, concurrent same-connection access, incorrect encodings, negative blob lengths, and bad VFS method implementations.

## Test Signals

Useful tests or validation signals for code using this chunk include:

- assert runtime version APIs match the compile-time macros when linking the bundled library;
- verify `sqlite3_compileoption_used()`/`get()` behavior under builds with and without `SQLITE_OMIT_COMPILEOPTION_DIAGS`;
- exercise open modes, URI parameters, VFS selection, and error reporting through `sqlite3_open_v2()`;
- confirm custom VFS implementations fill `pMethods` correctly on success/failure, zero-fill short reads, implement lock transitions, and return expected `SQLITE_FCNTL_*` results;
- test WAL persistence/checkpoint/locking behaviors through `SQLITE_FCNTL_PERSIST_WAL`, `SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE`, busy timeout, and setlk timeout where enabled;
- check allocator replacement with `SQLITE_CONFIG_MALLOC` and memory statistics with `sqlite3_memory_used()`/`sqlite3_memory_highwater()`;
- validate authorizer, trace, and progress callbacks for correct invocation timing and non-reentrant behavior;
- run prepared-statement lifecycle tests covering prepare v2/v3, binding all supported value kinds, stepping to `SQLITE_ROW`/`SQLITE_DONE`, automatic reprepare on schema change, and error-code differences from legacy prepare;
- test parameter metadata, column metadata, declared type, and statement SQL retrieval APIs under UTF-8 and UTF-16 prepares;
- verify destructive or security-sensitive DB config settings, especially defensive mode, trusted schema, reset database, load extension, writable schema, and ATTACH controls.

## Cross-Chunk Notes

- This chunk is the beginning of a much larger header. APIs referenced here but declared later include reset/finalize, column value extraction, BLOB I/O, backup, virtual table, extension, serialization, and many other SQLite interfaces.
- The line 5,212 boundary cuts into the `sqlite3_data_count()` documentation. The declaration and related column-access APIs should be researched in the following chunk before producing the merged per-file report.

### subset-b-009048: lines 5213-10675

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.h lines 5213-10675

## Scope

This chunk is a public C API declaration and contract section from SQLite's amalgamated `sqlite3.h`, embedded under WiredTiger's SQLite test dependency tree. It starts at the tail of statement result-count APIs and spans the API surface for column value extraction, prepared-statement reset/finalize, application-defined SQL functions, SQL value/result objects, collations, connection hooks, extension loading, virtual tables, incremental BLOB I/O, VFS registration, mutexes, file controls, test controls, keyword/dynamic-string/status interfaces, custom page-cache methods, online backup, shared-cache unlock notifications, string matching, WAL hooks/checkpointing, virtual-table planner helper APIs, scan-status instrumentation, cache flushing, and the beginning of pre-update hooks.

The code in this range is almost entirely declarations, macros, opaque type definitions, ABI structs, and detailed API comments. Runtime behavior is implemented elsewhere in the amalgamated `sqlite3.c`; this header chunk defines the contracts that callers, extensions, VFS providers, virtual-table modules, page-cache implementations, and test harnesses must obey.

## Purpose

- Expose row/result access for the SQLite virtual machine after `sqlite3_step()` returns `SQLITE_ROW`, including type conversion, byte-count, pointer lifetime, and out-of-memory ambiguity rules.
- Define prepared-statement lifecycle endpoints: `sqlite3_finalize()` releases statement resources and returns the last execution error, while `sqlite3_reset()` rewinds execution without clearing bound parameters.
- Define registration and callback contracts for application-defined scalar, aggregate, and window SQL functions, including function flags that affect query planning and schema-safety policy.
- Provide APIs for inspecting `sqlite3_value` arguments, returning SQL function results, preserving aggregate state, caching auxiliary data, and attaching wrapper-library client data to a connection.
- Define collation registration and lazy collation lookup callbacks.
- Expose connection state, transaction state, schema/file metadata, commit/rollback/update/autovacuum hooks, shared-cache control, extension loading, and automatic extension registration.
- Define the virtual table ABI: module method table, instance/cursor superclasses, planner handshake structures, constraint operator macros, registration APIs, and later planner helper APIs.
- Define lower-level persistence integration points: incremental BLOB handles, VFS lookup/registration, file-control dispatch, WAL hook/checkpoint operations, online backup, page-cache replacement hooks, and mid-transaction cache flushing.
- Expose concurrency and instrumentation interfaces: mutex allocation/method tables, runtime/db/statement status counters, scan-status metrics, unlock notifications, keyword lookup, dynamic strings, log emission, and testing controls.

## Important APIs, Types, And Constants

### Statement row access and lifecycle

- `sqlite3_data_count(sqlite3_stmt*)` reports available result columns for the current row, with special handling around completed statements and incremental vacuum noted just before this chunk.
- Fundamental datatype constants are `SQLITE_INTEGER`, `SQLITE_FLOAT`, `SQLITE_TEXT`/`SQLITE3_TEXT`, `SQLITE_BLOB`, and `SQLITE_NULL`.
- Column accessors are `sqlite3_column_blob()`, `sqlite3_column_double()`, `sqlite3_column_int()`, `sqlite3_column_int64()`, `sqlite3_column_text()`, `sqlite3_column_text16()`, `sqlite3_column_value()`, `sqlite3_column_bytes()`, `sqlite3_column_bytes16()`, and `sqlite3_column_type()`.
- `sqlite3_finalize()` destroys a prepared statement at any point in its lifecycle and must be called for every prepared statement to avoid leaks.
- `sqlite3_reset()` rewinds a prepared statement for reuse and preserves existing bindings; callers must still inspect its return code because deferred write/locking errors can surface during reset.

### User-defined SQL functions and values

- Function registration APIs are `sqlite3_create_function()`, `sqlite3_create_function16()`, `sqlite3_create_function_v2()`, and `sqlite3_create_window_function()`.
- Text encoding constants are `SQLITE_UTF8`, `SQLITE_UTF16LE`, `SQLITE_UTF16BE`, `SQLITE_UTF16`, deprecated `SQLITE_ANY`, and collation-only `SQLITE_UTF16_ALIGNED`.
- Function property flags include `SQLITE_DETERMINISTIC`, `SQLITE_DIRECTONLY`, `SQLITE_SUBTYPE`, `SQLITE_INNOCUOUS`, `SQLITE_RESULT_SUBTYPE`, and `SQLITE_SELFORDER1`.
- Deprecated compatibility APIs in this chunk include `sqlite3_aggregate_count()`, `sqlite3_expired()`, `sqlite3_transfer_bindings()`, `sqlite3_global_recover()`, `sqlite3_thread_cleanup()`, and `sqlite3_memory_alarm()`.
- `sqlite3_value_*()` APIs inspect protected SQL values passed to functions and virtual tables: blob, double, integer, int64, pointer, UTF-8/UTF-16 text, byte counts, original/numeric type, no-change marker, from-bind marker, encoding, subtype, duplication, and free.
- `sqlite3_aggregate_context()` allocates per-group aggregate state, `sqlite3_user_data()` retrieves the registration `pApp`, and `sqlite3_context_db_handle()` reaches the owning connection.
- `sqlite3_get_auxdata()` and `sqlite3_set_auxdata()` cache per-argument function data, often for compiled regex or parser state. `sqlite3_get_clientdata()` and `sqlite3_set_clientdata()` attach named wrapper-private pointers to a connection.
- `sqlite3_destructor_type`, `SQLITE_STATIC`, and `SQLITE_TRANSIENT` define ownership transfer semantics for result and binding buffers.
- Result APIs include `sqlite3_result_blob()`, `sqlite3_result_blob64()`, `sqlite3_result_double()`, `sqlite3_result_error*()`, `sqlite3_result_int*()`, `sqlite3_result_null()`, `sqlite3_result_text*()`, `sqlite3_result_value()`, `sqlite3_result_pointer()`, `sqlite3_result_zeroblob*()`, and `sqlite3_result_subtype()`.

### Collations, connection state, hooks, and extensions

- Collation registration uses `sqlite3_create_collation()`, `sqlite3_create_collation_v2()`, and `sqlite3_create_collation16()`. Lazy registration uses `sqlite3_collation_needed()` and `sqlite3_collation_needed16()`.
- Directory and platform hooks include `sqlite3_sleep()`, global `sqlite3_temp_directory`, global `sqlite3_data_directory`, `sqlite3_win32_set_directory*()`, and `SQLITE_WIN32_*_DIRECTORY_TYPE`.
- Connection and schema introspection APIs include `sqlite3_get_autocommit()`, `sqlite3_db_handle()`, `sqlite3_db_name()`, `sqlite3_db_filename()`, `sqlite3_db_readonly()`, `sqlite3_txn_state()`, and `sqlite3_next_stmt()`.
- Transaction state constants are `SQLITE_TXN_NONE`, `SQLITE_TXN_READ`, and `SQLITE_TXN_WRITE`.
- Hook APIs include `sqlite3_commit_hook()`, `sqlite3_rollback_hook()`, `sqlite3_autovacuum_pages()`, and `sqlite3_update_hook()`.
- Shared cache and memory pressure APIs include `sqlite3_enable_shared_cache()`, `sqlite3_release_memory()`, `sqlite3_db_release_memory()`, `sqlite3_soft_heap_limit64()`, `sqlite3_hard_heap_limit64()`, and deprecated `sqlite3_soft_heap_limit()`.
- `sqlite3_table_column_metadata()` forces schema loading/parsing as needed to report declared type, collation, not-null, primary-key, and autoincrement metadata.
- Extension APIs include `sqlite3_load_extension()`, `sqlite3_enable_load_extension()`, `sqlite3_auto_extension()`, `sqlite3_cancel_auto_extension()`, and `sqlite3_reset_auto_extension()`.

### Virtual table ABI

- Opaque/superclass types are `sqlite3_vtab`, `sqlite3_index_info`, `sqlite3_vtab_cursor`, and `sqlite3_module`.
- `struct sqlite3_module` is the core virtual-table method table. Versioned methods cover create/connect, best-index planning, disconnect/destroy, cursor open/close/filter/next/eof/column/rowid, updates, transaction callbacks, function overloading, rename, savepoint/release/rollback-to, shadow-table naming, and integrity checking.
- `struct sqlite3_index_info` is the `xBestIndex()` planner contract with input constraints/order-by/column-use fields and output constraint usage, strategy identifiers, order consumption, estimated cost/rows, and scan flags.
- Scan flags are `SQLITE_INDEX_SCAN_UNIQUE` and `SQLITE_INDEX_SCAN_HEX`.
- Constraint operators include equality/range operators, `MATCH`, `LIKE`, `GLOB`, `REGEXP`, `NE`, `IS`, null tests, `LIMIT`, `OFFSET`, and `SQLITE_INDEX_CONSTRAINT_FUNCTION`.
- Module registration/removal APIs are `sqlite3_create_module()`, `sqlite3_create_module_v2()`, and `sqlite3_drop_modules()`.
- `sqlite3_declare_vtab()` declares the schema from `xCreate`/`xConnect`; `sqlite3_overload_function()` installs placeholder functions that virtual tables may override.
- Later vtab helper APIs include `sqlite3_vtab_config()`, `sqlite3_vtab_on_conflict()`, `sqlite3_vtab_nochange()`, `sqlite3_vtab_collation()`, `sqlite3_vtab_distinct()`, `sqlite3_vtab_in()`, `sqlite3_vtab_in_first()`, `sqlite3_vtab_in_next()`, and `sqlite3_vtab_rhs_value()`.
- Virtual-table configuration constants are `SQLITE_VTAB_CONSTRAINT_SUPPORT`, `SQLITE_VTAB_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_USES_ALL_SCHEMAS`.
- Conflict return constants exposed here are `SQLITE_ROLLBACK`, `SQLITE_FAIL`, and `SQLITE_REPLACE`; comments cross-reference `SQLITE_IGNORE` and `SQLITE_ABORT` because those are defined for other callback/result-code roles.

### BLOB, VFS, mutex, file-control, and test interfaces

- `sqlite3_blob` is the opaque incremental BLOB handle. Operations are `sqlite3_blob_open()`, `sqlite3_blob_reopen()`, `sqlite3_blob_close()`, `sqlite3_blob_bytes()`, `sqlite3_blob_read()`, and `sqlite3_blob_write()`.
- VFS registry APIs are `sqlite3_vfs_find()`, `sqlite3_vfs_register()`, and `sqlite3_vfs_unregister()`.
- Mutex APIs are `sqlite3_mutex_alloc()`, `sqlite3_mutex_free()`, `sqlite3_mutex_enter()`, `sqlite3_mutex_try()`, `sqlite3_mutex_leave()`, debug-only `sqlite3_mutex_held()`, and `sqlite3_mutex_notheld()`.
- `struct sqlite3_mutex_methods` is the app-defined mutex provider table for `SQLITE_CONFIG_MUTEX` and `SQLITE_CONFIG_GETMUTEX`.
- Mutex type constants include dynamic `SQLITE_MUTEX_FAST`/`SQLITE_MUTEX_RECURSIVE`, static internal mutex IDs, app/VFS static mutexes, and legacy `SQLITE_MUTEX_STATIC_MASTER`.
- `sqlite3_db_mutex()` returns the connection mutex in serialized mode.
- `sqlite3_file_control()` dispatches low-level opcodes to a database file's `xFileControl` or handles selected opcodes directly in SQLite core.
- `sqlite3_test_control()` and `SQLITE_TESTCTRL_*` constants expose unstable internal testing/fault-injection controls.

### String, status, page cache, backup, WAL, and preupdate APIs

- Keyword helpers are `sqlite3_keyword_count()`, `sqlite3_keyword_name()`, and `sqlite3_keyword_check()`.
- Dynamic string APIs revolve around opaque `sqlite3_str`: `sqlite3_str_new()`, `sqlite3_str_finish()`, append/reset methods, and status/value methods.
- Process-wide status APIs are `sqlite3_status()` and `sqlite3_status64()` with `SQLITE_STATUS_*` verbs for memory, page-cache, malloc, and parser stack metrics.
- Connection status uses `sqlite3_db_status()` and `SQLITE_DBSTATUS_*` verbs for lookaside, pager cache, schema, statement memory, cache hit/miss/write/spill, and deferred foreign keys.
- Statement status uses `sqlite3_stmt_status()` and `SQLITE_STMTSTATUS_*` counters for full scans, sorts, automatic indexes, VM steps, reprepare, run count, Bloom-filter hits/misses, and memory used.
- Custom page cache types are `sqlite3_pcache`, `sqlite3_pcache_page`, `struct sqlite3_pcache_methods2`, and obsolete `struct sqlite3_pcache_methods`.
- Online backup uses opaque `sqlite3_backup` and `sqlite3_backup_init()`, `sqlite3_backup_step()`, `sqlite3_backup_finish()`, `sqlite3_backup_remaining()`, and `sqlite3_backup_pagecount()`.
- Shared-cache unlock notification is `sqlite3_unlock_notify()` behind `SQLITE_ENABLE_UNLOCK_NOTIFY`.
- Utility string/log APIs are `sqlite3_stricmp()`, `sqlite3_strnicmp()`, `sqlite3_strglob()`, `sqlite3_strlike()`, and `sqlite3_log()`.
- WAL APIs are `sqlite3_wal_hook()`, `sqlite3_wal_autocheckpoint()`, `sqlite3_wal_checkpoint()`, `sqlite3_wal_checkpoint_v2()`, and checkpoint mode constants `SQLITE_CHECKPOINT_PASSIVE`, `SQLITE_CHECKPOINT_FULL`, `SQLITE_CHECKPOINT_RESTART`, and `SQLITE_CHECKPOINT_TRUNCATE`.
- Scan-status APIs are `sqlite3_stmt_scanstatus()`, `sqlite3_stmt_scanstatus_v2()`, `sqlite3_stmt_scanstatus_reset()`, `SQLITE_SCANSTAT_*` opcodes, and `SQLITE_SCANSTAT_COMPLEX`.
- `sqlite3_db_cacheflush()` flushes dirty pager-cache pages mid-transaction.
- The pre-update hook section begins with `sqlite3_preupdate_hook()` behavior and describes companion APIs `sqlite3_preupdate_old()`, `sqlite3_preupdate_new()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, and blob-write-specific handling that continues beyond this chunk.

## Control Flow And Call Sequences

The statement result sequence is: prepare a statement elsewhere, call `sqlite3_step()`, and only while the latest step result is `SQLITE_ROW` call the `sqlite3_column_*()` APIs. A caller may force conversion by calling a text/blob accessor and then call the matching byte-count accessor. Calling `sqlite3_step()`, `sqlite3_reset()`, or `sqlite3_finalize()` invalidates returned pointers. `sqlite3_reset()` returns completion status for the prior run and prepares the statement for another run without clearing bindings; `sqlite3_finalize()` ends the lifecycle.

The user-defined function path starts with registration on each `sqlite3*` connection. During expression evaluation, SQLite invokes scalar `xFunc`, aggregate `xStep`/`xFinal`, or window `xStep`/`xFinal`/`xValue`/`xInverse` callbacks. The callback reads protected `sqlite3_value**` arguments, optionally uses aggregate context or auxdata, then emits exactly one result or error through `sqlite3_result_*()`. Destructor callbacks associated with function registration, result buffers, auxdata, pointer values, and client data form important cleanup edges.

Collation lookup is a connection-local dispatch. Callers may register explicit collations up front or install a collation-needed callback that registers a missing collation when the parser or VM asks for it. SQLite chooses the registered implementation that minimizes string encoding conversion, but all implementations for the same collation name must impose equivalent ordering.

Connection hooks form callback paths out of transaction execution. Commit hooks may veto a commit by returning non-zero, converting it into a rollback. Rollback hooks report explicit or implicit rollbacks except close-time rollback. Update hooks report rowid-table changes after/before timing that is intentionally unspecified. Autovacuum page callbacks run during commit-time autovacuum and must be simple, non-reentrant arithmetic decisions.

Extension loading is disabled by default. The safer flow is to enable only the C API via `sqlite3_db_config(...SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION...)` outside this chunk, then call `sqlite3_load_extension()`. `sqlite3_enable_load_extension()` enables both C loading and the SQL `load_extension()` function, which broadens SQL-injection impact. Automatic extensions register process-wide entry points that run for subsequent database opens.

Virtual table control flow is a multi-stage handshake. The application registers a stable `sqlite3_module` with a connection. SQLite invokes `xCreate` or `xConnect`, the module declares a schema with `sqlite3_declare_vtab()`, then queries call `xBestIndex()` with `sqlite3_index_info` inputs. `xBestIndex()` selects constraints, ordering, estimated cost/rows, and strategy IDs. Execution then opens a cursor, calls `xFilter()` with argv values selected by `xBestIndex()`, iterates through `xNext()`/`xEof()`, returns columns/rowids, and performs updates through `xUpdate()` when needed. Transaction and savepoint methods mirror SQLite transaction control.

Incremental BLOB flow opens a rowid-table text/blob cell using `sqlite3_blob_open()`, optionally repositions within the same table/column using `sqlite3_blob_reopen()`, reads/writes fixed-size slices, and closes with `sqlite3_blob_close()`. Writes cannot change blob length. Updating or deleting the underlying row expires the handle, causing later reads/writes to return `SQLITE_ABORT`.

Online backup flow is explicit: `sqlite3_backup_init()` creates state and opens a write transaction on the destination, repeated `sqlite3_backup_step()` calls copy pages, and exactly one `sqlite3_backup_finish()` releases resources and either commits or rolls back destination work. Source read locks are held only during each step, so source writes can proceed between steps and may restart copying.

WAL flow uses either a custom `sqlite3_wal_hook()` or the convenience `sqlite3_wal_autocheckpoint()`, which installs a hook that runs passive checkpoints after a frame threshold. Manual checkpointing uses `sqlite3_wal_checkpoint_v2()` with increasing blocking behavior from PASSIVE to FULL to RESTART to TRUNCATE. Hook and autocheckpoint installation overwrite each other because both occupy the single WAL callback slot on a connection.

Status and scan-status APIs are observational. Global status, connection status, statement counters, and scan-status measurements expose counters/high-water marks with reset flags. Scan status is build-conditional and indexes query-plan elements, enabling applications to compare planner estimates with measured loop visits.

## State And Persistence Behavior

Most declarations in this header manipulate opaque state owned by SQLite. Prepared statements hold current row values, converted value buffers, bindings, execution counters, and VM state. The chunk's comments repeatedly define pointer validity: column text/blob pointers live only until conversion or statement advancement/reset/finalize; `sqlite3_column_value()` returns an unprotected value; byte counts exclude zero terminators; `sqlite3_column_type()` is meaningful before conversions.

User-defined function state is split across connection-local function registries, per-call `sqlite3_context`, protected input values, aggregate context memory, auxdata cached on expression arguments, and optional connection client data. Auxdata can be discarded earlier than a caller expects, including immediately during `sqlite3_set_auxdata()` on allocation failure or planner-time evaluation, so destructors and post-call pointer use are central correctness concerns.

Function flags and virtual-table flags feed persistent schema safety. `SQLITE_DIRECTONLY`, `SQLITE_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_INNOCUOUS` determine whether application-defined behavior may run from views, triggers, constraints, generated columns, expression indexes, partial indexes, or untrusted schemas. Misclassification can turn a database file's schema into a vehicle for invoking application code.

Connection-global and process-global variables affect persistence locations. `sqlite3_temp_directory` controls temporary file placement for built-in VFSes, while `sqlite3_data_directory` affects relative database file resolution on Windows VFSes. The comments warn that changing these while connections are active is unsafe and, for `sqlite3_data_directory`, can corrupt databases.

Transaction and persistence state are exposed by `sqlite3_get_autocommit()`, `sqlite3_txn_state()`, hooks, autovacuum callbacks, BLOB handles, backup handles, WAL checkpoints, and cache flushing. Some APIs directly affect on-disk state: incremental BLOB writes modify existing cell content, online backup writes destination database pages, WAL checkpoints move WAL frames into database files and may truncate WAL files, autovacuum callbacks choose how many free pages to remove, and `sqlite3_db_cacheflush()` writes dirty cache pages mid-transaction.

Virtual table implementations own their own persistence behind `sqlite3_vtab` subclasses. SQLite relies on the module's claims, such as constraint support and unique scans, to decide rollback behavior and query planning. If a module claims `SQLITE_VTAB_CONSTRAINT_SUPPORT`, it promises constraint failures are reported before modifying internal or persistent data structures.

Custom page-cache state is process and cache-instance state supplied via `sqlite3_config(SQLITE_CONFIG_PCACHE2, ...)`. SQLite copies the method table, calls `xInit()` during initialization, creates per-database cache instances through `xCreate()`, pins/unpins pages through `xFetch()` and `xUnpin()`, and expects `xDestroy()`/`xShutdown()` to release resources. Because this sits under pager behavior, mistakes can corrupt cache coherence or cause memory leaks.

Mutex state may be SQLite-provided or application-provided. Static mutex IDs are ABI-visible but primarily internal; applications should allocate dynamic fast/recursive mutexes if they use this subsystem directly. Custom mutex providers must initialize without using SQLite allocation in `xMutexInit()` and support all static mutex types SQLite may request.

## Dependencies And Integration Points

- This header depends on earlier declarations of `sqlite3`, `sqlite3_stmt`, `sqlite3_value`, `sqlite3_context`, `sqlite3_int64`, `sqlite3_uint64`, `sqlite3_filename`, `sqlite3_vfs`, `sqlite3_mutex`, result codes, open flags, config flags, and many cross-linked constants.
- The statement APIs integrate with prepared-statement creation/binding/stepping APIs declared in other chunks and implemented in the VDBE.
- Function, aggregate, window, collation, auxdata, subtype, and pointer-passing APIs integrate application C callbacks with SQL expression evaluation.
- Virtual table definitions are a major extension ABI. They integrate with the parser (`CREATE VIRTUAL TABLE`), planner (`xBestIndex`), VM execution (`xFilter`/`xColumn`/`xUpdate`), transaction manager, savepoints, integrity checks, and optional shadow-table handling.
- BLOB APIs integrate with rowid table storage, constraints, foreign-key rules, transaction commit, and pre-update hook behavior.
- VFS APIs and file-control dispatch integrate SQLite with OS-specific filesystem implementations, custom VFS providers, and storage-engine-specific controls.
- Mutex and page-cache methods integrate embedders with SQLite's process initialization, pager cache, and memory pressure mechanisms.
- Backup, WAL, checkpoint, autovacuum, and cache-flush APIs integrate with pager locking, journal/WAL files, database page persistence, and busy handlers.
- Status, scan-status, keyword, dynamic-string, string match, and logging APIs integrate with diagnostics, query tuning, extension code, and test harnesses.
- Test-control constants integrate with SQLite's internal fault-injection and coverage tests, not stable application logic.

## Risks And Edge Cases

- The column access APIs have strict validity windows. Calling them outside a current `SQLITE_ROW`, mixing UTF-8 and UTF-16 accessors in the wrong order, or retaining returned pointers after conversions/reset/finalize can yield undefined behavior or stale pointers.
- `sqlite3_column_value()` returns an unprotected `sqlite3_value`; using it with general `sqlite3_value_*()` APIs in multithreaded application code is not safe. The intended use is mainly inside functions and virtual tables.
- `sqlite3_reset()` can report errors even when previous `sqlite3_step()` returned `SQLITE_ROW`, notably for `RETURNING` statements whose write completion is deferred.
- User-defined functions must not close the database connection or finalize/reset the running statement. Function result and auxdata destructors can run immediately on failure, so implementations must not use a pointer after giving it to SQLite with a destructor.
- Incorrect function flags are security-sensitive. Omitting `SQLITE_DIRECTONLY` from side-effecting or information-revealing functions may allow malicious schema objects to invoke application code. Marking a non-innocuous function as innocuous can bypass trusted-schema protections.
- Collation callbacks must implement a stable total ordering. Violating symmetry or transitivity makes SQLite behavior undefined and can corrupt query answers or indexes that depend on that collation.
- `sqlite3_create_collation_v2()` is an API exception: its destructor is not called if registration fails, so callers must clean up `pArg` themselves on error.
- Global directory variables are legacy, not thread-safe, and interact with pragmas that assume `sqlite3_malloc()` ownership. Directly assigning static or stack memory can later lead to invalid frees if the corresponding pragma is used.
- Commit, rollback, update, autovacuum, unlock-notify, and preupdate callbacks have non-reentrancy constraints. Calling back into SQLite in prohibited ways can deadlock, corrupt state, or produce undefined behavior.
- Shared cache is discouraged. Unlock-notify exists for shared-cache lock waits and includes deadlock detection, but callback timing can be immediate and the DROP TABLE/INDEX same-connection exception can cause retry loops.
- Extension loading is a direct code-loading surface. Enabling the SQL `load_extension()` function broadens exposure to SQL injection, so connection-specific C-only enabling is safer.
- Virtual table modules are ABI-sensitive. The `sqlite3_module` object must remain stable while registered, `sqlite3_index_info` fields added in later SQLite versions must not be used against older libraries, and invalid `orderByConsumed`, `omit`, `UNIQUE`, `DISTINCT`, or constraint-support claims can produce wrong query results or unsafe rollback behavior.
- Incremental BLOB writes cannot change blob size and are not automatically rolled back just because a handle later expires. Applications must reason about transaction boundaries and row modifications carefully.
- VFS registration with duplicate names or empty names is undefined. Unregistering the default VFS picks an arbitrary new default.
- Custom mutex and page-cache implementations sit below core invariants. Missing static mutex handling, non-threadsafe cache methods, incorrect pin/unpin semantics, or stale page rekey/truncate behavior can destabilize the entire library.
- `sqlite3_file_control()` can return `SQLITE_ERROR` for either an unknown database name or a VFS-level error, with no reliable distinction.
- `sqlite3_test_control()` and `SQLITE_TESTCTRL_*` are explicitly unstable and should not be used by applications.
- Status counters and scan-status values are conditional or approximate. Some high-water/current fields are undefined for specific opcodes, and scan status is only compiled with `SQLITE_ENABLE_STMT_SCANSTATUS`.
- WAL hooks and autocheckpointing occupy the same single callback slot. Installing one silently disables the other.
- Checkpoint modes differ materially in lock acquisition and busy-handler behavior. PASSIVE never invokes the busy handler; FULL/RESTART/TRUNCATE may block writers and wait for readers; all modes need the checkpoint lock and can return `SQLITE_BUSY`.
- `sqlite3_db_cacheflush()` intentionally does not set the connection error code/message, so callers must use the direct return code rather than later `sqlite3_errcode()` state.
- Preupdate value pointers are only valid until the callback returns, and old/new accessors are only valid for particular operation kinds. BLOB writes are reported through a special preupdate path that can appear as `SQLITE_DELETE` before new values are available.

## Test Signals

- SQLite's API documentation comments include requirement tags and method/destructor annotations that upstream tests often validate through documentation generation and API conformance checks.
- Unit and integration coverage for this header surface should exercise statement value extraction order, OOM during type conversion, pointer invalidation, reset/finalize return codes, and NULL/failure handling.
- Function tests should cover scalar/aggregate/window callback registration, destructor invocation on success/failure/overload/close, auxdata lifetime, subtype propagation, direct-only and innocuous restrictions, pointer passing, aggregate context allocation, and no-change/from-bind value flags.
- Collation tests should cover UTF-8/UTF-16 registrations, lazy collation-needed callbacks, deletion/replacement, v2 destructor asymmetry on failure, and equivalent ordering across encodings.
- Hook tests should verify commit veto rollback, rollback-hook omissions on close-time rollback, update-hook exclusions for system/WITHOUT ROWID/truncate/replace cases, autovacuum callback page counts, and callback non-reentrancy expectations.
- Extension tests should ensure loading is disabled by default, C-only enabling works independently from SQL `load_extension()`, auto-extension entry points run once per opened connection, and cancellation/reset works.
- Virtual table tests should cover the full `sqlite3_module` lifecycle, `xBestIndex` constraint mapping, `omit` behavior, order-by consumption, estimated rows/cost, unique scan rollback semantics, IN all-at-once handling, RHS literal extraction, collation lookup, distinct modes, no-change update optimization, conflict policy, direct-only/innocuous flags, all-schema read transactions, savepoints, and integrity callbacks.
- BLOB tests should cover row/table/column validation errors, read-only/write modes, indexed/PK/FK write restrictions, expiration after row modification, reopen failure abort state, offset bounds, close-time autocommit, and zeroblob workflows.
- VFS, mutex, and page-cache tests should cover duplicate/default VFS registration behavior, file-control core opcodes, app-defined mutex methods under debug assertions, page-cache create/fetch/unpin/rekey/truncate/destroy/shrink semantics, and memory pressure release hooks.
- Backup tests should cover destination transaction conflicts, step return codes, retryable `BUSY`/`LOCKED`, fatal IO/NOMEM/READONLY errors, source mutation restart, destination-handle exclusivity, shared-cache restrictions, remaining/pagecount updates, and finish behavior after incomplete backups.
- WAL tests should cover hook replacement by autocheckpoint, default autocheckpoint thresholds, all checkpoint modes, attached database handling, not-in-WAL outputs, busy-handler behavior, and truncation outputs.
- Instrumentation tests should cover process/db/statement status opcodes, unsupported opcode failures, high-water reset, scan-status build gating, `SQLITE_SCANSTAT_COMPLEX`, and cacheflush return behavior without connection error-state mutation.

## Unresolved Cross-Chunk References

- The tail of the pre-update hook declaration block continues after line 10675, including the final prototypes and the remainder of `sqlite3_preupdate_blobwrite()` behavior.
- Implementations for all APIs in this header chunk live in `sqlite3.c` and other portions of the amalgamation; this chunk documents ABI contracts rather than executable logic.
- Several referenced constants and APIs are declared outside this line range, including bind APIs, prepare/step APIs, `sqlite3_db_config()` options, VFS/file-control opcode structs, result codes, open flags, and `sqlite3_api_routines`.

### subset-b-009049: lines 10676-13775

# sources/storage-engines/wiredtiger/test/3rdparty/sqlite3/sqlite3.h lines 10676-13775

## Scope

This chunk is the end of the amalgamated SQLite public header embedded under WiredTiger's SQLite third-party test dependency. It begins in the optional pre-update hook declarations, covers low-level error reporting, WAL snapshot handles, serialize/deserialize APIs, WASI compile-time adjustments, and then appends the public extension headers that are folded into the amalgamation: `sqlite3rtree.h`, `sqlite3session.h`, and `fts5.h`.

The content is almost entirely API declarations, typedefs, flags, and public behavioral contracts. There is no implementation body here, but the comments define control-flow, ownership, state, persistence, and conflict-resolution semantics that consumers and the corresponding `sqlite3.c` implementation must honor.

## Purpose

- Expose optional pre-update hook accessors used by extensions such as the sessions module to inspect rows before mutation.
- Expose `sqlite3_system_errno()` so callers can retrieve the OS-level cause behind the most recent SQLite I/O/open failure on a database handle.
- Define the experimental WAL snapshot API used to capture, compare, reopen, recover, and free historical read snapshots in WAL-mode databases.
- Define database serialization and deserialization APIs for copying an attached schema to bytes or replacing an attached schema with an in-memory serialized image.
- Finish the main `sqlite3.h` C API block and add build-specific cleanup/adjustment macros, including undoing the floating-point integer hack and forcing WASI-safe defaults.
- Publish the RTree extension callback API for geometry and scored query functions used by virtual table `MATCH` predicates.
- Publish the sessions extension API for recording table changes, generating changesets/patchsets, iterating them, combining them, applying them with conflict handlers, rebasing local changesets, and using streaming variants for large inputs.
- Publish the FTS5 extension API for custom auxiliary functions and tokenizers, including versioned extension tables, phrase/instance access, tokenizer locale support, synonym support, and tokenizer/function registration.

## Important APIs, Types, And Functions

- Pre-update hook APIs are guarded by `SQLITE_ENABLE_PREUPDATE_HOOK`: `sqlite3_preupdate_hook()`, `sqlite3_preupdate_old()`, `sqlite3_preupdate_count()`, `sqlite3_preupdate_depth()`, `sqlite3_preupdate_new()`, and `sqlite3_preupdate_blobwrite()`.
- Error/snapshot/serialization declarations include `sqlite3_system_errno()`, opaque-layout `sqlite3_snapshot`, `sqlite3_snapshot_get()`, `sqlite3_snapshot_open()`, `sqlite3_snapshot_free()`, `sqlite3_snapshot_cmp()`, `sqlite3_snapshot_recover()`, `sqlite3_serialize()`, `sqlite3_deserialize()`, `SQLITE_SERIALIZE_NOCOPY`, `SQLITE_DESERIALIZE_FREEONCLOSE`, `SQLITE_DESERIALIZE_RESIZEABLE`, and `SQLITE_DESERIALIZE_READONLY`.
- RTree extension types and callbacks include `sqlite3_rtree_dbl`, `sqlite3_rtree_geometry_callback()`, `sqlite3_rtree_geometry`, `sqlite3_rtree_query_callback()`, `sqlite3_rtree_query_info`, and visibility constants `NOT_WITHIN`, `PARTLY_WITHIN`, and `FULLY_WITHIN`.
- Session object APIs include `sqlite3_session`, `sqlite3session_create()`, `sqlite3session_delete()`, `sqlite3session_object_config()`, `SQLITE_SESSION_OBJCONFIG_SIZE`, `SQLITE_SESSION_OBJCONFIG_ROWID`, `sqlite3session_enable()`, `sqlite3session_indirect()`, `sqlite3session_attach()`, `sqlite3session_table_filter()`, `sqlite3session_changeset()`, `sqlite3session_changeset_size()`, `sqlite3session_diff()`, `sqlite3session_patchset()`, `sqlite3session_isempty()`, and `sqlite3session_memory_used()`.
- Changeset iterator APIs include `sqlite3_changeset_iter`, `sqlite3changeset_start()`, `sqlite3changeset_start_v2()`, `SQLITE_CHANGESETSTART_INVERT`, `sqlite3changeset_next()`, `sqlite3changeset_op()`, `sqlite3changeset_pk()`, `sqlite3changeset_old()`, `sqlite3changeset_new()`, `sqlite3changeset_conflict()`, `sqlite3changeset_fk_conflicts()`, and `sqlite3changeset_finalize()`.
- Changeset transformation and grouping APIs include `sqlite3changeset_invert()`, `sqlite3changeset_concat()`, `sqlite3_changegroup`, `sqlite3changegroup_new()`, `sqlite3changegroup_schema()`, `sqlite3changegroup_add()`, `sqlite3changegroup_add_change()`, `sqlite3changegroup_output()`, and `sqlite3changegroup_delete()`.
- Apply/conflict APIs include `sqlite3changeset_apply()`, `sqlite3changeset_apply_v2()`, apply flags `SQLITE_CHANGESETAPPLY_NOSAVEPOINT`, `SQLITE_CHANGESETAPPLY_INVERT`, `SQLITE_CHANGESETAPPLY_IGNORENOOP`, and `SQLITE_CHANGESETAPPLY_FKNOACTION`, conflict classes `SQLITE_CHANGESET_DATA`, `SQLITE_CHANGESET_NOTFOUND`, `SQLITE_CHANGESET_CONFLICT`, `SQLITE_CHANGESET_CONSTRAINT`, and `SQLITE_CHANGESET_FOREIGN_KEY`, and conflict-handler return values `SQLITE_CHANGESET_OMIT`, `SQLITE_CHANGESET_REPLACE`, and `SQLITE_CHANGESET_ABORT`.
- Rebase APIs include `sqlite3_rebaser`, `sqlite3rebaser_create()`, `sqlite3rebaser_configure()`, `sqlite3rebaser_rebase()`, `sqlite3rebaser_delete()`, and `sqlite3rebaser_rebase_strm()`.
- Streaming session APIs include `_strm` equivalents for apply, apply_v2, concat, invert, start, start_v2, session changeset/patchset output, changegroup add/output, and rebaser rebase, plus `sqlite3session_config()` and `SQLITE_SESSION_CONFIG_STRMSIZE`.
- FTS5 extension types and callbacks include `Fts5ExtensionApi`, `Fts5Context`, `Fts5PhraseIter`, `fts5_extension_function`, `Fts5Tokenizer`, `fts5_tokenizer_v2`, legacy `fts5_tokenizer`, tokenization flags `FTS5_TOKENIZE_QUERY`, `FTS5_TOKENIZE_PREFIX`, `FTS5_TOKENIZE_DOCUMENT`, `FTS5_TOKENIZE_AUX`, token callback flag `FTS5_TOKEN_COLOCATED`, and registration table `fts5_api`.
- `Fts5ExtensionApi` version 4 exposes auxiliary-function helpers such as `xUserData`, `xColumnCount`, `xRowCount`, `xColumnTotalSize`, `xTokenize`, `xPhraseCount`, `xPhraseSize`, `xInstCount`, `xInst`, `xRowid`, `xColumnText`, `xColumnSize`, `xQueryPhrase`, `xSetAuxdata`, `xGetAuxdata`, phrase iterators, `xQueryToken`, `xInstToken`, `xColumnLocale`, and `xTokenize_v2`.

## Control Flow

The pre-update hook path is event driven by row changes in the VDBE/write path. Applications register one callback per connection with `sqlite3_preupdate_hook()`. During an INSERT, UPDATE, or DELETE, SQLite invokes the callback before the mutation and exposes row values through `sqlite3_preupdate_old()` and `sqlite3_preupdate_new()`. Nested changes from triggers or foreign-key actions are reflected through `sqlite3_preupdate_depth()`, while `sqlite3_preupdate_blobwrite()` identifies the column being modified by an incremental blob write or returns `-1` outside that special case.

Snapshot control flow is transaction-sensitive. `sqlite3_snapshot_get()` is called on a non-autocommit connection for a WAL-mode schema; it opens a read transaction if needed and returns an allocated snapshot handle. `sqlite3_snapshot_open()` then starts or adjusts a read transaction on another compatible handle so reads see the historical snapshot instead of the latest database state. `sqlite3_snapshot_cmp()` compares handles from the same WAL generation, `sqlite3_snapshot_recover()` scans a persistent WAL file so older transaction frames become openable, and `sqlite3_snapshot_free()` closes the ownership loop.

Serialization flow is direct data movement. `sqlite3_serialize()` returns either a freshly allocated copy of a schema's database image or, with `SQLITE_SERIALIZE_NOCOPY`, a pointer to SQLite's existing contiguous in-memory image when one exists. `sqlite3_deserialize()` disconnects the named schema and reopens it as an in-memory database backed by the caller-supplied byte buffer, with flags controlling ownership, resizing, and read-only behavior.

RTree extension flow starts at SQL registration. A connection registers a named geometry or query callback. Later, an RTree `MATCH` expression calls the registered function with either `sqlite3_rtree_geometry` or the richer `sqlite3_rtree_query_info`. The callback reads query parameters and candidate coordinates, sets `eWithin` to reject/accept/partially accept the object, and for query callbacks also sets `rScore` to influence traversal order.

Session flow starts by creating a `sqlite3_session` attached to a connection and database name. The caller configures it, attaches specific tables or installs a filter for lazy attachment, and then SQLite records changes while the session is enabled. Calling `sqlite3session_changeset()` or `sqlite3session_patchset()` materializes accumulated records by comparing recorded primary keys/original values with current table contents. Patchsets omit non-PK old values to shrink output and reduce conflict detection fidelity.

Changeset iteration is cursor based. `sqlite3changeset_start()` or `_v2()` creates an iterator over a changeset blob; each `sqlite3changeset_next()` advances to a change and returns `SQLITE_ROW`, `SQLITE_DONE`, or an error. The current entry is inspected through `sqlite3changeset_op()`, `sqlite3changeset_pk()`, `sqlite3changeset_old()`, and `sqlite3changeset_new()`. Iterators passed to apply conflict handlers additionally allow `sqlite3changeset_conflict()` or `sqlite3changeset_fk_conflicts()`. `sqlite3changeset_finalize()` returns any deferred iterator error.

Apply flow is conflict-directed. `sqlite3changeset_apply()` and `_v2()` filter tables, verify compatible target schemas, and attempt each DELETE, INSERT, or UPDATE under a savepoint unless `SQLITE_CHANGESETAPPLY_NOSAVEPOINT` is used. Data mismatches, missing rows, primary-key conflicts, constraint errors, and final foreign-key violations invoke the user conflict callback. The callback chooses omit, replace, or abort, with replace valid only for data/primary-key conflicts.

Changegroup flow merges multiple changesets or patchsets into one logical sequence. `sqlite3changegroup_add()` parses each input and combines changes by table and primary key. When the same row appears multiple times, the existing/new operation matrix collapses inserts, updates, and deletes into the final effect of applying inputs in order. `sqlite3changegroup_output()` writes the merged set; optional `sqlite3changegroup_schema()` lets the merge normalize compatible schemas against a live database schema.

Rebase flow starts while applying a remote changeset with `sqlite3changeset_apply_v2()`: if conflicts are resolved, SQLite can emit a rebase buffer. A `sqlite3_rebaser` is configured with one or more such buffers, then local changesets are transformed so they account for the earlier conflict decisions and should not require the same conflict resolution downstream.

Streaming APIs replace complete input/output buffers with callbacks. Input callbacks are repeatedly asked to fill a provided buffer and signal EOF by setting the byte count to zero. Output callbacks receive arbitrary positive-size chunks. For streaming iterators, input may be requested during later iterator calls, so an input error moves the iterator into a persistent error state.

FTS5 auxiliary-function flow is invoked from an FTS5 query. The function receives the `Fts5ExtensionApi`, an opaque `Fts5Context`, a normal SQLite result context, and SQL arguments. It uses the API table to inspect the current row, phrase structure, phrase matches, tokens, locale metadata, and auxiliary cached state, and then returns a scalar result through `sqlite3_context`.

FTS5 tokenizer flow is registration then per-use instantiation. The application registers a tokenizer by name through `fts5_api.xCreateTokenizer_v2()` or the legacy method. During `CREATE VIRTUAL TABLE`, FTS5 calls `xCreate()` with tokenizer arguments, later calls `xTokenize()` for document, query, prefix-query, or auxiliary tokenization, and finally calls `xDelete()` once per created tokenizer instance. Tokens are returned through the supplied callback in input order; colocated tokens represent synonyms at the same position.

## State And Persistence Behavior

`sqlite3_snapshot` is an opaque 48-byte public struct whose contents encode a WAL snapshot identity. Snapshot handles are heap objects returned by SQLite and must be freed with `sqlite3_snapshot_free()`. Their validity depends on WAL lifecycle: checkpoints can make old snapshots unopenable, and deleting/recreating the WAL file makes comparisons involving older handles undefined.

Serialized database buffers have explicit ownership rules. A normal `sqlite3_serialize()` result is allocated by SQLite and owned by the caller until freed with `sqlite3_free()`. A `SQLITE_SERIALIZE_NOCOPY` result remains SQLite-owned, must not be modified, and is only stable until the next write on that connection or connection close. For `sqlite3_deserialize()`, the buffer must remain valid until close unless `SQLITE_DESERIALIZE_FREEONCLOSE` transfers ownership to SQLite; `SQLITE_DESERIALIZE_RESIZEABLE` permits `sqlite3_realloc64()` growth and is meaningful only with SQLite ownership.

Deserialization changes persistent behavior by replacing a schema connection with an in-memory image. It does not support `temp`, fails if the target schema is in a read transaction or backup, and should not be used with WAL-mode serialized images unless the header is adjusted to rollback mode. Writes can grow only to `szBuf` unless the buffer is resizable.

RTree callback state is partly per-registration and partly per-callback. `pContext` is copied from registration, `aParam`/`apSqlParam` expose SQL parameters, `pUser` can hold callback-managed state, and `xDelUser` gives SQLite a cleanup hook. Query callbacks also receive traversal state such as node coordinates, queue counts, level, rowid, parent score, and parent containment.

Session objects persist an in-memory record of first-observed row changes by primary key. They record enough data to later compare against current table contents and produce net changes. Tables without explicit primary keys are ignored unless `SQLITE_SESSION_OBJCONFIG_ROWID` is enabled before any table attachment; `sqlite_stat1` is a documented special case treated as if `(tbl,idx)` were its key with a zero-length blob representing NULL `idx` values in changeset accessors.

Session state includes enabled/disabled and indirect flags. Disabled periods do not record new first-touch records, but final changeset construction still compares earlier records against current contents, so changes made while disabled can influence the net result for a row already recorded. Indirect status is merged across multiple changes to the same row: a row is indirect only if all contributing operations are indirect.

Changeset and patchset blobs are binary state transfer formats. Changesets store old and new values sufficient for data-conflict detection and inversion. Patchsets reduce stored old values, cannot be inverted with `sqlite3changeset_invert()`, and do not report `SQLITE_CHANGESET_DATA` conflicts because the old non-PK data is absent.

Apply operations persist modifications to the target database if committed. By default, all changes are enclosed in a savepoint and rolled back on errors or abort decisions. With `SQLITE_CHANGESETAPPLY_NOSAVEPOINT`, the caller is responsible for transaction boundaries and partial effects. Foreign-key handling may emit a final `SQLITE_CHANGESET_FOREIGN_KEY` callback if violations remain.

Changegroups persist merged changes in memory until deleted. Their state becomes undefined after an error from `sqlite3changegroup_add()` or a schema mismatch, so callers cannot rely on partial merge contents after failure. Output buffers are SQLite allocations owned by the caller.

FTS5 auxiliary data is scoped to an extension function and MATCH query. `xSetAuxdata()` replaces any previous pointer and invokes its destructor; the destructor is also called when the FTS5 query finishes. `xGetAuxdata(..., bClear=1)` clears without invoking the destructor, transferring cleanup responsibility to the function.

FTS5 tokenization affects persistent full-text indexes during document insert/delete tokenization. Synonym strategy changes index size and query behavior: mapping synonyms to one canonical token is space-efficient, adding synonyms to the document index supports prefix matching at a storage cost, and expanding query tokens costs CPU without changing index size.

## Dependencies And Integration Points

- The pre-update hook API depends on SQLite being compiled with `SQLITE_ENABLE_PREUPDATE_HOOK`. The session module depends on it and reserves the connection pre-update hook, so application pre-update hooks and session objects on the same handle are mutually incompatible by contract.
- Snapshot APIs depend on `SQLITE_ENABLE_SNAPSHOT`, WAL mode, open transactions, pager/checkpointer state, and connection knowledge that a schema is in WAL mode. The docs explicitly suggest running a pragma on a new connection to force I/O before opening snapshots.
- Serialization APIs are omitted under `SQLITE_OMIT_DESERIALIZE` and integrate with SQLite allocation APIs, backup semantics, in-memory database backing stores, pager schema attachment, and database header format bytes.
- WASI integration changes default feature availability by omitting loadable extensions and forcing `SQLITE_THREADSAFE` to 0 if the embedding build has not already specified otherwise.
- RTree callbacks integrate with the RTree virtual table module, SQL `MATCH` expressions, `sqlite3_value` parameter handling, and optional integer-only coordinate builds through `SQLITE_RTREE_INT_ONLY`.
- Sessions integrate with SQLite schema introspection, primary-key definitions, pre-update hooks, trigger/foreign-key action depth, `sqlite_stat1`, `sqlite3_free()` allocation ownership, conflict callbacks, `sqlite3_log()` warnings, savepoints, foreign-key enforcement, and streaming callback contracts.
- Changeset apply integrates with live target schemas. A compatible table must share the recorded table name, have at least the recorded column count, and have primary keys in the same positions. Missing incompatible tables are skipped with `SQLITE_SCHEMA` warnings rather than hard failure.
- Rebase integrates tightly with `sqlite3changeset_apply_v2()` because rebase buffers encode conflict decisions observed while applying remote changes.
- FTS5 extension APIs integrate with virtual-table function overloading (`xFindFunction`), FTS5 query execution, tokenizer implementations, locale-aware tokenization, `fts5_locale()`, `fts5_insttoken()`, table options such as `detail`, `content`, `columnsize`, `tokendata`, and `insttoken`, and SQLite scalar-function result/error reporting through `sqlite3_context`.

## Risks And Edge Cases

- Most APIs in this chunk are compile-option gated. Consumers must not assume snapshot, pre-update, deserialize, session, RTree, or FTS5 declarations imply usable runtime support in every SQLite build.
- Snapshot operations are easy to misuse because they require WAL mode, a non-autocommit handle, no write transaction on the schema, and at least one transaction in the current WAL file. Existing read transactions weaken invalidation guarantees for the returned snapshot handle.
- `sqlite3_snapshot_open()` has nuanced failure semantics. For `SQLITE_ERROR`, `SQLITE_BUSY`, and `SQLITE_ERROR_SNAPSHOT`, an existing read transaction remains on the same snapshot, but other errors can leave its state undefined.
- Snapshot comparisons are undefined across different database files or across WAL lifetimes. Any test or replication logic comparing stale snapshot handles can silently make invalid ordering decisions.
- `sqlite3_serialize(SQLITE_SERIALIZE_NOCOPY)` returns borrowed immutable memory. Treating it like an owned or writable buffer risks memory corruption or stale reads after the next write.
- `sqlite3_deserialize()` ownership flags are sharp: on failure, `SQLITE_DESERIALIZE_FREEONCLOSE` still causes SQLite to free the input buffer before returning. Callers must avoid double-freeing it.
- Deserializing a WAL-mode image produces later `SQLITE_CANTOPEN` behavior unless callers rewrite file-format bytes 18 and 19 to rollback-mode values before use.
- RTree callback structures expose raw pointers and require callbacks to set output fields correctly. Forgetting to set `eWithin` or `rScore`, retaining `aCoord`/`aParam` beyond the callback, or mishandling `xDelUser` can produce wrong search results or lifetime bugs.
- Session capture ignores rows with NULL primary-key columns, which can make changes disappear or appear as only INSERT/DELETE when NULL-ness changes. Enabling rowid capture after attaching a table is misuse.
- `sqlite3session_diff()` requires compatible table definitions. The comments describe row differences by primary key and current contents, so schema drift and missing attached databases surface as `SQLITE_SCHEMA` or error strings rather than normal changes.
- Changeset iterator accessors are state-dependent. Calling `old()` on INSERT, `new()` on DELETE, `conflict()` outside suitable conflict callbacks, or `finalize()` on an apply-owned iterator is misuse.
- `sqlite3changeset_invert()` explicitly assumes a valid input changeset; invalid or patchset input can produce undefined results or `SQLITE_CORRUPT`.
- Changegroup state becomes undefined after errors. Robust callers must delete and recreate a group rather than retrying on the same handle after corrupt input, OOM, or schema mismatch.
- Apply conflict handlers must return only the allowed constants. Illegal returns or `REPLACE` for unsupported conflict classes roll back and return `SQLITE_MISUSE`.
- `SQLITE_CHANGESETAPPLY_IGNORENOOP` suppresses conflict callbacks for no-op situations; applications that audit every skipped change may lose visibility when this flag is used.
- `SQLITE_CHANGESETAPPLY_FKNOACTION` deliberately changes effective foreign-key action behavior during apply, which can differ from normal database operations using cascade, restrict, set-null, or set-default actions.
- Streaming callbacks must handle arbitrary chunking and error propagation. For `start_strm`, input may be requested after construction, so failures appear during later iteration/finalization rather than at start.
- `sqlite3session_config()` is not threadsafe and is undefined after any session object exists or while another thread is in session APIs.
- FTS5 `Fts5ExtensionApi` is versioned. Extension code must check `iVersion` before calling newer members such as `xQueryToken`, `xInstToken`, `xColumnLocale`, or `xTokenize_v2`.
- FTS5 APIs can be slow or empty depending on table options. `xInst`, `xInstCount`, phrase iterators, and token access are expensive or unavailable with `detail=none`, `detail=column`, contentless tables, or prefix-token lookups without `insttoken` support.
- FTS5 tokenizer implementations must define all methods, return tokens in order, respect callback error returns, and avoid emitting `FTS5_TOKEN_COLOCATED` for the first token. Locale buffers are not nul-terminated.
- Providing synonyms during both document and query tokenization is not incorrect but is inefficient and can bloat indexes or query work unexpectedly.

## Test Signals

- Pre-update tests should cover INSERT, UPDATE, DELETE, trigger/foreign-key nested depth, incremental blob writes, old/new value access by column, and coexistence failure/undefined behavior boundaries with sessions.
- Snapshot tests should cover success in WAL mode with a non-autocommit read transaction, failure in rollback mode, failure with no WAL transaction yet, checkpoint invalidation yielding `SQLITE_ERROR_SNAPSHOT`, recovery from persistent WAL files, compare ordering, compare undefined cases avoided by test design, and required freeing.
- Serialization tests should cover on-disk, in-memory, and TEMP schemas; `NOCOPY` success/failure and borrowed-buffer stability; OOM returning NULL; deserialize busy cases with open reads/backups; read-only buffers; fixed-size growth failure; resizable/free-on-close ownership; and WAL-header rejection/workaround.
- RTree tests should register geometry and query callbacks, verify SQL parameter propagation, check coordinate counts and rowids, exercise `NOT_WITHIN`/`PARTLY_WITHIN`/`FULLY_WITHIN`, verify score-based ordering/pruning, and run both floating-point and `SQLITE_RTREE_INT_ONLY` builds where applicable.
- Session capture tests should cover attach-by-name, attach-all with table filter, missing tables, tables without primary keys, rowid-object config, `sqlite_stat1` special conversion, enabled/disabled periods, indirect changes from triggers, NULL primary-key behavior, memory accounting, and upper-bound changeset size config.
- Changeset generation tests should cover insert-then-delete cancellation, delete-then-insert collapse to update, primary-key changes represented as delete plus insert, patchset omissions, table grouping/order, `sqlite3session_isempty()` false positives for net-empty changes, and caller ownership of generated buffers.
- Iterator tests should cover empty, valid, corrupt, and inverted-start changesets; accessor misuse; primary-key masks; old/new NULL returns for unchanged UPDATE columns; conflict-row access inside apply callbacks; foreign-key conflict counts; and finalize returning deferred errors.
- Changegroup tests should exercise every operation-combination row in the documented INSERT/UPDATE/DELETE merge matrix, mixed changeset/patchset rejection, schema-normalized column defaults, adding one change from an iterator, output ordering, corrupt input, and state discard after errors.
- Apply tests should cover target schema compatibility, filtered tables, skipped missing tables with log warnings, DELETE data conflicts, UPDATE data conflicts, INSERT primary-key conflicts, constraint conflicts, missing-row conflicts, foreign-key final conflicts, each handler return action, illegal handler returns, savepoint rollback, no-savepoint partial application, invert mode, ignore-noop mode, and foreign-key no-action mode.
- Rebase tests should cover local INSERT/DELETE/UPDATE rebased against remote INSERT/UPDATE/DELETE conflicts with OMIT and REPLACE resolutions, multiple remote rebase buffers in order, per-field rebasing for multiple UPDATE conflicts, and streaming rebase equivalence.
- Streaming tests should compare `_strm` and non-streaming outputs for apply, concat, invert, start, session changeset, patchset, changegroup add/output, and rebase; inject short reads, zero-length EOF, arbitrary output chunking, callback errors, and `SQLITE_SESSION_CONFIG_STRMSIZE` changes.
- FTS5 auxiliary-function tests should register custom functions, verify user data, row/column/token counts, column text and size, phrase count/size, instance iteration, phrase-column iteration, query-token and instance-token access, auxdata destructor behavior, locale retrieval, and behavior under `detail=none`, `detail=column`, contentless, `tokendata`, and prefix queries.
- FTS5 tokenizer tests should register legacy and v2 tokenizers, verify create/delete lifetimes, document/query/prefix/aux flags, locale argument handling, non-nul-terminated input and locale buffers, callback error propagation, synonym colocated tokens, prefix query behavior across synonym strategies, and API version checks through `fts5_api`.
