# sources/storage-engines/sqlite/ext/jni/src/c/sqlite3-jni.h

## Purpose
Machine-generated JNI header for the SQLite Java binding. It exposes native entry points for `org.sqlite.jni.capi.CApi`, plus JNI declarations for `SQLTester` and FTS5 helper classes. It is the ABI contract between Java native methods and the C implementation in `sqlite3-jni.c`.

## Important APIs, Types, And Functions
The header defines `org_sqlite_jni_capi_CApi_*` constants mirroring SQLite integer constants and declares `JNIEXPORT` functions for database handles, statements, blobs, backup, binding, column access, result values, hooks, configuration, preupdate APIs, value accessors, status APIs, NIO buffer support, Java object binding, and shutdown/thread-cache maintenance. Additional declarations cover `SQLTester.strglob`, `SQLTester.installCustomExtensions`, `Fts5ExtensionApi` methods, `fts5_api.getInstanceForDb`, `fts5_api.xCreateFunction`, and `fts5_tokenizer.xTokenize`.

## Control Flow
There is no executable control flow in this header. Runtime dispatch is controlled by the JVM resolving Java native method signatures to the C symbols declared here. Overloaded Java native methods are represented with JNI-mangled suffixes, for example the two `sqlite3_db_config` forms.

## State And Persistence Behavior
No state is stored here. The header describes functions that manipulate SQLite persistent state through database files and transient JNI state through native pointer wrappers, callbacks, direct buffers, and per-thread caches. Staleness risk is ABI-level: if Java native declarations and this generated header diverge, class loading or native calls fail.

## Dependencies And Integration Points
Depends on `jni.h`, `org.sqlite.jni.capi.CApi`, `SQLTester`, and `org.sqlite.jni.fts5` Java classes. It integrates with the JNI C implementation, the Java wrapper objects derived from `NativePointerHolder`, and SQLite optional features such as FTS5, preupdate hook, column metadata, normalization, and SQL log.

## Risks And Edge Cases
Because this is generated, manual edits are likely to be lost and can desynchronize native signatures. Pointer arguments appear as `jlong` or `jobject`, so C implementation must validate null and stale pointer cases. The header includes several logical API families in one file, so partial regeneration can miss FTS5 or tester declarations. Constant drift from SQLite upstream can cause Java callers to pass wrong opcodes or flags.

## Test Signals
Signals are successful native library load, `CApi.init()` resolution, JNI compilation against this header, Java tests exercising `CApi`, `SQLTester`, and FTS5 methods, and failures such as `UnsatisfiedLinkError` when signatures do not match.
