# Research: sources/storage-engines/sqlite/src/sqlite.h.in

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008788`: lines 1-5232, `Docs/researches/chunks/subset-b-008788_research.md`
- `subset-b-008789`: lines 5233-10716, `Docs/researches/chunks/subset-b-008789_research.md`
- `subset-b-008790`: lines 10717-11389, `Docs/researches/chunks/subset-b-008790_research.md`

## Chunk Research

### subset-b-008788: lines 1-5232

# sources/storage-engines/sqlite/src/sqlite.h.in lines 1-5232

## Chunk Scope

This chunk covers the first 5,232 lines of `sources/storage-engines/sqlite/src/sqlite.h.in`, the template header used by SQLite's build to produce the public `sqlite3.h` API. It begins with linkage/calling-convention macros and version placeholders, then defines the core C API up through prepared-statement binding and result-column metadata. The range ends mid-comment in the "Declared Datatype Of A Query Result" section, so the actual `sqlite3_column_decltype()` declarations and any later column/value/step/finalize APIs are cross-chunk continuations.

## Purpose

`sqlite.h.in` is the authoritative public API contract for client programs embedding or linking SQLite. The comments are not incidental: they drive official C API documentation and specify ownership, threading, lifetime, persistence, and compatibility behavior that external code depends on. The build system substitutes version/source-control placeholders such as `--VERS--`, `--VERSION-NUMBER--`, and `--SOURCE-ID--` and emits the installed header as `sqlite3.h`.

Within this chunk the header exposes:

- Process/library metadata and diagnostics.
- Opaque handles for connections, statements, values, contexts, mutexes, VFS files, VFS objects, and extension thunks.
- Database connection construction/destruction, one-shot execution, error reporting, busy/progress/trace/authorizer hooks, connection configuration, and statement preparation.
- VFS and file I/O interfaces used by SQLite's pager/WAL/journal layers to persist database state.
- Core result, open, synchronization, locking, file-control, configuration, authorizer, trace, prepare, bind, and column metadata constants.

## Public Surface In This Chunk

### Header/linkage and version APIs

The opening block guards `SQLITE3_H`, provides C++ `extern "C"` linkage, and defines overrideable interface macros: `SQLITE_EXTERN`, `SQLITE_API`, `SQLITE_CDECL`, `SQLITE_APICALL`, `SQLITE_STDCALL`, `SQLITE_CALLBACK`, and `SQLITE_SYSAPI`. `SQLITE_DEPRECATED` and `SQLITE_EXPERIMENTAL` are retained as no-op markers to preserve source compatibility without forcing compiler warnings.

Version state is split between compile-time macros and runtime functions:

- `SQLITE_VERSION`, `SQLITE_VERSION_NUMBER`, `SQLITE_SOURCE_ID`, `SQLITE_SCM_BRANCH`, `SQLITE_SCM_TAGS`, and `SQLITE_SCM_DATETIME` are generated at build time.
- `sqlite3_version[]`, `sqlite3_libversion()`, `sqlite3_sourceid()`, and `sqlite3_libversion_number()` expose the linked library's identity.
- `sqlite3_compileoption_used()` and `sqlite3_compileoption_get()` are omitted or stubbed when `SQLITE_OMIT_COMPILEOPTION_DIAGS` is set.
- `sqlite3_threadsafe()` reports compile-time mutex support only, not runtime mode changes made with `sqlite3_config()`.

Risk signal: callers commonly assert that runtime and header versions match. Mismatched `sqlite3.h` and library binaries can silently alter ABI assumptions, result-code availability, and feature macros.

### Opaque handles and scalar types

The chunk introduces opaque `typedef struct` handles for `sqlite3`, `sqlite3_stmt`, `sqlite3_value`, `sqlite3_context`, `sqlite3_mutex`, `sqlite3_api_routines`, `sqlite3_vfs`, and `sqlite3_file`. It defines cross-platform signed/unsigned 64-bit integer aliases `sqlite_int64`, `sqlite_uint64`, `sqlite3_int64`, and `sqlite3_uint64`, with `SQLITE_INT64_TYPE`/`SQLITE_UINT64_TYPE` overrides and compiler-specific fallbacks. `SQLITE_OMIT_FLOATING_POINT` can replace `double` with `sqlite3_int64`.

These declarations keep object layouts private except for extension interfaces that must be subclassed or filled by embedders, especially `sqlite3_file`, `sqlite3_io_methods`, `sqlite3_vfs`, and `sqlite3_mem_methods`.

### Connection lifecycle and one-step execution

`sqlite3_close()` and `sqlite3_close_v2()` are destructors for `sqlite3` connections. The older close API returns `SQLITE_BUSY` if statements, BLOB handles, or backups remain open; `sqlite3_close_v2()` marks the connection as a zombie and defers deallocation until dependent objects are released. Any open transaction is automatically rolled back when the connection is destroyed.

`sqlite3_exec()` is the convenience wrapper around prepare/step/finalize. It accepts one or more UTF-8 SQL statements, invokes an optional row callback with result text and column names, stops on the first SQL error or callback abort, and returns an error message allocated by `sqlite3_malloc()` when requested. The caller must free that error string with `sqlite3_free()`.

Risk signals:

- Closing order is observable. `sqlite3_close_v2()` is suitable for garbage-collected host bindings, but wrappers must avoid using the zombie connection.
- `sqlite3_exec()` callbacks receive transient pointers; retaining them after callback return is invalid.
- If a callback returns non-zero, execution aborts with `SQLITE_ABORT` and remaining statements are skipped.

### Result, extended result, open, lock, sync, and I/O capability constants

The header defines primary result codes (`SQLITE_OK`, `SQLITE_ERROR`, `SQLITE_BUSY`, `SQLITE_LOCKED`, `SQLITE_ROW`, `SQLITE_DONE`, etc.) and a large matrix of extended result codes created by OR-ing primary codes with subcodes shifted by 8 bits. Important families include `SQLITE_IOERR_*`, `SQLITE_LOCKED_*`, `SQLITE_BUSY_*`, `SQLITE_CANTOPEN_*`, `SQLITE_CORRUPT_*`, `SQLITE_READONLY_*`, `SQLITE_CONSTRAINT_*`, `SQLITE_NOTICE_*`, and `SQLITE_WARNING_AUTOINDEX`.

Open flags are shared by `sqlite3_open_v2()` and VFS `xOpen()`, but the header explicitly separates flags legal for application opens from flags reserved for the VFS layer. Application-facing flags include `SQLITE_OPEN_READONLY`, `SQLITE_OPEN_READWRITE`, `SQLITE_OPEN_CREATE`, `SQLITE_OPEN_URI`, `SQLITE_OPEN_MEMORY`, `SQLITE_OPEN_NOMUTEX`, `SQLITE_OPEN_FULLMUTEX`, `SQLITE_OPEN_SHAREDCACHE`, `SQLITE_OPEN_PRIVATECACHE`, `SQLITE_OPEN_NOFOLLOW`, and `SQLITE_OPEN_EXRESCODE`. VFS object-type flags include `SQLITE_OPEN_MAIN_DB`, journal/temp/subjournal/super-journal flags, and `SQLITE_OPEN_WAL`.

The chunk also defines:

- Storage capability bits such as `SQLITE_IOCAP_ATOMIC*`, `SQLITE_IOCAP_SAFE_APPEND`, `SQLITE_IOCAP_SEQUENTIAL`, `SQLITE_IOCAP_POWERSAFE_OVERWRITE`, `SQLITE_IOCAP_IMMUTABLE`, `SQLITE_IOCAP_BATCH_ATOMIC`, and `SQLITE_IOCAP_SUBPAGE_READ`.
- Lock levels from `SQLITE_LOCK_NONE` to `SQLITE_LOCK_EXCLUSIVE`.
- Sync flags `SQLITE_SYNC_NORMAL`, `SQLITE_SYNC_FULL`, and `SQLITE_SYNC_DATAONLY`.

Persistence risk: incorrect VFS capability reporting can corrupt databases. For example, failing to zero-fill short reads, overstating atomicity, or incorrectly disabling locks changes pager and WAL safety assumptions.

### VFS file methods and file-control opcodes

`struct sqlite3_file` contains only `pMethods`, allowing each VFS to subclass it with platform-specific file state. `struct sqlite3_io_methods` is the per-file method table:

- Version 1 methods: `xClose`, `xRead`, `xWrite`, `xTruncate`, `xSync`, `xFileSize`, `xLock`, `xUnlock`, `xCheckReservedLock`, `xFileControl`, `xSectorSize`, and `xDeviceCharacteristics`.
- Version 2 WAL/shared-memory methods: `xShmMap`, `xShmLock`, `xShmBarrier`, and `xShmUnmap`.
- Version 3 memory-map methods: `xFetch` and `xUnfetch`.

The file-control section documents opcodes through `SQLITE_FCNTL_FILESTAT` and legacy aliases. It covers lock inspection, size hints and size limits, chunk sizing, file/journal pointers, sync and commit-phase notifications, Windows AV retry policy, persistent WAL, powersafe-overwrite toggling, VFS stack names/pointers, pragma interception, busy-handler access for custom VFSes, temp filename generation, mmap size control, tracing, file-moved detection, native handle access, null I/O, WAL blocking, zipvfs/RBU hooks, batch atomic write begin/commit/rollback, lock timeouts, WAL checkpoint start/done signals, external reader detection, checksum VFS support, cache reset, and file statistics.

State/persistence behavior:

- VFS `xOpen()` must set `sqlite3_file.pMethods` to either a valid method table or NULL even on failure; otherwise SQLite may call `xClose()` after a failed open.
- Journal and WAL file-control opcodes are part of transaction ordering and checkpoint coordination. Applications are warned not to issue internal opcodes such as `SQLITE_FCNTL_SYNC`, `SQLITE_FCNTL_COMMIT_PHASETWO`, or `SQLITE_FCNTL_WAL_BLOCK`.
- `SQLITE_FCNTL_PERSIST_WAL` changes whether WAL and shared-memory files remain after the last connection closes.
- Batch atomic write opcodes constrain which VFS calls SQLite may make between begin and commit/rollback.

Integration points: custom VFS implementations, VFS shims, WAL subsystem, pager, rollback journal, checkpoint code, `sqlite3_file_control()`, PRAGMA handling, zipvfs, RBU, checksum VFS, and diagnostic tooling.

### VFS object and filename helpers

`sqlite3_filename` is a `const char *` with SQLite-owned metadata attached for VFS use. `struct sqlite3_vfs` defines the registered OS interface:

- Identity/chain fields: `iVersion`, `szOsFile`, `mxPathname`, `pNext`, `zName`, `pAppData`.
- File and path methods: `xOpen`, `xDelete`, `xAccess`, `xFullPathname`.
- Dynamic loading: `xDlOpen`, `xDlError`, `xDlSym`, `xDlClose`.
- Misc OS services: `xRandomness`, `xSleep`, `xCurrentTime`, `xGetLastError`, `xCurrentTimeInt64`.
- Version 3 optional syscall override/testing hooks: `xSetSystemCall`, `xGetSystemCall`, `xNextSystemCall`.

VFS access flags (`SQLITE_ACCESS_EXISTS`, `SQLITE_ACCESS_READWRITE`, `SQLITE_ACCESS_READ`) and shared-memory lock flags (`SQLITE_SHM_UNLOCK`, `SQLITE_SHM_LOCK`, `SQLITE_SHM_SHARED`, `SQLITE_SHM_EXCLUSIVE`, `SQLITE_SHM_NLOCK`) define exact method arguments for lock coordination.

Filename helper APIs in the later open section include `sqlite3_uri_parameter()`, `sqlite3_uri_boolean()`, `sqlite3_uri_int64()`, `sqlite3_uri_key()`, `sqlite3_filename_database()`, `sqlite3_filename_journal()`, `sqlite3_filename_wal()`, `sqlite3_database_file_object()`, `sqlite3_create_filename()`, and `sqlite3_free_filename()`. These are primarily for VFS and VFS shim implementations. Misusing arbitrary strings as `sqlite3_filename` values is undefined and likely a memory error.

### Library initialization and global configuration

`sqlite3_initialize()`, `sqlite3_shutdown()`, `sqlite3_os_init()`, and `sqlite3_os_end()` manage process-level SQLite state. Normal applications rely on auto-initialization, but `SQLITE_OMIT_AUTOINIT` builds require explicit initialization. `sqlite3_shutdown()` is not threadsafe and requires all connections/resources to be closed first.

`sqlite3_config()` changes global configuration, mostly before initialization or after shutdown. "Anytime" options documented in this chunk are limited and version-dependent. `sqlite3_db_config()` configures a single `sqlite3` connection.

`struct sqlite3_mem_methods` defines an embeddable allocator with `xMalloc`, `xFree`, `xRealloc`, `xSize`, `xRoundup`, `xInit`, `xShutdown`, and `pAppData`. The surrounding configuration constants include:

- Threading modes: `SQLITE_CONFIG_SINGLETHREAD`, `MULTITHREAD`, `SERIALIZED`.
- Memory/allocator/page-cache controls: `MALLOC`, `GETMALLOC`, `PAGECACHE`, `HEAP`, `MEMSTATUS`, `PCACHE2`, `GETPCACHE2`, `PCACHE_HDRSZ`, `SMALL_MALLOC`, obsolete `SCRATCH`, `PCACHE`, and `GETPCACHE`.
- Mutex controls: `SQLITE_CONFIG_MUTEX`, `GETMUTEX`.
- Diagnostics/hooks: `SQLITE_CONFIG_LOG`, `SQLITE_CONFIG_SQLLOG`.
- URI/default behavior and optimizer/sorter/storage knobs: `URI`, `COVERING_INDEX_SCAN`, `MMAP_SIZE`, `WIN32_HEAPSIZE`, `PMASZ`, `STMTJRNL_SPILL`, `SORTERREF_SIZE`, `MEMDB_MAXSIZE`, `ROWID_IN_VIEW`.

Risks:

- Most `sqlite3_config()` options return `SQLITE_MISUSE` if called while initialized. Embedders need a clear startup phase.
- Custom allocators must satisfy SQLite's size, roundup, initialization, and thread-safety expectations or failures can manifest as memory corruption rather than clean errors.
- `SQLITE_CONFIG_LOG` callbacks are not reentrant and must not call SQLite APIs.

### Connection configuration constants

`SQLITE_DBCONFIG_*` options define connection-local switches for security, compatibility, planner behavior, attachment behavior, comments, loadable extension access, and display precision. This chunk includes constants from `SQLITE_DBCONFIG_MAINDBNAME` through `SQLITE_DBCONFIG_FP_DIGITS`, with `SQLITE_DBCONFIG_MAX` currently equal to the FP digits value.

Important behavioral groups:

- Security hardening: `DEFENSIVE`, `TRUSTED_SCHEMA`, `WRITABLE_SCHEMA`, `ENABLE_LOAD_EXTENSION`, `ENABLE_FTS3_TOKENIZER`, `ENABLE_ATTACH_CREATE`, `ENABLE_ATTACH_WRITE`, `ENABLE_COMMENTS`.
- SQL feature gates and compatibility: `ENABLE_FKEY`, `ENABLE_TRIGGER`, `ENABLE_VIEW`, `LEGACY_ALTER_TABLE`, `DQS_DML`, `DQS_DDL`, `LEGACY_FILE_FORMAT`, `RESET_DATABASE`.
- Planner/diagnostic behavior: `ENABLE_QPSG`, `TRIGGER_EQP`, `STMT_SCANSTATUS`, `REVERSE_SCANORDER`, `FP_DIGITS`.
- Storage lifecycle: `NO_CKPT_ON_CLOSE` affects WAL close-time checkpoint/delete behavior.
- Memory: `LOOKASIDE` sets per-connection lookaside memory.
- Naming: `MAINDBNAME` changes the schema name for the main database without copying the input string.

Risk signals:

- `RESET_DATABASE` is deliberately multi-step because it destructively resets even corrupt databases and abandons virtual tables without `xDestroy()`.
- `TRUSTED_SCHEMA` defaults to legacy-friendly behavior but should be disabled for untrusted databases to prevent unsafe functions/virtual tables inside schema objects.
- `MAINDBNAME` requires the caller-provided string to remain valid until close.

### Runtime state APIs on connections

This chunk declares connection methods for extended result codes, rowid/change counters, interruption, completeness checks, busy handling, setlk timeouts, convenience query tables, formatting, memory, randomness, authorizers, tracing, progress handlers, opening, URI filename inspection, error reporting, and manual error setting.

Notable APIs and behavior:

- `sqlite3_extended_result_codes()` toggles detailed error reporting per connection.
- `sqlite3_last_insert_rowid()` and `sqlite3_set_last_insert_rowid()` track or override the most recent successful insert into a rowid table on a connection. Trigger execution temporarily changes the observed value; rolled-back inserts still count as successful for this API.
- `sqlite3_changes()`/`sqlite3_changes64()` report rows changed by the most recently completed direct INSERT/UPDATE/DELETE; `sqlite3_total_changes()`/`sqlite3_total_changes64()` report cumulative direct plus trigger changes since open. Concurrent use of the same connection makes these values unpredictable.
- `sqlite3_interrupt()` and `sqlite3_is_interrupted()` coordinate cancellation across threads, with interrupted write operations inside explicit transactions causing transaction rollback.
- `sqlite3_complete()`, `sqlite3_complete16()`, and `sqlite3_incomplete()` check SQL text completeness, not SQL validity.
- `sqlite3_busy_handler()` installs one non-reentrant busy callback per connection; `sqlite3_busy_timeout()` replaces any existing busy handler.
- `sqlite3_setlk_timeout()` is only effective in `SQLITE_ENABLE_SETLK_TIMEOUT` builds and VFSes that support blocking locks.
- `sqlite3_get_table()` and `sqlite3_free_table()` provide a legacy/convenience full-result materialization path; returned tables must be released by the matching free routine.
- `sqlite3_mprintf()`, `sqlite3_vmprintf()`, `sqlite3_snprintf()`, and `sqlite3_vsnprintf()` provide SQLite's formatting dialect and allocator ownership rules.
- `sqlite3_malloc()`, `sqlite3_malloc64()`, `sqlite3_realloc()`, `sqlite3_realloc64()`, `sqlite3_free()`, and `sqlite3_msize()` expose SQLite's allocator; `sqlite3_memory_used()` and `sqlite3_memory_highwater()` expose allocator statistics when enabled.
- `sqlite3_randomness()` exposes the same PRNG used by random rowid selection and SQL random functions, seeding from the default VFS when needed.

### Authorization, tracing, and progress callbacks

`sqlite3_set_authorizer()` installs a compile-time authorization callback invoked during prepare/reprepare. Return values are `SQLITE_OK`, `SQLITE_DENY`, or `SQLITE_IGNORE`; action codes cover schema creation/deletion, table reads/writes, pragma, transaction, attach/detach, virtual table creation/drop, function calls, savepoints, and recursive trigger/view activity.

Security integration: the authorizer is relevant when preparing SQL from untrusted sources and should be paired with `sqlite3_limit()` and storage-size limits for defense in depth. It is not a runtime row-level security hook; it fires during preparation and can fire again if `sqlite3_step()` triggers automatic reprepare.

Tracing APIs include deprecated `sqlite3_trace()`/`sqlite3_profile()` and replacement `sqlite3_trace_v2()` with event masks `SQLITE_TRACE_STMT`, `SQLITE_TRACE_PROFILE`, `SQLITE_TRACE_ROW`, and `SQLITE_TRACE_CLOSE`. A connection can have at most one trace callback.

`sqlite3_progress_handler()` installs one progress callback per connection, invoked during long-running prepare/step work. Returning non-zero interrupts the operation. The callback must not modify the invoking connection.

Risk signals: authorizer, busy, trace, log, and progress callbacks have strict reentrancy limits. Wrappers should document which callbacks may call back into SQLite and should serialize callback state if connections are shared across threads.

### Opening databases and URI behavior

`sqlite3_open()`, `sqlite3_open16()`, and `sqlite3_open_v2()` construct database connections. `sqlite3_open()` and `sqlite3_open_v2()` take UTF-8 filenames; `sqlite3_open16()` takes native-endian UTF-16. Even failed opens usually return a connection handle that must be closed, except allocation failure can set `*ppDb` to NULL.

`sqlite3_open_v2()` requires one of three base access modes: read-only, read-write existing, or read-write/create. It accepts optional flags for URI interpretation, in-memory databases, mutex mode, shared/private cache, extended result-code mode on open, and no-follow symlink protection. The VFS name parameter can select a custom registered VFS.

Special filenames and URI parameters affect persistence:

- `":memory:"` creates a private in-memory database that disappears at close.
- An empty filename creates a private temporary on-disk database deleted at close.
- URI parameter `mode` can request `ro`, `rw`, `rwc`, or `memory`.
- `cache` selects shared/private cache.
- `vfs` selects a VFS by name.
- `psow` provides powersafe-overwrite metadata.
- `nolock=1` disables rollback-mode file locking and can corrupt databases if multiple writers exist.
- `immutable=1` disables locking/change detection and opens read-only under the assumption the file cannot change; using it on a changing file can produce incorrect results or `SQLITE_CORRUPT`.

### Error reporting

`sqlite3_errcode()`, `sqlite3_extended_errcode()`, `sqlite3_errmsg()`, `sqlite3_errmsg16()`, `sqlite3_errstr()`, and `sqlite3_error_offset()` expose the most recent error for a connection or a result-code string. Error strings are SQLite-owned and can be overwritten by later API calls. In serialized mode, another thread using the same connection can replace the error before the caller retrieves it unless the caller holds the connection mutex.

`sqlite3_set_errmsg()` lets extensions or wrappers set the connection's error code/message so they behave more like core features. It returns `SQLITE_OK`, `SQLITE_NOMEM`, or `SQLITE_MISUSE`.

### Prepared statement lifecycle, limits, prepare flags, and compile APIs

`sqlite3_stmt` is an opaque compiled SQL program. The documented lifecycle is prepare, bind, step, reset/rebind as needed, and finalize. The chunk declares `sqlite3_limit()` and limit constants for string/blob/row size, SQL length, columns, expression depth, compound select terms, VDBE op count, function arguments, attached databases, LIKE/GLOB pattern size, variable number, trigger depth, worker threads, and parser stack depth.

Prepare flags for `sqlite3_prepare_v3()`/`sqlite3_prepare16_v3()` include:

- `SQLITE_PREPARE_PERSISTENT`: hint that the statement will be reused and should avoid lookaside depletion.
- `SQLITE_PREPARE_NORMALIZE`: retained as a no-op compatibility flag.
- `SQLITE_PREPARE_NO_VTAB`: fail if virtual tables are used.
- `SQLITE_PREPARE_DONT_LOG`: suppress compiler errors from the configured error log.
- `SQLITE_PREPARE_FROM_DDL`: apply schema-sourced security restrictions, especially with `TRUSTED_SCHEMA` disabled.

Compile APIs declared here are `sqlite3_prepare()`, `sqlite3_prepare_v2()`, `sqlite3_prepare_v3()`, `sqlite3_prepare16()`, `sqlite3_prepare16_v2()`, and `sqlite3_prepare16_v3()`. New code should use the v2/v3 family because prepared statements retain original SQL text, enabling automatic reprepare on schema changes, more precise step errors, and plan recompile when bound parameters can influence query planning.

Risk signals:

- `ppStmt` must not be NULL.
- Only the first statement in input SQL is compiled; `pzTail` points to the remainder.
- UTF-16 prepare paths convert to UTF-8 internally.
- Legacy prepare statements may fail operations that require saved SQL text, such as later explain-mode changes.

### Statement SQL, explain mode, busy state, values, contexts, and bindings

The statement-inspection APIs include `sqlite3_sql()`, `sqlite3_expanded_sql()`, and conditionally `sqlite3_normalized_sql()`. `sqlite3_expanded_sql()` allocates with `sqlite3_malloc()` and must be freed by the application; the others are statement-owned.

Statement property APIs include:

- `sqlite3_stmt_readonly()` to detect direct database writes.
- `sqlite3_stmt_isexplain()` to distinguish normal, EXPLAIN, and EXPLAIN QUERY PLAN statements.
- `sqlite3_stmt_explain()` to change explain mode when possible, requiring reset/inactive state and possibly saved SQL text.
- `sqlite3_stmt_busy()` to detect statements stepped but not completed or reset.

`sqlite3_value` is the dynamic typed SQL value object. The chunk distinguishes protected values, which have an internal mutex held, from unprotected values. Function arguments and `sqlite3_vtab_rhs_value()` results are protected; `sqlite3_column_value()` returns unprotected values that may only be passed to selected APIs. `sqlite3_context` is the SQL-function execution context used by application-defined functions and aggregate/window state APIs declared in later chunks.

Binding APIs declared here include blob, blob64, double, int, int64, null, text, text16, text64, value, pointer, zeroblob, and zeroblob64 variants. Parameter metadata APIs include `sqlite3_bind_parameter_count()`, `sqlite3_bind_parameter_name()`, `sqlite3_bind_parameter_index()`, and `sqlite3_clear_bindings()`.

Important binding semantics:

- Host parameters are 1-indexed and may be anonymous (`?`), numbered (`?NNN`), or named (`:VVV`, `@VVV`, `$VVV`).
- `sqlite3_reset()` does not clear bindings.
- Length arguments are byte counts, not character counts.
- Negative blob length is undefined; negative text length means scan to terminator.
- `SQLITE_STATIC`, `SQLITE_TRANSIENT`, or a destructor define object lifetime for text/blob pointers.
- `sqlite3_bind_pointer()` binds SQL NULL plus a typed pointer for the pointer-passing interface; `SQLITE_TRANSIENT` as its destructor value is undefined.
- `zeroblob` placeholders are memory-efficient and intended for incremental BLOB writes.

Test signals: binding tests should cover destructor invocation on failure, embedded NUL behavior, text encoding and BOM handling, out-of-range indexes (`SQLITE_RANGE`), oversized values (`SQLITE_TOOBIG`), OOM (`SQLITE_NOMEM`), binding after step without reset (`SQLITE_MISUSE`), and parameter name/index handling for repeated named parameters and sparse `?NNN` slots.

### Result column metadata at chunk end

The chunk declares `sqlite3_column_count()`, `sqlite3_column_name()`, `sqlite3_column_name16()`, and, when compiled with `SQLITE_ENABLE_COLUMN_METADATA`, origin metadata APIs:

- `sqlite3_column_database_name()` / `sqlite3_column_database_name16()`
- `sqlite3_column_table_name()` / `sqlite3_column_table_name16()`
- `sqlite3_column_origin_name()` / `sqlite3_column_origin_name16()`

These functions return statement-owned pointers valid until finalize, automatic reprepare, or a later same-column metadata request in another encoding. They return NULL for expressions/subqueries or allocation failures. Concurrent metadata calls against the same statement/result column have undefined results.

Line 5,207 starts documentation for declared datatype lookup. The range stops at line 5,232 before completing the documentation or declarations, so the merge lane should expect the corresponding APIs to be covered in the next chunk.

## Control Flow and State Model

This header chunk describes a layered API flow rather than implementation bodies:

1. Process startup optionally calls `sqlite3_config()` before `sqlite3_initialize()`.
2. `sqlite3_initialize()` initializes mutexes, memory, global state, and the default VFS via `sqlite3_os_init()`.
3. Applications open a `sqlite3` connection with `sqlite3_open*()`, optionally selecting flags, URI parameters, mutex mode, cache mode, and VFS.
4. Connection-local behavior is adjusted with `sqlite3_db_config()`, limits, busy handlers, authorizers, trace/progress hooks, or extended result-code mode.
5. SQL is compiled with `sqlite3_prepare_v2()`/`v3()`, optionally invoking authorizer/progress callbacks and using limits/security flags.
6. Applications bind values, step statements, inspect results/metadata/errors, reset and reuse statements, and finalize them in later API sections.
7. VFS and file method tables mediate persistence, locking, shared memory, WAL/journal files, syncs, and file-control signals.
8. Connections are closed with `sqlite3_close()` or `sqlite3_close_v2()`, rolling back open transactions and handling dependent objects according to close variant.
9. Process shutdown may call `sqlite3_shutdown()` only after all resources are released.

State is scoped at several levels:

- Global: initialization state, threading mode, allocator/mutex/page-cache/log/URI defaults, memory statistics, PRNG seed, registered VFS list.
- Connection: open database files, error state, last insert rowid, change counters, busy handler, authorizer, trace callback, progress callback, runtime limits, DBCONFIG flags, mutex mode, cache mode, URI state.
- Statement: original SQL, bytecode, bindings, activity/reset state, explain mode, result-column metadata, automatic reprepare state.
- VFS/file: OS file handles, lock state, WAL shared-memory mappings, device capabilities, sync behavior, filesystem-specific configuration.

## Dependencies and Integration Points

Internal SQLite modules implied by this API include the parser/code generator, VDBE bytecode engine, pager, btree, WAL, rollback journal, mutex subsystem, memory allocator, page cache, pragma processor, virtual table layer, extension loading, error logging, and platform VFS implementations.

External integration points include:

- Host-language wrappers that map `sqlite3`, `sqlite3_stmt`, and callback lifetimes into managed runtimes.
- Custom VFS implementations or shims that implement `sqlite3_vfs`, `sqlite3_file`, `sqlite3_io_methods`, URI metadata, and file-control opcodes.
- Embedded systems that configure static allocators, custom mutexes, or nonstandard OS initialization with `SQLITE_OS_OTHER`.
- Security-sensitive applications that combine authorizers, DBCONFIG defensive/trusted-schema flags, prepare flags, limits, immutable/nolock choices, and extension loading controls.
- Diagnostics/observability through compile options, runtime version checks, error codes, error offsets, trace/profile/progress callbacks, memory statistics, file statistics, and VFS names.

## Risks and Edge Cases

- The file is a generated-header template. Research and downstream reports should preserve the distinction between `sqlite.h.in` placeholders and emitted `sqlite3.h` constants.
- ABI/source compatibility depends on opaque handles staying opaque and on public struct append-only versioning for VFS and I/O method tables.
- Many APIs are intentionally not reentrant from callbacks. Busy, authorizer, progress, trace, and log callbacks can deadlock or corrupt state if they call mutating SQLite APIs on the invoking connection.
- Shared connections across threads require attention even in serialized mode because per-connection error state and counters can change between API calls.
- VFS implementers can cause silent corruption by mishandling short reads, locks, sync ordering, shared-memory locks, atomic-write opcodes, file-control opcodes, or immutable/nolock semantics.
- `SQLITE_OPEN_EXCLUSIVE` is VFS-only and does not mean application-level exclusive open in `sqlite3_open_v2()`.
- `sqlite3_open*()` failure handling still usually requires `sqlite3_close()` on the returned handle.
- Text/blob binding length and lifetime rules are a frequent source of use-after-free, embedded-NUL surprises, destructor double-free assumptions, and undefined behavior.
- Security options are interdependent: `TRUSTED_SCHEMA`, `PREPARE_FROM_DDL`, extension loading, FTS tokenizer exposure, writable schema, attach-create/write, comments, and defensive mode each cover different attack surfaces.
- This chunk ends mid-section; declared-type APIs and the rest of the column/value/step/finalize surface must be reconciled with later chunk reports.

## Test Signals

Useful tests or review checks for this chunk include:

- Header/library version mismatch checks using `sqlite3_libversion_number()`, `sqlite3_sourceid()`, and compile-time macros.
- Build matrix tests with `SQLITE_OMIT_COMPILEOPTION_DIAGS`, `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_THREADSAFE=0/1/2`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ENABLE_NORMALIZE`, `SQLITE_ENABLE_SETLK_TIMEOUT`, and custom allocator/VFS builds.
- Connection lifecycle tests for unfinalized statements, `sqlite3_close()` returning `SQLITE_BUSY`, `sqlite3_close_v2()` zombie behavior, and transaction rollback on close.
- VFS contract tests for `xOpen()` failure cleanup, short-read zero fill, lock transition legality, `xShmLock()` legal combinations, sync flags, mmap fetch/unfetch, persistent WAL, atomic write opcodes, and URI filename metadata helpers.
- Configuration ordering tests proving pre-init-only options reject with `SQLITE_MISUSE` after initialization while documented anytime options still work.
- Security tests combining `sqlite3_set_authorizer()`, `sqlite3_limit()`, `SQLITE_PREPARE_NO_VTAB`, `SQLITE_PREPARE_FROM_DDL`, `SQLITE_DBCONFIG_TRUSTED_SCHEMA`, `SQLITE_DBCONFIG_DEFENSIVE`, and load-extension controls.
- Busy/progress/interrupt tests for lock contention, timeout replacement of custom busy handlers, deadlock avoidance, progress cancellation during prepare and step, and transaction rollback after interrupt.
- Open/URI tests for `:memory:`, empty temporary filename, `mode=ro/rw/rwc/memory`, VFS precedence, `cache=shared/private`, `immutable=1`, `nolock=1`, `SQLITE_OPEN_NOFOLLOW`, and `SQLITE_OPEN_EXRESCODE`.
- Error reporting tests for extended result-code mode, `sqlite3_error_offset()`, `sqlite3_set_errmsg()`, and thread interleaving of per-connection error state.
- Statement tests for v2/v3 automatic reprepare, `pzTail`, UTF-16 conversion, prepare flags, limit truncation, `sqlite3_stmt_explain()`, `sqlite3_stmt_busy()`, expanded SQL ownership, and normalized SQL conditional availability.
- Binding and metadata tests for 1-indexed parameters, repeated named parameters, sparse numbered parameters, destructor/lifetime modes, text64 encoding validation assumptions, zeroblob placeholders, clear-bindings behavior, column-count/name lifetime, and column-origin metadata under `SQLITE_ENABLE_COLUMN_METADATA`.

