# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_api.java

## Purpose
`fts5_api` wraps the C `fts5_api*` table for registering FTS5 auxiliary functions.

## Important APIs, Types, and Functions
It extends `NativePointerHolder<fts5_api>`, defines `iVersion = 2`, exposes synchronized native `getInstanceForDb(sqlite3 db)`, native `xCreateFunction(String name, Object userData, fts5_extension_function xFunction)`, and a convenience overload without user data.

## Control Flow
Client code asks for the per-database API instance, then registers Java `fts5_extension_function` objects. SQLite/FTS5 later invokes those functions during FTS5 queries.

## State and Persistence Behavior
The comments and tests indicate one singleton wrapper per database. Registered functions and user data are retained by the native/JNI layer until FTS5 or the DB releases them.

## Dependencies and Integration Points
It depends on `sqlite3`, `NativePointerHolder`, `fts5_extension_function`, and annotations. It is the registration gateway for `Fts5ExtensionApi` callbacks.

## Risks
Tokenizer creation/find APIs are still TODO/commented out. Registering functions requires correct destroy/lifetime handling for Java callback objects and user data.

## Test Signals
`TesterFts5.test1()` validates per-DB singleton behavior and user-data round trip; `create_test_functions()` validates mass registration and query execution of registered auxiliary functions.
