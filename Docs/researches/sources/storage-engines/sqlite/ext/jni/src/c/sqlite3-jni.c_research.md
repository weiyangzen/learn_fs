# sources/storage-engines/sqlite/ext/jni/src/c/sqlite3-jni.c

## Purpose

`sqlite3-jni.c` is the native implementation for the Java JNI bindings declared by `org.sqlite.jni.capi.CApi` and generated `sqlite3-jni.h`. It builds SQLite directly into the JNI library by including `sqlite3.c`, sets JNI-specific SQLite compile defaults, and exposes a broad set of SQLite C APIs to Java classes under `org.sqlite.jni.capi` plus optional FTS5 bindings under `org.sqlite.jni.fts5`.

The file is not only a thin wrapper layer. It owns global JNI state, native pointer holder caches, per-thread and per-database state, Java callback plumbing for SQLite hooks and user-defined SQL functions, Java object lifetime bridging through SQLite pointer/destructor APIs, direct `ByteBuffer` handling, optional metrics/debug output, optional SQLTester helpers, and static initialization through `CApi.init()`.

## Important APIs, Types, and Functions

- JNI naming and pointer helpers: `JniFuncName`, `JniDecl`, `S3JniApi`, `S3JniCast_L2P`, `S3JniCast_P2L`, `PtrGet_T`, and `LongPtrGet_T` centralize JNI symbol naming and pointer-to-`jlong` transport.
- Global state: `S3JniGlobalType S3JniGlobal` stores `JavaVM`, mutexes, cached Java classes/methods, native pointer holder metadata, per-thread env cache, per-db free list, Java auto-extension list, optional FTS5 singleton/cache, global config hooks, optional metrics, and recycling lists.
- Native pointer holder cache: `S3JniNphOp`, `S3JniNphOps`, `s3jni_nphop()`, `s3jni_nphop_field()`, `NativePointerHolder_get/set/new()`, and `new_java_sqlite3*()` connect Java wrapper instances to native `sqlite3`, `sqlite3_stmt`, `sqlite3_blob`, `sqlite3_value`, `sqlite3_context`, backup, FTS5, and `OutputPointer.*` types.
- JNI conversion helpers: `s3jni_jstring_to_utf8()`, `s3jni_utf8_to_jstring()`, `s3jni_jstring_to_mutf8()`, `s3jni_new_jbyteArray()`, `s3jni_text16_to_jstring()`, `s3jni_get_nio_buffer()`, and `s3jni__blob_to_ByteBuffer()` handle Java strings, byte arrays, UTF-16, and direct NIO buffers.
- Per-db state: `S3JniDb` tracks the native db handle, the Java db wrapper, main-db-name memory owned for `SQLITE_DBCONFIG_MAINDBNAME`, per-db hooks, and optional FTS5 API cache. It is associated with SQLite handles via `sqlite3_set_clientdata(..., "S3JniDb", ...)`.
- Hook/callback state: `S3JniHook` stores global Java references, callback method IDs, optional extra Java state, optional `xDestroy()`, and free-list links. `S3JniHook_localdup()` creates local-reference snapshots so callbacks can run while another thread changes hook registration.
- Java UDF state: `S3JniUdf` detects scalar, aggregate, or window SQL functions from Java method presence, stores method IDs and the function name, and dispatches through `udf_xFunc`, `udf_xStep`, `udf_xFinal`, `udf_xValue`, and `udf_xInverse`.
- Auto-extension bridge: `S3JniAutoExtension`, `sqlite3_auto_extension()` JNI wrapper, `s3jni_run_java_auto_extensions()`, cancel/reset routines, and `S3JniEnv.pdbOpening` coordinate Java auto-extension callbacks during `sqlite3_open()` before the Java wrapper is fully connected.
- Open/prepare/close paths: `s3jni_open_pre()`, `s3jni_open_post()`, `sqlite3_open`, `sqlite3_open_v2`, `sqlite3_jni_prepare_v123()`, `sqlite3_prepare`, `sqlite3_prepare_v2`, `sqlite3_prepare_v3`, `s3jni_close_db()`, `sqlite3_close`, and `sqlite3_close_v2` are the high-risk lifecycle bindings.
- Binding/result/data APIs: the file wraps binding blobs/text/int/double/null/value/zeroblob/Java object/NIO buffer; column/value accessors; result setters; blob open/read/write/reopen/close; backup APIs; db/status/config/metadata APIs; trace/progress/busy/authorizer/collation/update/preupdate/commit/rollback hooks; keyword/complete/strlike/strglob helpers.
- FTS5 APIs: under `SQLITE_ENABLE_FTS5`, it exposes `Fts5ExtensionApi`, `fts5_api`, and tokenizer bindings, including auxiliary function registration (`xCreateFunction`), FTS5 context methods, auxdata, phrase iterators, `xQueryPhrase`, and `xTokenize`.
- Initialization/shutdown: `Java_org_sqlite_jni_capi_CApi_init()` populates global Java references, method IDs, mutexes, optional FTS5 field IDs, and direct `ByteBuffer` capability, then calls `sqlite3_shutdown()` so Java may later call `sqlite3_config()`. `sqlite3_shutdown()` releases Java-side callbacks, free lists, and cached env rows while retaining `JavaVM` and core class refs for restart.

