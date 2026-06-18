# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/fts5/fts5_extension_function.java

## Purpose
`fts5_extension_function` is the Java equivalent of C's FTS5 auxiliary function callback type.

## Important APIs, Types, and Functions
It declares `void call(Fts5ExtensionApi ext, Fts5Context fCx, sqlite3_context pCx, sqlite3_value argv[])` and `void xDestroy()`. Nested abstract class `Abstract` keeps `call()` abstract and supplies a no-op `xDestroy()`.

## Control Flow
After registration through `fts5_api.xCreateFunction()`, FTS5 invokes `call()` for matching SQL auxiliary function calls. Implementations use `ext` and `fCx` to inspect FTS5 state and `pCx`/`sqlite3_result_*()` to return SQL results.

## State and Persistence Behavior
Implementations may hold Java state or user data; `xDestroy()` is called when SQLite destroys the registered function. Callback arguments are invocation-scoped native wrappers.

## Dependencies and Integration Points
It integrates `Fts5ExtensionApi`, `Fts5Context`, `sqlite3_context`, `sqlite3_value`, and registration through `fts5_api`.

## Risks
Implementations must not retain invocation-scoped wrappers and should translate errors into SQLite results or exceptions handled by the JNI layer. `xDestroy()` should be lightweight and safe.

## Test Signals
`TesterFts5` defines many anonymous implementations, verifies result-producing behavior, and checks `xDestroy()` is called for an auxiliary function when the database closes.
