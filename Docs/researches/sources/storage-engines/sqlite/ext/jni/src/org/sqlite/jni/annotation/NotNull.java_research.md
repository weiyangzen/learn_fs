# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/NotNull.java

## Purpose
Documents parameters that must not be Java null and, for SQLite handle wrappers or native pointer longs, must not represent a closed/finalized or invalid C resource.

## Important APIs, Types, And Functions
`@NotNull` is documented, source-retained, and targets parameters. Its javadoc defines null broadly to include stale SQLite handles and invalid native pointer values.

## Control Flow
No direct runtime flow. Annotated methods may still throw Java null-related exceptions or return SQLite misuse/error codes depending on wrapper behavior and native API armor.

## State And Persistence Behavior
No state. The annotation documents ownership/lifetime preconditions around native resources whose real state lives in SQLite C objects and `NativePointerHolder.nativePointer`.

## Dependencies And Integration Points
Depends on `java.lang.annotation` and references `sqlite3`, `sqlite3_stmt`, and `sqlite3_context` wrapper classes. Heavily used throughout `CApi` and callback signatures.

## Risks And Edge Cases
It is informational only and not enforced programmatically. Passing null or stale handles can produce non-standard result codes, Java exceptions, suppressed callback errors, or invalid native behavior despite `SQLITE_ENABLE_API_ARMOR`.

## Test Signals
Compilation and javadoc links confirm syntax. Behavioral tests should cover null/stale handle paths on public wrappers where those are intended to return `SQLITE_MISUSE` rather than crash.