### subset-b-008789: lines 5233-10716

# sources/storage-engines/sqlite/src/sqlite.h.in lines 5233-10716

## Scope and Purpose

This chunk is the middle public C API reference section of SQLite's generated-header template. It declares and documents runtime interfaces for prepared statement execution, result and function value handling, application-defined SQL functions, collations, extension loading, virtual tables, incremental BLOB I/O, VFS registration, mutexes, runtime status counters, custom page-cache hooks, online backup, unlock notification, WAL hooks/checkpointing, and the beginning of prepared-statement scan-status support.

The file is a header input (`sqlite.h.in`), so the code here is mostly declarations, macros, typedefs, and API contracts rather than implementation bodies. Its implementation dependencies are the SQLite core objects declared elsewhere in the header (`sqlite3`, `sqlite3_stmt`, `sqlite3_context`, `sqlite3_value`, `sqlite3_vfs`, `sqlite3_mutex`, `sqlite3_file`, result codes, config opcodes, limits, and VFS/file-control opcodes). This chunk starts immediately after `sqlite3_column_decltype()` declarations and ends in the opening prose for `sqlite3_stmt_scanstatus()`, so scan-status function prototypes and remaining details continue in the next chunk.

## Major API Areas

### Prepared Statement Execution and Results

- `sqlite3_step(sqlite3_stmt*)` drives a prepared statement VM. Its return protocol distinguishes row production (`SQLITE_ROW`), completion (`SQLITE_DONE`), lock contention (`SQLITE_BUSY`), misuse, and richer `v2`/`v3` prepare-time errors. Legacy prepare APIs collapse many errors to `SQLITE_ERROR` until `sqlite3_reset()` or `sqlite3_finalize()`.
- `sqlite3_data_count(sqlite3_stmt*)` reports the number of columns in the current `SQLITE_ROW`, returning 0 for NULL statements, no current row, `SQLITE_DONE`, and special pragmas such as incremental vacuum.
- Datatype macros define the public dynamic type tags: `SQLITE_INTEGER`, `SQLITE_FLOAT`, `SQLITE_TEXT`/`SQLITE3_TEXT`, `SQLITE_BLOB`, and `SQLITE_NULL`.
- Column accessors (`sqlite3_column_blob`, `_double`, `_int`, `_int64`, `_text`, `_text16`, `_value`, `_bytes`, `_bytes16`, `_type`) expose the current row. Their core control-flow precondition is strict: the latest statement operation must have produced `SQLITE_ROW`, with no intervening reset/finalize, and no concurrent step/reset/finalize from another thread.
- `sqlite3_finalize()` is the required destructor for every prepared statement. It can be called at any point in statement lifetime and returns the most recent evaluation error if one occurred.
- `sqlite3_reset()` rewinds a prepared statement for re-execution without clearing bindings. Its return value reports the status of the prior evaluation, including late errors such as commit/locking failure after a statement that returned rows.

