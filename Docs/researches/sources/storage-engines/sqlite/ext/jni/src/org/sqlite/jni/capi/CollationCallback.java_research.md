# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/CollationCallback.java

## Purpose
Interface for custom SQLite collation implementations in Java.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and `XDestroyCallback`. Declares `int call(byte[] lhs, byte[] rhs)` with `memcmp()` semantics and `void xDestroy()`.

## Control Flow
Registered collations are invoked during SQL comparison/sort operations. SQLite invokes `xDestroy()` when the collation is replaced or destroyed.

## State And Persistence Behavior
No interface state. Implementations may hold comparator state retained by the database connection's collation registry.

## Dependencies And Integration Points
Registered through `CApi.sqlite3_create_collation`; `AbstractCollationCallback` supplies a no-op destroy method.

## Risks And Edge Cases
Invalid comparator semantics can corrupt query ordering or indexes using the collation. Exceptions should not escape JNI callback dispatch. Byte arrays represent text encoding chosen by SQLite/JNI and should be compared consistently.

## Test Signals
Sort and equality tests using custom collations, replacement/destroy cleanup tests, and exception-path tests.