## Control Flow

Static initialization begins when `CApi.init()` is called from Java. It clears `S3JniGlobal`, captures the `JavaVM`, looks up persistent Java class/method references (`Long`, `String`, `StandardCharsets.UTF_8`, optional FTS5 phrase iterator fields), allocates SQLite mutexes, detects direct `ByteBuffer` support, and shuts SQLite down so configuration calls remain legal before explicit initialization.

Most wrapper functions follow a simple shape: extract native pointers from Java wrappers or `jlong`, convert Java data into C buffers or strings, call the SQLite C API, convert return/output values back into Java objects or `OutputPointer.*` fields, and release local/array/native allocations. Macro-generated wrappers cover direct scalar functions such as changes counts, statement status, libversion, keyword count, and simple value predicates. Hand-written wrappers are used where ownership, output pointers, Java object creation, callbacks, or text encoding are involved.

Opening a database is a multi-stage flow. `s3jni_open_pre()` allocates a Java `sqlite3` wrapper and `S3JniDb`, stashes the being-opened db in the current `S3JniEnv.pdbOpening`, and converts the filename/VFS. `sqlite3_open()` or `sqlite3_open_v2()` may trigger auto-extensions; if so `s3jni_run_java_auto_extensions()` temporarily associates the native db with the preallocated Java object. `s3jni_open_post()` finalizes the native pointer, attaches `S3JniDb` as SQLite client data with `S3JniDb_xDestroy`, writes the Java db object to `OutputPointer.sqlite3`, and cleans up failed opens.

Statement preparation goes through `sqlite3_jni_prepare_v123()`, which creates a Java `sqlite3_stmt` wrapper before calling `sqlite3_prepare`, `sqlite3_prepare_v2`, or `sqlite3_prepare_v3`. On success it stores the native statement pointer in the wrapper and optionally returns the SQL tail byte offset; comments/whitespace that produce no statement return a null output object. `sqlite3_finalize()` frees statements, while Java wrappers are only pointer holders and are not themselves native owners unless the Java layer enforces lifecycle.

Callback-heavy flows snapshot Java references before calling back into Java. Busy/progress/trace/update/preupdate/commit/rollback/collation/config-log hooks store Java global refs in `S3JniDb` or `S3JniGlobal.hook`, duplicate them into local refs inside the C callback, invoke Java methods, translate or suppress exceptions depending on SQLite callback semantics, and release local refs. UDF callbacks additionally wrap `sqlite3_context` and `sqlite3_value**` into temporary Java pointer holders, call Java function methods, then clear those temporary native pointers with `udf_unargs()` to reduce stale-pointer misuse.