Important state behavior: column text/BLOB pointers are owned by SQLite and are valid only until type conversion, `sqlite3_step()`, `sqlite3_reset()`, or `sqlite3_finalize()`. Calls that force conversion between UTF-8/UTF-16/text/BLOB can invalidate earlier pointers. OOM during conversion can look like SQL NULL, so callers must consult `sqlite3_errcode()` immediately before making another SQLite call.

### Application-Defined SQL Functions and Values

- `sqlite3_create_function`, `sqlite3_create_function16`, `sqlite3_create_function_v2`, and `sqlite3_create_window_function` register scalar, aggregate, and window functions on a single database connection. They bind function name, arity, preferred text encoding, flags, user data, callbacks, and optional destructor.
- Text encoding constants (`SQLITE_UTF8`, `SQLITE_UTF16LE`, `SQLITE_UTF16BE`, `SQLITE_UTF16`, deprecated `SQLITE_ANY`, `SQLITE_UTF16_ALIGNED`, `SQLITE_UTF8_ZT`) are reused by function, collation, result, and bind APIs.
- Function flags (`SQLITE_DETERMINISTIC`, `SQLITE_DIRECTONLY`, `SQLITE_SUBTYPE`, `SQLITE_INNOCUOUS`, `SQLITE_RESULT_SUBTYPE`, `SQLITE_SELFORDER1`) feed planner optimization and schema-security policy. `DIRECTONLY` and `INNOCUOUS` are explicitly security-relevant for trusted-schema and injection-resistance scenarios.
- Deprecated APIs guarded by `SQLITE_OMIT_DEPRECATED` include `sqlite3_aggregate_count`, `sqlite3_expired`, `sqlite3_transfer_bindings`, `sqlite3_global_recover`, `sqlite3_thread_cleanup`, and `sqlite3_memory_alarm`.
- Value readers (`sqlite3_value_blob`, `_double`, `_int`, `_int64`, `_pointer`, `_text`, `_text16*`, `_bytes*`, `_type`, `_numeric_type`, `_nochange`, `_frombind`) expose `sqlite3_value` objects inside SQL function and virtual-table callbacks. They share pointer invalidation and same-thread requirements with column accessors.
- `sqlite3_value_encoding`, `sqlite3_value_subtype`, `sqlite3_value_dup`, and `sqlite3_value_free` expose internal text encoding, subtype metadata, and managed copies of values.
- Function-context APIs include `sqlite3_aggregate_context`, `sqlite3_user_data`, `sqlite3_context_db_handle`, `sqlite3_get_auxdata`, `sqlite3_set_auxdata`, `sqlite3_get_clientdata`, and `sqlite3_set_clientdata`.
- Result setters (`sqlite3_result_blob*`, `_double`, `_error*`, `_error_toobig`, `_error_nomem`, `_error_code`, `_int*`, `_null`, `_text*`, `_value`, `_pointer`, `_zeroblob*`) construct SQL function results and errors. `sqlite3_result_subtype()` attaches limited subtype metadata to a result.

