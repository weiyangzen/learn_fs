# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/OutputPointer.java

## Purpose
Defines Java holder classes that model C output pointer parameters for SQLite JNI methods.

## Important APIs, Types, And Functions
Nested classes include opaque handle outputs `sqlite3`, `sqlite3_blob`, `sqlite3_stmt`, `sqlite3_value` with private `value`, `get()`, `clear()`, and `take()`, plus primitive/object outputs `Bool`, `Int32`, `Int64`, `String`, `ByteArray`, and `ByteBuffer` with public `value` and accessors.

## Control Flow
Callers instantiate an output holder, pass it to a `CApi` method, then read with `get()` or transfer with `take()`. JNI mutates private opaque values directly; Java code cannot set handle outputs.

## State And Persistence Behavior
All state is transient Java heap state. `take()` clears opaque outputs so ownership of returned wrappers is explicit. The classes are not thread-safe and should not be shared across threads.

## Dependencies And Integration Points
Used by open, prepare, blob open, preupdate old/new, db/status APIs, table metadata, FTS5 APIs, and other JNI methods needing C-style out parameters.

## Risks And Edge Cases
Sharing output holders across threads can corrupt assumptions around native state. Forgetting `take()` may leave aliases to a handle. Primitive outputs are publicly mutable, so callers can overwrite returned values accidentally.

## Test Signals
Open/prepare/blob/preupdate/status tests using output holders, `take()` clearing checks, null optional output pointer tests, and thread confinement review.
