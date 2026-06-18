# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/XDestroyCallback.java

## Purpose
`XDestroyCallback` is a shared lifecycle callback for Java objects whose client-provided state is destroyed by SQLite.

## Important APIs, Types, and Functions
It declares `void xDestroy()`. The documentation states implementations must not throw and must not call back into SQLite, because that can deadlock.

## Control Flow
SQLite or the JNI proxy calls `xDestroy()` when registered state is finalized, such as a collation, SQL function, or FTS5 aux/function object.

## State and Persistence Behavior
The interface itself stores no state, but implementations typically release or mark Java-side resources. It is part of the lifecycle contract for state retained by native proxies.

## Dependencies and Integration Points
It is referenced by callback/function abstractions that need an xDestroy equivalent, including collations and SQL functions.

## Risks
The documented major risk is registering the same instance multiple times. Duplicate native ownership can lead to double free, memory corruption, or crashes when native references are released.

## Test Signals
`Tester1.testCollation()` and UDF tests check that destroy callbacks are called on close/finalization and not prematurely.