State and lifecycle details are central here. Aggregate context memory is allocated once per aggregate instance, zeroed, reused for later xStep/xFinal calls, and freed when the aggregate query concludes. Auxdata and clientdata have destructor rules that may run on overwrite, reset/finalize, connection close, OOM, or even immediately during `sqlite3_set_auxdata()` when planning-time evaluation or allocation failure occurs. Result and pointer APIs use SQLite-owned copies or caller-provided destructors via `SQLITE_STATIC` and `SQLITE_TRANSIENT`.

### Collation, Sleep, Directories, Connection Metadata, and Hooks

- Collation APIs (`sqlite3_create_collation`, `_v2`, `_collation16`, `sqlite3_collation_needed`, `_needed16`) register comparison callbacks per connection and encoding. Comparison callbacks must define a stable total ordering; violating equality/transitivity/ordering constraints yields undefined SQLite behavior.
- `sqlite3_sleep()` delegates to the default VFS `xSleep`, with negative arguments normalized to zero in SQLite 3.42.0 and later.
- Global directory variables `sqlite3_temp_directory` and `sqlite3_data_directory` are legacy process-global knobs. They are unsafe to mutate concurrently, should be set during initialization, may be modified/freed by their PRAGMA counterparts, and are especially dangerous while connections are open (`sqlite3_data_directory` can contribute to corruption).
- Win32-specific helpers (`sqlite3_win32_set_directory`, `_directory8`, `_directory16`) and `SQLITE_WIN32_DATA_DIRECTORY_TYPE`/`SQLITE_WIN32_TEMP_DIRECTORY_TYPE` configure Windows directory state when enabled.
- Connection/statement introspection APIs include `sqlite3_get_autocommit`, `sqlite3_db_handle`, `sqlite3_db_name`, `sqlite3_db_filename`, `sqlite3_db_readonly`, `sqlite3_txn_state`, `SQLITE_TXN_NONE/READ/WRITE`, and `sqlite3_next_stmt`.
- Commit, rollback, autovacuum, and update hooks (`sqlite3_commit_hook`, `sqlite3_rollback_hook`, `sqlite3_autovacuum_pages`, `sqlite3_update_hook`) register callback behavior on a connection. The update hook excludes internal tables, WITHOUT ROWID tables, some REPLACE deletes, and truncate optimization deletes.