FTS5 flow is conditional. The code retrieves database-specific `fts5_api` via `SELECT fts5(?1)`, exposes a global `Fts5ExtensionApi` wrapper for the SQLite extension API singleton, registers Java auxiliary functions through `fts5_api::xCreateFunction`, and bridges `Fts5Context` operations into Java. FTS5 tokenization and query-phrase callbacks use small state structs that hold Java callback objects, JNI method IDs, current token byte arrays, and temporary `Fts5Context` wrappers.

## State and Persistence Behavior

Persistent process-level state lives in `S3JniGlobal`. It includes cached global Java references and method/field IDs, free lists for `S3JniDb`, `S3JniHook`, and `S3JniUdf`, a per-thread `S3JniEnv` cache, Java auto-extension registrations, optional global config hooks, and optional metrics. These are in-memory only and survive SQLite open/close cycles until `sqlite3_shutdown()` or another `CApi.init()` reset.

Per-database state is stored in `S3JniDb` and attached to `sqlite3*` using `sqlite3_set_clientdata()`. This state persists for the lifetime of a JNI-opened database handle and owns the Java db wrapper global reference, hook refs, `zMainDbName`, and optional per-db FTS5 API wrapper. `S3JniDb_xDestroy()` moves it to a reusable free list when SQLite destroys the client data during close.

Java object persistence is managed with JNI global references for anything stored beyond a single native call. Java objects stored as SQL values, result pointers, auxdata, or FTS5 auxdata are retained as global refs and released by registered SQLite destructors. Temporary callback wrappers use local refs and attempt to clear embedded native pointers before returning.

The file affects SQLite persistence through the underlying SQLite APIs: open handles, statements, blobs, backups, SQL functions, collations, hooks, auto-extensions, and database configuration. It does not implement on-disk storage itself; persistent database behavior is delegated to the included SQLite core.

## Dependencies and Integration Points

- Includes `sqlite3.c` directly through configurable `SQLITE_C`, allowing builds against custom amalgamations while exposing internal SQLite constants and functions.
- Includes generated `sqlite3-jni.h`, which must match Java native declarations and JNI-mangled names. There is an explicit alternate mangled export for one `sqlite3_db_config()` overload to handle OpenJDK version differences.
- Relies on Java classes in `org.sqlite.jni.capi` such as `CApi`, `sqlite3`, `sqlite3_stmt`, `sqlite3_blob`, `sqlite3_value`, `sqlite3_context`, `sqlite3_backup`, `OutputPointer.*`, and callback interfaces.
- Optional FTS5 integration depends on Java classes in `org.sqlite.jni.fts5`, SQLite FTS5 being enabled, the SQLite FTS5 extension API singleton from `sqlite3.c`, and `Fts5PhraseIter` field names/signatures.
- Uses JNI 1.8 via `GetEnv(..., JNI_VERSION_1_8)`.
- Uses SQLite mutex APIs for process-global caches when `SQLITE_THREADSAFE` is enabled.
- Uses `sqlite3_set_clientdata`, `sqlite3_set_errmsg`, direct `ByteBuffer` JNI support, SQLite pointer APIs (`sqlite3_bind_pointer`, `sqlite3_result_pointer`, `sqlite3_value_pointer`), and optional compile flags such as `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_FTS5`, `SQLITE_ENABLE_SQLLOG`, `SQLITE_JNI_ENABLE_METRICS`, and `SQLITE_JNI_ENABLE_SQLTester`.

## Risks and Review Notes

