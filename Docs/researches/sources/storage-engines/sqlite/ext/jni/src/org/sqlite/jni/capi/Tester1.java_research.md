# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/Tester1.java

## Purpose
`Tester1` is the main regression and smoke-test suite for the SQLite JNI C API bindings. It can run single-threaded, repeated, shuffled, or multi-threaded, and validates handle lifetimes, callback proxies, UDFs, metadata, blob/backup APIs, error paths, and optional FTS5 support.

## Important APIs, Types, and Functions
The file defines annotations `ManualTest`, `SingleThreadOnly`, and `RequiresJniNio`, shared helpers `affirm()`, `createNewDb()`, `execSql()`, and `prepare()`, plus many `test*()` methods discovered reflectively. It covers open/close, prepare/tail handling, binding/fetching integers, doubles, text, blobs, Java objects, NIO buffers, SQL expansion, collations, status APIs, scalar/aggregate/window UDFs, trace/profile hooks, busy/progress/commit/update/preupdate/rollback/authorizer hooks, auto-extensions, table metadata, transaction state, explain, limits, keywords, backup, randomness, incremental blob I/O, prepare-multi, custom errmsg, config log, SQL log, shutdown, and JNI thread cache release.

## Control Flow
`main()` parses flags, optionally installs config callbacks, builds the reflective method list, validates `sqlite3_threadsafe()` configuration transitions, then runs loops either directly or through an `ExecutorService`. Each `Tester1` instance invokes all selected `test*()` methods and collects thread errors in a synchronized list.

## State and Persistence Behavior
Static state tracks multi-thread mode, shuffling, quiet output, run counts, selected methods, accumulated errors, assertion count, and DB-open metrics. Most tests use in-memory databases; file-backed tests clean up named files in `finally`. Native handles are checked for pointer zeroing after close/finalize.

## Dependencies and Integration Points
It imports nearly all `CApi` functions and integrates with low-level handle classes, output pointers, callbacks, UDF interfaces, FTS5 tester loading, and optional compile features such as `ENABLE_FTS5`, `ENABLE_PREUPDATE_HOOK`, `ENABLE_COLUMN_METADATA`, and `ENABLE_SQLLOG`.

## Risks
Threaded runs intentionally skip tests whose global state or SQLite behavior is thread-agnostic. Timing in `awaitTermination(nThread*200ms)` can be tight under slow environments. Tests assert JNI-specific lifetime defenses by retaining invalid handles; production code must not copy that pattern. Optional compile features change coverage.

## Test Signals
The whole class is itself the test signal. Strong indicators are zero thrown exceptions, nonzero assertion count, expected DB-open metrics, all pointer invalidation assertions passing, hook replacement return values matching previous callbacks, and FTS5 tests running when compiled in.