The hook APIs are integration points for host applications and extensions, but several callbacks are explicitly not reentrant or must not modify the invoking connection. `sqlite3_autovacuum_pages()` is particularly restrictive: its callback must not call other SQLite APIs because doing so can crash or corrupt database files.

### Memory, Metadata, Extension Loading, and Shared Cache

- `sqlite3_enable_shared_cache()` toggles process-wide shared-cache behavior for future connections, but shared cache use is discouraged and may be omitted by compile options.
- Memory APIs include `sqlite3_release_memory`, `sqlite3_db_release_memory`, `sqlite3_soft_heap_limit64`, `sqlite3_hard_heap_limit64`, and deprecated `sqlite3_soft_heap_limit`. Soft limits are advisory; hard limits fail allocations. Enforcement depends on memory accounting, page-cache configuration, and compile-time options.
- `sqlite3_table_column_metadata()` reads schema metadata for a table column, including type, collation, NOT NULL, primary-key, and autoincrement attributes. It can force schema loading/parsing and returns view/column/table existence errors.
- Extension loading APIs include `sqlite3_load_extension`, `sqlite3_enable_load_extension`, `sqlite3_auto_extension`, `sqlite3_cancel_auto_extension`, and `sqlite3_reset_auto_extension`.

Security risks are strong in this area. Extension loading is off by default; the C API recommends enabling only the C loading interface via `SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION` rather than `sqlite3_enable_load_extension()`, because the latter also enables the SQL `load_extension()` function and can turn SQL injection into arbitrary native-code loading. Automatic extensions run for every newly opened connection and can cause `sqlite3_open*()` to fail if an entry point returns an error.

### Virtual Table Core Interfaces

- Opaque typedefs introduce `sqlite3_vtab`, `sqlite3_index_info`, `sqlite3_vtab_cursor`, and `sqlite3_module`.
- `struct sqlite3_module` defines the virtual table module callback surface: create/connect, best-index planning, disconnect/destroy, cursor open/close/filter/next/eof/column/rowid, update, transaction hooks, function overloading, rename, savepoint/release/rollback-to, shadow-table naming, and integrity checking.
- `struct sqlite3_index_info` is the xBestIndex planner contract. Inputs describe constraints, ORDER BY terms, and used columns; outputs describe argv mapping, omitted constraints, chosen index number/string, ordering, estimated cost/rows, and scan flags.
- Scan and constraint macros include `SQLITE_INDEX_SCAN_UNIQUE`, `SQLITE_INDEX_SCAN_HEX`, and operator codes for equality/range/match/LIKE/GLOB/REGEXP/IS/ISNULL/ISNOTNULL/LIMIT/OFFSET/function constraints.
- Module registration APIs (`sqlite3_create_module`, `_v2`, `sqlite3_drop_modules`) attach module implementations to a connection and define destructor behavior for module client data.
- `sqlite3_vtab` and `sqlite3_vtab_cursor` are documented as superclasses for implementation-specific instances. Virtual table methods set `zErrMsg` with `sqlite3_mprintf()` and must free previous messages.
- `sqlite3_declare_vtab` declares the virtual table schema, and `sqlite3_overload_function` allows a virtual table to overload SQL functions.

Planner correctness risk is high. If xBestIndex sets `omit`, `orderByConsumed`, `estimatedRows`, `idxFlags`, or constraint argv mappings incorrectly, SQLite may generate inefficient plans or return incorrect results. The `estimatedRows`, `idxFlags`, and `colUsed` fields are version-gated by SQLite version; old runtimes cannot safely access fields added after their ABI version.

### Incremental BLOB, VFS, Mutex, File-Control, and Test-Control APIs

- `sqlite3_blob` is the handle for incremental BLOB I/O. `sqlite3_blob_open` opens a row/column blob, `sqlite3_blob_reopen` retargets to another row, `sqlite3_blob_close` releases it, `sqlite3_blob_bytes` reports size, and `sqlite3_blob_read`/`sqlite3_blob_write` move bytes.
- BLOB handles expire when the target row is updated, deleted, or affected by conflict side effects. Reads/writes on expired handles return `SQLITE_ABORT`; writes cannot resize a BLOB and require a write-opened handle.
- VFS registration APIs (`sqlite3_vfs_find`, `sqlite3_vfs_register`, `sqlite3_vfs_unregister`) manage process-level VFS instances and the default VFS.
- Mutex APIs (`sqlite3_mutex_alloc`, `_free`, `_enter`, `_try`, `_leave`) expose SQLite's synchronization layer. `sqlite3_mutex_methods` lets applications install custom mutex implementations through `sqlite3_config()`. Debug verification APIs `sqlite3_mutex_held` and `sqlite3_mutex_notheld` are available under `!NDEBUG`.
- Mutex type macros define dynamic (`SQLITE_MUTEX_FAST`, `SQLITE_MUTEX_RECURSIVE`) and static internal/application/VFS mutex IDs.
- `sqlite3_db_mutex()` returns the connection mutex in serialized mode.
- `sqlite3_file_control()` passes low-level opcodes and payloads through to a database file's VFS `xFileControl`.
- `sqlite3_test_control()` and `SQLITE_TESTCTRL_*` opcodes expose unstable internal testing/fault-injection hooks.
- SQL keyword helpers (`sqlite3_keyword_count`, `sqlite3_keyword_name`, `sqlite3_keyword_check`) expose parser keyword knowledge, which depends on compile-time options.

Risk signals here are mostly misuse and portability. Passing stale or foreign handles to BLOB, mutex, file-control, or test-control routines is undefined. `sqlite3_test_control()` is expressly not application-stable. VFS names must be unique and non-empty; conflicting registrations are undefined. Static mutexes are for SQLite internals and can change across releases.

### Dynamic Strings and Runtime Status

- `sqlite3_str` is an incremental string builder created with `sqlite3_str_new`, appended via `sqlite3_str_appendf`, `_vappendf`, `_append`, `_appendall`, `_appendchar`, reset/truncated, and finalized with `sqlite3_str_finish` or freed with `sqlite3_str_free`.
- `sqlite3_str_errcode`, `_length`, and `_value` report builder status. OOM and too-big conditions are sticky in the object; pointers returned by `_value` are invalidated by later string operations.
- Runtime status APIs `sqlite3_status`/`sqlite3_status64`, database status APIs `sqlite3_db_status`/`sqlite3_db_status64`, and statement status API `sqlite3_stmt_status` expose current/highwater counters with optional resets.
- Status macros cover heap memory use/counts, page-cache use/overflow/size, parser stack, lookaside usage/misses, pager cache use/hit/miss/write/spill, deferred foreign keys, temp-buffer spill, and statement-level counters such as full-scan steps, sorts, automatic indexes, VM steps, reprepare count, run count, bloom-filter hits/misses, and statement memory use.

Test signals for this area include checking that counters reset when requested, 64-bit APIs preserve large values, unsupported status verbs return non-OK, and highwater-only/current-only counters match documented behavior.

### Page Cache, Online Backup, Unlock Notify, Strings, and WAL

- `sqlite3_pcache` and `sqlite3_pcache_page` are opaque page-cache structures. `sqlite3_pcache_page` exposes page content (`pBuf`) and extra metadata storage (`pExtra`).
- `sqlite3_pcache_methods2` defines application-provided page-cache callbacks for init/shutdown/create/cache-size/page-count/fetch/unpin/rekey/truncate/destroy/shrink. The older `sqlite3_pcache_methods` is retained only for compatibility and is not used by current SQLite.
- `sqlite3_backup` and backup APIs (`sqlite3_backup_init`, `_step`, `_finish`, `_remaining`, `_pagecount`) implement online copying between source and destination databases.
- `sqlite3_unlock_notify()` coordinates shared-cache `SQLITE_LOCKED` failures by registering non-reentrant callbacks, detecting direct and indirect deadlocks, and documenting the DROP TABLE/INDEX same-connection exception.
- String utility APIs (`sqlite3_stricmp`, `_strnicmp`, `_strglob`, `_strlike`) provide SQLite-compatible case folding and pattern behavior. Match routines return zero on match.
- `sqlite3_log()` writes to the configured SQLite error log without dynamic allocation.
- WAL APIs include `sqlite3_wal_hook`, `sqlite3_wal_autocheckpoint`, `sqlite3_wal_checkpoint`, `sqlite3_wal_checkpoint_v2`, and checkpoint mode macros `SQLITE_CHECKPOINT_NOOP`, `PASSIVE`, `FULL`, `RESTART`, and `TRUNCATE`.

State and persistence behavior are especially explicit for backups and WAL. Backups hold a write transaction on the destination for the operation, read-lock the source only during step calls, can be retried for `BUSY`/`LOCKED`, and may restart if the source changes externally. The destination connection must not be used by other APIs until `sqlite3_backup_finish()`. WAL hooks run after commit and can read/write/checkpoint, but overriding auto-checkpoint hooks can allow WAL files to grow without periodic checkpoints. Checkpoint modes vary in locking, busy-handler use, reader/writer blocking, and whether the WAL is reset or truncated.

### Virtual Table Advanced Configuration and Scan Status Opening

