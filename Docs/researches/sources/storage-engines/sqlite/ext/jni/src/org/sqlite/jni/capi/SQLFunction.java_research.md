# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/SQLFunction.java

## Purpose
Marker base interface for Java SQL functions installed through `CApi.sqlite3_create_function`.

## Important APIs, Types, And Functions
Defines no methods. The javadoc describes expected callback shapes for scalar, aggregate, and window function implementations recognized by JNI.

## Control Flow
No direct flow in this interface. Native UDF dispatch checks for expected method names/signatures on objects passed as `SQLFunction` implementations.

## State And Persistence Behavior
No state. Implementing function objects may carry per-function state and are retained by SQLite/JNI until function destruction.

## Dependencies And Integration Points
Implemented by function classes such as scalar, aggregate, and window UDF helpers. Used by `CApi.sqlite3_create_function`.

## Risks And Edge Cases
Because it is a marker, compile-time enforcement of required callback methods is limited to helper classes/interfaces. Custom implementations must match JNI-dispatched method signatures exactly.

## Test Signals
Register scalar, aggregate, and window functions; verify callbacks dispatch, state cleanup, exception handling, and invalid custom implementation behavior.
