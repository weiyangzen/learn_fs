# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3.java

## Purpose
`sqlite3` is the Java wrapper type for C-level `sqlite3*` database handles.

## Important APIs, Types, and Functions
The class extends `NativePointerHolder<sqlite3>` and implements `AutoCloseable`. Its private constructor is for JNI creation only. `toString()` includes the native pointer and main database filename via `CApi.sqlite3_db_filename()`. `close()` delegates to `CApi.sqlite3_close_v2(this)`.

## Control Flow
Instances are returned by open APIs. User code passes them back to `CApi` methods, or uses try-with-resources to call `close()`.

## State and Persistence Behavior
The wrapper does not own the pointer independently; the native API owns lifecycle and sets the pointer to zero after close. The Java object remains as a typed carrier even after invalidation.

## Dependencies and Integration Points
It integrates with `NativePointerHolder`, `CApi.sqlite3_open*`, `sqlite3_close_v2`, filename lookup, and wrapper1 `Sqlite.fromNative()` mappings.

## Risks
Calling methods after close yields null/zero pointer semantics and may be misuse depending on the API. Concurrent use follows package-level threading restrictions.

## Test Signals
Many `Tester1` tests assert nonzero pointer after open and zero pointer after close; `testOpenDb1()`, `testOpenDb2()`, and try-with-resources paths validate `close()`.