- `sqlite3_vtab_config()` is callable only from xCreate/xConnect and accepts options such as `SQLITE_VTAB_CONSTRAINT_SUPPORT`, `SQLITE_VTAB_INNOCUOUS`, `SQLITE_VTAB_DIRECTONLY`, and `SQLITE_VTAB_USES_ALL_SCHEMAS`.
- `sqlite3_vtab_on_conflict`, `sqlite3_vtab_nochange`, `sqlite3_vtab_collation`, `sqlite3_vtab_distinct`, `sqlite3_vtab_in`, `sqlite3_vtab_in_first`, `sqlite3_vtab_in_next`, and `sqlite3_vtab_rhs_value` support virtual table update policy, xColumn no-change optimization, collation discovery, DISTINCT/GROUP BY/order planning, all-at-once IN handling, and literal RHS constraint access.
- Conflict macros `SQLITE_ROLLBACK`, `SQLITE_FAIL`, and `SQLITE_REPLACE` supplement existing `SQLITE_IGNORE` and `SQLITE_ABORT` constants.
- Scan-status opcodes begin here: `SQLITE_SCANSTAT_NLOOP`, `NVISIT`, `EST`, `NAME`, `EXPLAIN`, `SELECTID`, `PARENTID`, and `NCYCLE`. The chunk ends before the full `sqlite3_stmt_scanstatus()` declaration/details, which continue in the following chunk.

These advanced virtual-table APIs have narrow call-context requirements. Calling them outside xBestIndex, xFilter, xColumn, xUpdate, or xCreate/xConnect as documented is undefined and likely harmful. `sqlite3_vtab_distinct()` and `orderByConsumed` are correctness-sensitive: claiming ordering/distinctness guarantees that the virtual table cannot actually meet can produce wrong query answers.

## Dependencies and Integration Points

