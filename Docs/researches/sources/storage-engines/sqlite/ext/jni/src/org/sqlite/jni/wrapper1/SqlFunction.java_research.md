# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/SqlFunction.java

## Purpose
`SqlFunction` is the wrapper1 marker interface and adapter hub for scalar, aggregate, and window UDFs. It raises the API above raw JNI callback types while still delegating to `CApi`.

## Important APIs, Types, and Functions
The interface exports UDF flags and encodings from `CApi`. Nested `Arguments` wraps `sqlite3_context` plus `sqlite3_value[]`, provides typed getters (`getInt`, `getText16`, `getObject`, metadata methods), result setters (`resultInt`, `resultText`, `resultError`, `resultArg`, `resultZeroBlob`, etc.), auxdata helpers, DB lookup, and iterable `Arg` proxies. `ScalarAdapter`, `AggregateAdapter`, and `WindowAdapter` adapt wrapper1 function classes to low-level `org.sqlite.jni.capi` function classes.

## Control Flow
Registration code creates an adapter around a wrapper1 implementation. SQLite invokes the low-level adapter, which constructs an `Arguments` object and calls wrapper methods. Exceptions are caught and reported with `sqlite3_result_error()`.

## State and Persistence Behavior
`Arguments` is per callback and holds invocation-scoped native wrappers. Adapters hold the user implementation and forward `xDestroy()`. Auxdata is stored in SQLite through `sqlite3_set_auxdata()` and fetched by argument index.

## Dependencies and Integration Points
It depends on `CApi`, `sqlite3_context`, `sqlite3_value`, wrapper1 `Sqlite`, `ScalarFunction`, `AggregateFunction`, and `WindowFunction`.

## Risks
Index validation is explicit for argument access, but retaining `Arguments.Arg` after the callback remains unsafe. `getDb()` can return null if the database has been closed during a UDF. Adapters intentionally swallow Java exceptions into SQLite result errors, so callers must inspect SQLite step results.

## Test Signals
No direct wrapper1 tests are in this subset. Low-level tests cover the underlying result/error/value/auxdata behavior; wrapper-specific tests should assert adapter exception translation, iterable arguments, auxdata bounds checks, and `getDb()` mapping.
