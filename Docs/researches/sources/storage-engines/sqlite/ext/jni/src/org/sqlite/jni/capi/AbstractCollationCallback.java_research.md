# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AbstractCollationCallback.java

## Purpose
Convenience abstract base for SQLite collation callbacks that supplies a no-op destroy hook.

## Important APIs, Types, And Functions
Extends `CollationCallback` and `XDestroyCallback`. Implementers must provide `call(byte[] lhs, byte[] rhs)` using `memcmp()`-style ordering. `xDestroy()` is optional and defaults to no-op.

## Control Flow
SQLite invokes `call()` through JNI during string comparison for a registered collation and invokes `xDestroy()` when the collation is destroyed.

## State And Persistence Behavior
No built-in state. Subclasses may carry Java state retained by native callback mappings for the lifetime of the registered collation.

## Dependencies And Integration Points
Depends on `CollationCallback`, `XDestroyCallback`, and `@NotNull`. Registered through `CApi.sqlite3_create_collation`.

## Risks And Edge Cases
Comparison must obey a total order and must not throw. Stateful subclasses need cleanup in `xDestroy()` if they hold external resources.

## Test Signals
Create a custom collation, run sorted queries, and verify destroy callbacks are invoked when replaced, connection closes, or function mappings are cleared.