- Core database and VM handles: `sqlite3`, `sqlite3_stmt`, `sqlite3_context`, `sqlite3_value`, and `sqlite3_blob`.
- Error/result-code system: APIs rely heavily on `SQLITE_OK`, `SQLITE_ROW`, `SQLITE_DONE`, `SQLITE_BUSY`, `SQLITE_LOCKED`, `SQLITE_MISUSE`, `SQLITE_NOMEM`, `SQLITE_READONLY`, `SQLITE_ABORT`, `SQLITE_ERROR`, `SQLITE_NOTFOUND`, and extended IO/locked codes.
- Memory API integration: destructors and ownership rules depend on `sqlite3_malloc`, `sqlite3_malloc64`, `sqlite3_mprintf`, and `sqlite3_free`.
- VFS and pager integration: sleep, temp/data directories, file control, VFS registration, page cache methods, BLOB I/O, backup, WAL hooks/checkpoints, and shared cache all depend on lower-level VFS, pager, lock, and journaling subsystems.
- Planner integration: application functions, deterministic/innocuous/direct-only flags, virtual table xBestIndex output, RHS values, collation lookup, DISTINCT handling, IN handling, and statement/scan status all feed or observe the query planner and VDBE.
- Build-option integration: many APIs or semantics depend on compile options such as `SQLITE_OMIT_DEPRECATED`, `SQLITE_ENABLE_CEROD`, `SQLITE_ENABLE_UNLOCK_NOTIFY`, `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `SQLITE_ENABLE_ORDERED_SET_AGGREGATES`, `SQLITE_STRICT_SUBTYPE`, debug/NDEBUG settings, and platform VFS choices.

## Control Flow and Lifecycle Themes

- Prepared statement lifecycle: prepare (previous chunk), step repeatedly, read current-row columns only after `SQLITE_ROW`, reset for reuse while retaining bindings, finalize exactly once.
- SQL function lifecycle: register callbacks per connection, SQLite invokes callbacks during statement execution or sometimes planning, callbacks use `sqlite3_value` inputs and `sqlite3_result_*` outputs, destructors run on close/overwrite/failure according to API-specific rules.
- Virtual table lifecycle: register module, create/connect instance, planner calls xBestIndex, executor opens cursor and runs filter/next/eof/column/rowid, update and transaction callbacks participate in writes, disconnect/destroy releases instance state.
- BLOB lifecycle: open handle to a row/column, read/write within fixed byte length, optionally reopen to a different row, close handle; handle can expire due to row changes.
- Backup lifecycle: initialize, step pages in bounded increments, inspect remaining/pagecount after steps, finish to commit or roll back destination transaction and release resources.
- WAL lifecycle: commits may invoke WAL hook/autocheckpoint, manual checkpoints transfer frames from WAL to database with mode-dependent locks, periodic checkpointing is required to keep WAL size bounded.

## Risks and Edge Cases

- Undefined behavior is common for wrong call order, stale handles, cross-thread use, invalid pointers, out-of-range column indexes, and calling virtual-table helpers outside their documented callback.
- Pointer invalidation after text/blob/value conversion is a major API hazard; callers must copy data they need beyond the documented lifetime.
- Security-sensitive APIs include extension loading, application-defined SQL functions reachable from schema objects, clientdata exposure, direct access to global directory variables, and virtual tables marked innocuous/direct-only incorrectly.
- Reentrant callbacks can deadlock or corrupt state: autovacuum callbacks, unlock-notify callbacks, update hooks, and some function/virtual-table callbacks restrict which SQLite APIs may be called.
- Process-global knobs (`sqlite3_temp_directory`, `sqlite3_data_directory`, shared cache, VFS registration, auto extensions, heap limits) can affect unrelated connections and threads.
- Version and compile-option skew affect ABI fields, available APIs, keyword sets, status counters, unlock notify, ordered-set aggregates, strict subtype enforcement, memory management, and deprecated symbols.
- Backup and WAL APIs interact directly with filesystem locks; busy/locked responses are sometimes retryable and sometimes fatal depending on the exact operation and code.

## Test Signals

- Statement tests should cover legacy versus v2/v3 prepare error propagation, automatic reset behavior after terminal step results, reset returning late write errors, and column pointer invalidation after conversions.
- Function tests should exercise deterministic/direct-only/innocuous/subtype flags, destructor invocation on success/failure/overwrite/close, auxdata immediate destructor paths, aggregate context allocation from xFinal with no rows, and same-thread constraints.
- Extension-loading tests should verify disabled-by-default behavior, C-only enablement through db-config, SQL `load_extension()` isolation, auto-extension duplicate registration, cancellation, reset, and error propagation through `sqlite3_open*()`.
- Virtual table tests should validate xBestIndex argv mapping, omit semantics, `orderByConsumed`, estimated rows/flags under version gates, IN all-at-once iteration, RHS literal extraction, no-change optimization, and conflict-policy reporting.
- BLOB tests should include fixed-size writes, bounds errors, readonly handles, expiration after row update/delete, reopen behavior, and error-code propagation.
- VFS/mutex/page-cache tests should use custom implementations to verify init/shutdown, static versus dynamic mutex behavior, file-control forwarding, VFS default replacement, page fetch/unpin/rekey/truncate semantics, and shrink calls.
- Status tests should check current/highwater behavior, reset flags, large-value preservation in 64-bit APIs, unsupported op return codes, and statement counters across step/reset/finalize.
- Backup/WAL/unlock tests should cover retryable `BUSY`/`LOCKED`, fatal backup errors, destination-handle exclusivity, source modification restart, checkpoint mode locking differences, autocheckpoint hook replacement, and unlock-notify deadlock detection.

## Cross-Chunk Notes

- Lines before 5233 define earlier declaration context for column metadata and many base types/macros referenced here.
- Lines after 10716 continue the `sqlite3_stmt_scanstatus()` CAPI section, so this chunk only captures scan-status opcode definitions and the start of the API prose.

### subset-b-008790: lines 10717-11389

# sources/storage-engines/sqlite/src/sqlite.h.in lines 10717-11389

## Scope

This chunk covers the final public API declarations and preprocessor cleanup in `sqlite.h.in`. It starts in the prepared-statement scan-status documentation and then declares APIs for scan counters, mid-transaction pager cache flushing, pre-update hooks, OS error reporting, WAL snapshot handles, database serialization/deserialization, `carray()` parameter binding, and closing platform/header guards. The file is a generated-header template, so this range is API contract and documentation rather than implementation logic.

## Purpose

- Expose optional statement scan-status inspection for prepared statements compiled with `SQLITE_ENABLE_STMT_SCANSTATUS`.
- Provide `sqlite3_db_cacheflush()` as an explicit way to push dirty pager-cache pages to disk during a write transaction without ending the transaction.
- Define the optional pre-update hook API family behind `SQLITE_ENABLE_PREUPDATE_HOOK` for observing row changes before they occur and for reading old/new column values during the callback.
- Expose `sqlite3_system_errno()` so callers can retrieve the platform-specific low-level cause of the most recent file-open or I/O failure.
- Define the opaque `sqlite3_snapshot` handle and its lifecycle for opening historical WAL read transactions.
- Expose database image serialization and deserialization APIs when `SQLITE_OMIT_DESERIALIZE` is not used.
- Expose `sqlite3_carray_bind_v2()` and the legacy-compatible `sqlite3_carray_bind()` wrapper for binding host arrays into the `carray()` table-valued function.
- Restore header state at the end of the generated SQLite C API header: undo the no-floating-point `double` macro, apply WASI defaults, close the C++ `extern "C"` block, and leave the final include-guard close for `mksqlite3.tcl`.

## Important APIs, Types, And Constants

- `sqlite3_stmt_scanstatus(sqlite3_stmt *pStmt, int idx, int iScanStatusOp, void *pOut)` returns one scan-status metric for a query-plan loop. It is documented as equivalent to `sqlite3_stmt_scanstatus_v2()` with `flags==0`.
- `sqlite3_stmt_scanstatus_v2(sqlite3_stmt *pStmt, int idx, int iScanStatusOp, int flags, void *pOut)` extends scan status to optionally cover all `EXPLAIN QUERY PLAN` elements, not only loop elements. `idx==-1` may target whole-query statistics for supported metrics. Out-of-range `idx` returns non-zero and leaves `*pOut` unchanged.
- `SQLITE_SCANSTAT_COMPLEX` is the only scan-status flag in this chunk. When set, indexes address all complex plan elements reported by `EXPLAIN QUERY PLAN`; when clear, indexes address only `SCAN...` and `SEARCH...` loop elements.
- `sqlite3_stmt_scanstatus_reset(sqlite3_stmt*)` zeros scan-status event counters for a prepared statement.
- `sqlite3_db_cacheflush(sqlite3*)` flushes dirty pager-cache pages for all schemas on a connection, including `main`, `temp`, and attached databases, subject to page-use and locking constraints.
- `sqlite3_preupdate_hook(sqlite3 *db, xPreUpdate, void *pArg)` installs or clears a single pre-update callback per database connection. It returns the previous callback context pointer.
- `sqlite3_preupdate_old(sqlite3*, int, sqlite3_value**)` and `sqlite3_preupdate_new(sqlite3*, int, sqlite3_value**)` expose old/new protected values for the current pre-update event. Valid call sites depend on the operation: old values are valid for `UPDATE`/`DELETE`, new values for `INSERT`/`UPDATE`.
- `sqlite3_preupdate_count(sqlite3*)` returns the column count for the row being changed.
- `sqlite3_preupdate_depth(sqlite3*)` reports trigger nesting depth for the current change, with direct top-level changes at depth 0.
- `sqlite3_preupdate_blobwrite(sqlite3*)` distinguishes `sqlite3_blob_write()`-driven pre-update events from normal deletes by returning the written blob column index, or `-1` otherwise.
- `sqlite3_system_errno(sqlite3*)` returns an OS-dependent error number associated with the most recent I/O or open failure, for example a Unix `errno` after `SQLITE_CANTOPEN`.
- `sqlite3_snapshot` is an opaque 48-byte public struct. The hidden byte array deliberately prevents callers from depending on the internal WAL header layout while keeping the ABI-sized object visible.
- `sqlite3_snapshot_get(sqlite3 *db, const char *zSchema, sqlite3_snapshot **ppSnapshot)` allocates a snapshot handle for the current read view of a WAL-mode schema. The caller must free successful handles with `sqlite3_snapshot_free()`.
- `sqlite3_snapshot_open(sqlite3 *db, const char *zSchema, sqlite3_snapshot *pSnapshot)` starts or repositions a read transaction so it reads from a historical snapshot instead of the newest database state.
- `sqlite3_snapshot_free(sqlite3_snapshot*)` destroys a snapshot handle allocated by `sqlite3_snapshot_get()`.
- `sqlite3_snapshot_cmp(sqlite3_snapshot *p1, sqlite3_snapshot *p2)` compares snapshot age for two handles associated with the same database file and current WAL generation.
- `sqlite3_snapshot_recover(sqlite3 *db, const char *zDb)` scans a persistent WAL file to make older valid frames available to `sqlite3_snapshot_open()`.
- `sqlite3_serialize(sqlite3 *db, const char *zSchema, sqlite3_int64 *piSize, unsigned int mFlags)` returns a byte image for a database schema. Without `SQLITE_SERIALIZE_NOCOPY`, it returns a caller-owned allocation from `sqlite3_malloc64()`.
- `SQLITE_SERIALIZE_NOCOPY` requests a direct pointer to SQLite's contiguous in-memory representation, when one exists, and avoids allocating a copy.
- `sqlite3_deserialize(sqlite3 *db, const char *zSchema, unsigned char *pData, sqlite3_int64 szDb, sqlite3_int64 szBuf, unsigned mFlags)` replaces a schema with an in-memory database backed by the supplied serialized bytes.
- `SQLITE_DESERIALIZE_FREEONCLOSE`, `SQLITE_DESERIALIZE_RESIZEABLE`, and `SQLITE_DESERIALIZE_READONLY` control ownership, growth, and mutability of the deserialized database buffer.
- `sqlite3_carray_bind_v2(sqlite3_stmt *pStmt, int i, void *aData, int nData, int mFlags, void (*xDel)(void*), void *pDel)` binds an array to the first argument of a `carray()` table-valued function invocation.
- `sqlite3_carray_bind(...)` is a compatibility wrapper equivalent to the v2 form with the destructor argument `D` set to the array pointer `P`.
- `SQLITE_CARRAY_INT32`, `SQLITE_CARRAY_INT64`, `SQLITE_CARRAY_DOUBLE`, `SQLITE_CARRAY_TEXT`, and `SQLITE_CARRAY_BLOB` identify the element layout passed to `carray()`. The unprefixed `CARRAY_*` aliases preserve legacy compatibility.

## Control Flow And Contracts

Scan-status callers prepare and execute a statement, then query `sqlite3_stmt_scanstatus_v2()` by metric and query-plan element index. With `SQLITE_SCANSTAT_COMPLEX` clear, the index space is filtered to loop-like plan nodes. With the flag set, it is aligned to all plan elements for which SQLite stored scan-status metadata. The API writes a type-specific value into `pOut`: counters are integer-like, estimates are `double`, and plan/name data are string pointers. `sqlite3_stmt_scanstatus_reset()` clears the accumulated execution and cycle counters without changing the statement program.

`sqlite3_db_cacheflush()` runs against a database connection, not a single schema. It only has useful flushing work when a write transaction is open. The flush loop skips dirty pages currently in use by active cursors and page 1, and it may acquire additional database locks before writing pages. If a needed lock is busy and cannot be obtained after the busy handler, that database is skipped and the routine continues with other schemas. A pure lock-skipped result returns `SQLITE_BUSY`; I/O, allocation, or other errors abort the operation immediately with that error code.

The pre-update hook registration is connection-local. Registering a callback overwrites the old callback, and registering a NULL callback disables it. The callback fires before real table changes for `INSERT`, `UPDATE`, and `DELETE`, but not for virtual table updates or system tables such as `sqlite_sequence` and `sqlite_stat1`. During the callback, the caller can ask for operation metadata, rowids, column counts, old/new column values, and trigger depth. The auxiliary routines are callback-scoped; using them outside the matching callback or with a different connection is explicitly undefined.

Pre-update rowid arguments have operation-specific meaning. For rowid-table `UPDATE` and `DELETE`, `iKey1` is the original rowid. For rowid-table `INSERT` and `UPDATE`, `iKey2` is the final rowid. For `WITHOUT ROWID` tables, and for rowid cases where the operation does not provide the corresponding old or new rowid, the value is undefined. `sqlite3_blob_write()` is documented as invoking the hook with `SQLITE_DELETE` because the new values are not available at that point; `sqlite3_preupdate_blobwrite()` is the disambiguation signal.

Snapshot control flow is WAL-specific. A caller must turn off autocommit with an explicit transaction before calling `sqlite3_snapshot_get()` or `sqlite3_snapshot_open()`. Snapshot get may automatically open a read transaction on the named schema if none exists, then returns a heap-allocated handle representing the current WAL read mark. Snapshot open either starts a read transaction on the requested snapshot or upgrades an existing read transaction, but an existing read transaction requires no active statements. If the snapshot has been overwritten by checkpointing, `sqlite3_snapshot_open()` returns `SQLITE_ERROR_SNAPSHOT`.

Snapshot recovery is a special repair/discovery path for persistent WAL files left on disk after all connections closed. Without recovery, a new connection may only be able to open the last WAL transaction through the snapshot API. `sqlite3_snapshot_recover()` scans the WAL for the named database and makes all valid snapshots visible to later `sqlite3_snapshot_open()` calls. It fails if a read transaction is already open or the database is not in WAL mode.

Serialization reads a database image and returns its byte representation. For ordinary on-disk databases, the image is equivalent to the database file. For in-memory and temp databases, it is the database image that would be written by a backup. The no-copy mode only succeeds when SQLite is already using a contiguous memory image for that schema, usually after deserialization. If no-copy succeeds, the pointer stays valid and unchanged until the next write on the connection or connection close, and applications must not modify it.

Deserialization disconnects the named schema and reopens it as an in-memory database using the caller-supplied buffer. `szDb` is the database image size and `szBuf` is the total available buffer size; `szBuf` must be at least `szDb`. If the buffer is larger and the database is not read-only, SQLite may append page-sized content up to `szBuf`. With `SQLITE_DESERIALIZE_RESIZEABLE`, SQLite may grow the buffer with `sqlite3_realloc64()`, but the docs constrain that flag to buffers also owned by SQLite through `SQLITE_DESERIALIZE_FREEONCLOSE`.

`carray()` binding stores a typed array pointer or copy on a prepared-statement parameter. The parameter index must be the first argument to the `carray()` table-valued function. Destructor handling follows SQLite's binding conventions with an extension: a custom destructor is invoked with the separate `pDel` argument in the v2 form, and it is invoked even if binding fails. `SQLITE_STATIC` means SQLite does not own the data. `SQLITE_TRANSIENT` means SQLite copies the array before returning and does not call the caller's destructor.

## State And Persistence Behavior

- Scan-status counters are statement-local runtime state attached to the VDBE program. Resetting them does not change database contents.
- `sqlite3_db_cacheflush()` affects pager-cache dirty state and database files, but it does not commit or roll back the active transaction. Pages written mid-transaction remain part of the transaction's normal durability and rollback/WAL semantics.
- Pre-update hook registration is mutable connection state. The callback context pointer is stored on the `sqlite3` handle and the previous pointer is returned when replacing it.
- Pre-update old/new `sqlite3_value` pointers are protected and temporary. They are destroyed when the pre-update callback returns and should not be retained.
- `sqlite3_system_errno()` exposes low-level connection error state stored by VFS/open paths; the value is platform-specific and meaningful only for recent open/I/O failures.
- Snapshot handles are heap objects whose public type is opaque. They encode WAL-index header state and remain useful only while their WAL generation and frames are still available.
- Snapshot validity depends on WAL persistence and checkpoint behavior. A checkpoint can make a historical snapshot unavailable, and WAL deletion/restart invalidates comparisons for older handles.
- Serialized database buffers returned without `SQLITE_SERIALIZE_NOCOPY` are caller-owned and must be freed with SQLite's allocator. No-copy buffers remain SQLite-owned.
- Deserialized buffers may become SQLite-owned, caller-owned, fixed-size, resizable, or read-only depending on flags. Applications must not modify or invalidate the buffer while the connection uses it.
- `carray()` bindings are prepared-statement parameter state. Data lifetime is governed by `SQLITE_STATIC`, `SQLITE_TRANSIENT`, or the custom destructor installed through `sqlite3_carray_bind_v2()`.
- The final `#undef double` restores the C token after earlier floating-point omission support. The WASI block forces `SQLITE_WASI`, disables loadable extensions by default, and defaults `SQLITE_THREADSAFE` to 0 if the caller has not set it.

## Dependencies And Integration Points

