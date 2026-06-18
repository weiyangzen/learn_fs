# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CApi.java

## Purpose
Primary Java surface for the SQLite C API JNI binding. It loads `sqlite3-jni`, declares native methods, wraps raw pointer-oriented native calls with safer Java object overloads, provides UTF conversion helpers, exposes SQLite constants, and adds Java-specific convenience APIs.

## Important APIs, Types, And Functions
Major API families include open/close, prepare/prepare multi, bind/result/column/value access, blob I/O, backup, hooks, authorizer, collation, UDF creation, aggregate context, auxdata, config/db_config/status, preupdate hooks, trace/update/commit/rollback/progress callbacks, keyword and compile option helpers, error handling, memory/shutdown/thread maintenance, and experimental NIO direct-buffer functions. `nulTerminateUtf8()` protects C APIs needing NUL-terminated UTF-8. `JNI_SUPPORTS_NIO` caches native direct-buffer support after `init()`.

## Control Flow
Class initialization loads the native library, initializes constants through native version calls, calls native `init()`, then probes NIO support. Most public wrappers unwrap `NativePointerHolder` instances to raw pointers, call private native methods, and sometimes clear or transfer ownership. `sqlite3_prepare_multi()` loops over UTF-8 input, prepares one statement at a time using tail offsets, passes ownership to a `PrepareMultiCallback`, and converts callback exceptions into database errors.

## State And Persistence Behavior
Persistent database state is owned by SQLite files and handles. Java-side state includes static constants, NIO support flag, callback objects held by native registrations, native pointer values in handle wrappers, and output pointer objects. Ownership-sensitive methods clear native pointers on `close`, `close_v2`, `finalize`, `blob_close`, `backup_finish`, and `value_free` to avoid stale Java handles.

## Dependencies And Integration Points
Depends on `StandardCharsets`, `Arrays`, annotations, `OutputPointer`, handle wrappers, callback interfaces, `SQLFunction`, `AggregateFunction`, and native implementation symbols declared in `sqlite3-jni.h`. It is the integration point for wrapper-level APIs under `wrapper1`, tests, and FTS5 helpers.

## Risks And Edge Cases
UTF-8 versus JNI modified UTF-8 is a central risk; byte-array APIs must use standard UTF-8 and some string APIs must append NUL terminators. Null/stale handles annotated `@NotNull` may still produce Java exceptions or SQLite misuse codes. Direct buffer APIs are experimental and can crash if buffers are mutated concurrently or native direct access is unavailable. Preupdate value handles must not escape callback scope. Shutdown while handles are active leaks or leaves undefined behavior.

## Test Signals
Signals include loading `sqlite3-jni`, sanity SQL tests, bind/column/value round trips for all supported types, prepare tail handling, multi-statement callback ownership, UDF/aggregate/window tests, hook callback tests, null/stale handle checks, direct-buffer tests gated on `sqlite3_jni_supports_nio()`, and constant parity with upstream SQLite.
