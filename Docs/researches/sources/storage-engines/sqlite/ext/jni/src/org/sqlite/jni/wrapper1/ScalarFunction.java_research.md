# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/wrapper1/ScalarFunction.java

## Purpose
`wrapper1.ScalarFunction` is the higher-level wrapper1 abstraction for scalar SQL functions.

## Important APIs, Types, and Functions
It implements `SqlFunction`, requires `xFunc(SqlFunction.Arguments args)`, and offers no-op `xDestroy()`. The API hides low-level `sqlite3_context` and `sqlite3_value[]` behind `SqlFunction.Arguments`.

## Control Flow
`SqlFunction.ScalarAdapter` receives low-level JNI callbacks, constructs an `Arguments` object, calls this `xFunc()`, and converts thrown exceptions into SQLite result errors.

## State and Persistence Behavior
The base class stores no state. Subclasses may hold Java state and can use argument/result helpers during callback execution.

## Dependencies and Integration Points
It depends on `SqlFunction` and is registered through wrapper1 database APIs that adapt it to `org.sqlite.jni.capi.ScalarFunction`.

## Risks
Implementations must not retain `Arguments` or objects derived from invocation-scoped native handles. The wrapper is higher-level but still executes inside SQLite callback constraints.

## Test Signals
No direct wrapper1 tests are included here. Equivalent low-level scalar behavior is tested in `Tester1.testUdf1()`, `testUdfThrows()`, and `testUdfJavaObject()`.