- `sqlite3_stmt_scanstatus*()` depends on the scan-status option and VDBE instrumentation in `vdbeapi.c`. It integrates with earlier scan-status constants and with `EXPLAIN QUERY PLAN` output.
- Scan-status cycle reporting depends on opcode execution counters and cycle accounting, including `SQLITE_SCANSTAT_NCYCLE` and the bytecode virtual table's `nexec` and `ncycle` columns referenced by the header comments.
- `sqlite3_db_cacheflush()` integrates with the pager layer for each attached schema and with the busy-handler mechanism used by the connection's locking code.
- The pre-update hook declarations depend on `SQLITE_ENABLE_PREUPDATE_HOOK`. Registration state lives on the `sqlite3` connection object, and value retrieval is tied to the internal update/delete/insert execution path.
- Pre-update callbacks use operation constants `SQLITE_INSERT`, `SQLITE_DELETE`, and `SQLITE_UPDATE` declared earlier in the public header. They expose `sqlite3_value` objects with protected lifetime rules.
- `sqlite3_system_errno()` is coupled to VFS implementations that preserve OS error numbers through failed opens and I/O operations. On Unix this maps naturally to `errno`; other VFSes define their own meaning.
- Snapshot APIs require `SQLITE_ENABLE_SNAPSHOT` and non-`SQLITE_OMIT_WAL` internals. Public functions in `main.c` call btree and pager snapshot helpers, which delegate to WAL functions such as `sqlite3WalSnapshotGet()`, `sqlite3WalSnapshotOpen()`, and snapshot comparison/check logic.
- Snapshot handles are documented in `sqlite.h.in` as 48 bytes because the WAL implementation currently stores `WalIndexHdr`-shaped data behind the opaque public type. Consumers must treat it as opaque despite the visible size.
- `sqlite3_serialize()` and `sqlite3_deserialize()` are omitted under `SQLITE_OMIT_DESERIALIZE`. Implementations live in the in-memory database/VFS path and interact with btree, pager, schema selection, and file-control hooks.
- Serialization and deserialization integrate with backup semantics, page-size/page-count logic, SQLite memory allocation (`sqlite3_malloc64()`, `sqlite3_free()`, `sqlite3_realloc64()`), and schema attachment rules.
- `sqlite3_deserialize()` cannot target `temp` and the docs warn that WAL-mode input database images are not supported as deserialized databases unless bytes 18 and 19 are changed to rollback-mode file-format values before the call.
- `sqlite3_carray_bind*()` depends on the `carray.c` table-valued function module and on `sqlite3_bind_pointer()` using the `"carray-bind"` pointer type. Extension access is exposed through `sqlite3ext.h` and `loadext.c`.
- `SQLITE_CARRAY_BLOB` uses `struct iovec`, so callers need the platform-visible iovec definition expected by the carray implementation.
- The WASI defaults affect extension loading and threading for the generated header on WebAssembly System Interface targets.
- The final comment notes that `mksqlite3.tcl` appends the closing `#endif` for `SQLITE3_H`, confirming this file is a template input to SQLite's amalgamation/header generation pipeline.

## Risks And Edge Cases

- `sqlite3_stmt_scanstatus_v2()` has undefined behavior if `iScanStatusOp` is not a valid scan-status option unless API armor catches it. Callers must pass a correctly typed `pOut` for the requested metric.
- The `SQLITE_SCANSTAT_COMPLEX` flag changes the meaning of `idx`. Tooling that mixes complex and non-complex indexing can silently ask for different plan elements.
- `idx==-1` is only documented as "may retrieve" whole-query statistics. Code should not assume all scan-status operations support whole-query values.
- Scan-status APIs exist only in builds with `SQLITE_ENABLE_STMT_SCANSTATUS`; applications and extensions need compile-time or runtime feature handling before linking against them.
- `sqlite3_db_cacheflush()` does not update `sqlite3_errcode()` or `sqlite3_errmsg()`. Callers relying on connection error state after a failure may report stale diagnostics.
- Cache flushing can return `SQLITE_BUSY` after partially flushing other attached databases. This creates observable partial progress without transaction completion.
- Pre-update auxiliary functions are explicitly undefined outside the callback or with the wrong connection. Misuse can expose invalid temporary values.
- Pre-update hooks do not fire for virtual tables or system tables, so audit/replication code using this hook alone can miss changes.
- Rowid callback arguments are undefined for several valid operation/table combinations, especially `WITHOUT ROWID` tables. Consumers must branch on table kind and operation instead of assuming values are meaningful.
- `sqlite3_blob_write()` appears as a `SQLITE_DELETE` pre-update event, which can confuse delete-tracking code unless it checks `sqlite3_preupdate_blobwrite()`.
- Snapshot APIs require non-autocommit transaction state. Calling them in SQLite's default autocommit mode returns `SQLITE_ERROR` and, for `snapshot_get()`, the docs leave read-transaction side effects undefined for some failure cases.
- `sqlite3_snapshot_get()` cannot create a snapshot until at least one transaction has been written to the current WAL file. Fresh WAL-mode databases with no WAL file are a documented failure case.
- Snapshot handles can be invalidated by writers or checkpointers depending on whether `sqlite3_snapshot_get()` opened the read transaction itself or reused an existing one.
- `sqlite3_snapshot_open()` requires the connection to know that the schema is in WAL mode. A newly opened connection may need a harmless read such as `PRAGMA application_id` before snapshot APIs work.
- Snapshot comparison is undefined for handles from different database files or from before the last WAL deletion/restart.
- `sqlite3_snapshot_recover()` is only for WAL files that persist across connection shutdown or abnormal process exit. It fails when a read transaction is open and should not be used as a general snapshot open retry.
- `sqlite3_serialize()` may return NULL for allocation failure, invalid schema, no no-copy contiguous representation, or other preparation/step failures. Callers need to inspect `piSize` and context, not only the pointer.
- `SQLITE_SERIALIZE_NOCOPY` returns SQLite-owned memory that becomes invalid after the next write or connection close. Modifying it is forbidden.
- `sqlite3_deserialize()` accepts potentially malformed database bytes and warns that SQLite may read slightly past `szDb`; untrusted inputs should include the recommended extra padding and still be treated as database parser attack surface.
- Deserialization fails with `SQLITE_BUSY` when the schema has an active read transaction or backup operation. Calling code must coordinate with readers and backups before replacing a schema.
- `SQLITE_DESERIALIZE_RESIZEABLE` without `SQLITE_DESERIALIZE_FREEONCLOSE` violates the documented ownership model and risks reallocating memory that SQLite does not own.
- Deserialized WAL-mode images will produce `SQLITE_CANTOPEN` when used unless the caller rewrites the database header file-format version bytes to rollback mode.
- `sqlite3_carray_bind_v2()` invokes custom destructors even on bind failure. Callers must not free the same data again after receiving an error.
- With `SQLITE_STATIC`, array memory must remain valid until SQLite finishes using the bound parameter. This includes the array of pointers for text and the `struct iovec` array and pointed-to blob memory for blob arrays.
- `SQLITE_TRANSIENT` copying can be expensive for large text/blob arrays and can fail with `SQLITE_NOMEM`; code must not assume binding is cheap.
- The unprefixed `CARRAY_*` constants can collide with application symbols, but they are intentionally retained for compatibility.
- WASI defaults may surprise embedders that expect loadable extensions or SQLite mutexes unless they explicitly define `SQLITE_OMIT_LOAD_EXTENSION`/`SQLITE_THREADSAFE` differently before including/building SQLite.

## Test Signals

- Build with `SQLITE_ENABLE_STMT_SCANSTATUS` and verify `sqlite3_stmt_scanstatus()` matches `sqlite3_stmt_scanstatus_v2(..., flags=0, ...)` for loop nodes.
- Exercise `SQLITE_SCANSTAT_COMPLEX` with plans containing non-loop `EXPLAIN QUERY PLAN` elements and verify index mapping differs from loop-only mode.
- Query valid and out-of-range scan-status indexes and confirm out-of-range calls return non-zero without mutating the output buffer.
- Reset scan status after statement execution and verify execution/cycle counters return to zero while statement execution remains valid.
- Run `sqlite3_db_cacheflush()` during write transactions with multiple attached schemas, with active cursors pinning dirty pages, and with a busy lock on one schema to verify partial flush plus `SQLITE_BUSY`.
- Verify cache-flush I/O or allocation failure returns immediately and does not rely on `sqlite3_errmsg()` being updated.
- Build with `SQLITE_ENABLE_PREUPDATE_HOOK` and cover callback registration replacement, disabling with NULL, returned previous context pointer, and operation metadata for insert/update/delete.
- Test pre-update value access for `UPDATE`, `DELETE`, and `INSERT`, including invalid old/new access patterns guarded in test builds.
- Cover trigger depth reporting for direct changes, top-level triggers, and nested triggers.
- Verify the hook excludes virtual tables and system tables, and separately cover `sqlite3_blob_write()` producing a delete-like callback with `sqlite3_preupdate_blobwrite()` returning the blob column.
- For snapshots, test failure in autocommit mode, failure on rollback-journal databases, failure before any WAL transaction exists, and success after a WAL write inside an explicit transaction.
- Test `sqlite3_snapshot_open()` with active statements on the target schema, invalid schema names, invalid snapshot data, and snapshots overwritten by checkpoint returning `SQLITE_ERROR_SNAPSHOT`.
- Test `sqlite3_snapshot_cmp()` for older/same/newer snapshots in the same WAL generation and avoid asserting behavior across WAL deletion or different database files.
- Test `sqlite3_snapshot_recover()` on a persistent WAL containing multiple transactions after reopening the database, and verify failure with an already-open read transaction.
- Test `sqlite3_serialize()` on on-disk, in-memory, temp, empty, and attached databases; verify size reporting, caller ownership, and NULL results under no-copy mode without a contiguous memory image.
- Test no-copy serialization after `sqlite3_deserialize()` and verify pointer stability until the next write and invalidation after write/close.
- Test `sqlite3_deserialize()` with fixed-size, resizable, read-only, and free-on-close buffers; include `szBuf==szDb`, extra capacity, growth past capacity, and failure cleanup behavior when `FREEONCLOSE` is set.
- Verify deserialization rejects `"temp"`, returns `SQLITE_BUSY` during active reads/backups, and fails or reports `SQLITE_CANTOPEN` for WAL-mode images unless header bytes are adjusted.
- Test `sqlite3_carray_bind_v2()` for all five element types, including text NULL entries and blob `struct iovec` entries.
- Test `carray()` destructor behavior for custom destructor success, custom destructor failure, `SQLITE_STATIC`, `SQLITE_TRANSIENT`, and the wrapper equivalence of `sqlite3_carray_bind()`.
- Build with `SQLITE_OMIT_FLOATING_POINT` and confirm the header's temporary `double` macro is undefined by the end of the header.
- Build for `__wasi__` and confirm the generated configuration defines `SQLITE_WASI`, omits loadable extensions by default, and defaults to single-threaded mode unless overridden.