- Native pointer lifetime is the central risk. Many Java wrapper objects carry raw native pointers; stale wrappers after finalize/close/callback return can invoke undefined behavior if the Java layer does not prevent reuse. `udf_unargs()` mitigates temporary UDF wrapper misuse but cannot clear values if Java mutates the argument array.
- Callback exception handling is intentionally mixed. UDF `xFunc` and `xFinal` translate exceptions into SQLite result errors, while some hooks warn and clear exceptions because SQLite callback contracts cannot propagate them cleanly. This needs tests that verify Java exceptions do not leak across JNI calls and that database error state is set where expected.
- Global/free-list state is mutex protected in many paths, but callbacks can re-enter SQLite/JNI. The code avoids holding certain mutexes across Java calls by duplicating local hook refs. Any new hook or global callback should follow that pattern to avoid races or deadlocks.
- `s3jni_xAuth()` appears to pass `s0, s1, s3, s3` to the Java authorizer callback instead of `s0, s1, s2, s3`; this would drop SQLite's third string argument and duplicate the fourth. That deserves focused verification against authorizer tests.
- `result_blob_text()` releases `jbyteArray` elements inside the non-64-bit branch, but the 64-bit branch does not visibly release `pBuf` before returning. If accurate, repeated `sqlite3_result_blob64()` or `sqlite3_result_text64()` calls may pin or leak array resources. This should be checked with JNI array stress tests and maybe `-Xcheck:jni`.
- Direct `ByteBuffer` handling deliberately uses `limit()` instead of capacity, which is correct for Java-visible bounds but calls back into Java on each buffer use. Tests should cover changed limits, non-direct buffers, zero-length slices, negative offsets, oversize lengths, and JVMs without direct-buffer JNI support.
- OOM behavior changes with `SQLITE_JNI_FATAL_OOM`. Some paths return `SQLITE_NOMEM`; others intentionally call `FatalError()`. New code must choose consistently based on whether SQLite can recover.
- JNI symbol names are brittle. New native methods must match generated `sqlite3-jni.h` mangling, and overloaded Java signatures may need special handling similar to the `db_config` OpenJDK compatibility wrapper.
- `CApi.init()` resets `S3JniGlobal` without first freeing prior global refs if called repeatedly in one JVM. If Java can invoke it more than once after active use, that may leak refs or invalidate cached state expectations.
- `sqlite3_shutdown()` intentionally retains `SJG.jvm` and `SJG.g` class refs. That supports restart but means full JVM-level native unload cleanup is not implemented in this file.

## Test Signals

- JNI smoke tests should load `CApi`, call `init`, verify `sqlite3_initialize/config/shutdown` order, and cover `sqlite3_jni_supports_nio()` on supported and unsupported JVMs.
- Open/close tests should cover successful open, failed open, auto-extension during open, `close` vs `close_v2`, reopen after shutdown/initialize, and client-data cleanup.
- Statement tests should cover `prepare`, `prepare_v2`, `prepare_v3`, tail offsets, whitespace/comment SQL returning null statements, step/reset/finalize, and wrapper misuse after finalize.
- Binding/result tests should cover byte arrays, UTF-8 strings containing non-MUTF-8-compatible content, UTF-16 strings, blobs, zeroblobs, `sqlite3_bind_java_object`, `sqlite3_result_java_object`, pointer destructor release, and NIO buffer slices.
- Hook tests should cover busy, progress, trace, commit, rollback, update, preupdate, collation-needed, collation compare, config log, authorizer argument ordering, replacing the same hook object, replacing with a new object, clearing hooks, and callbacks that throw.
- UDF tests should cover scalar, aggregate, and window detection; all callback methods; `xDestroy`; exception-to-result-error translation; auxdata; aggregate context; and stale temporary pointer protection after callback return.
- FTS5 tests, when enabled, should cover retrieving `fts5_api`, registering Java auxiliary functions, `xColumn*`, `xInst*`, phrase iterator round trips, `xQueryPhrase`, `xTokenize`, auxdata ownership, and callback exception behavior.
- Diagnostic builds should run with `-Xcheck:jni`, SQLite API armor, `SQLITE_DEBUG`, optional `SQLITE_JNI_ENABLE_METRICS`, and memory/fault-injection tests for allocation failures and JNI local/global ref cleanup.
