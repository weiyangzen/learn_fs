# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/ScalarFunction.java

## Purpose
`ScalarFunction` is the low-level JNI binding abstraction for SQLite scalar user-defined functions registered through `sqlite3_create_function()`.

## Important APIs, Types, and Functions
The abstract class implements `SQLFunction` and requires `xFunc(sqlite3_context cx, sqlite3_value[] args)`. It also provides an overridable no-op `xDestroy()` lifecycle callback. The signature mirrors SQLite's scalar callback while exposing JNI wrapper types for the function context and arguments.

## Control Flow
Client code subclasses `ScalarFunction`, registers the object with `CApi.sqlite3_create_function()`, and SQLite calls `xFunc()` during statement execution. Native proxy code translates thrown Java exceptions into SQLite result errors as documented by the class comments.

## State and Persistence Behavior
The base class stores no state. Subclasses may hold Java state, but `sqlite3_context` and `sqlite3_value` arguments are only valid during a single callback invocation and should not be retained.

## Dependencies and Integration Points
It integrates with `SQLFunction`, `sqlite3_context`, `sqlite3_value`, and the C API registration layer in `CApi`. Higher-level wrapper1 scalar functions adapt to this type through `SqlFunction.ScalarAdapter`.

## Risks
The primary risk is retaining callback-only native wrappers beyond their valid lifetime. Implementations also need to use `sqlite3_result_*()` APIs correctly to set a result or error.

## Test Signals
`Tester1.testUdf1()`, `testUdfThrows()`, `testUdfJavaObject()`, and ByteBuffer UDF tests exercise scalar execution, error translation, Java object values, `xDestroy()`, and invalidation of temporary native handles.
