# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/AutoExtensionCallback.java

## Purpose
Java representation of a SQLite auto-extension callback invoked for newly opened database connections.

## Important APIs, Types, And Functions
Extends `CallbackProxy` and declares `int call(sqlite3 db)`. The javadoc documents recursion and statefulness hazards.

## Control Flow
After registration through `CApi.sqlite3_auto_extension`, SQLite/JNI invokes the callback for database opens. Return codes influence open error handling and exceptions become database error strings.

## State And Persistence Behavior
The interface has no fields. Registered callback objects are retained globally by the JNI/native auto-extension registry until canceled or reset.

## Dependencies And Integration Points
Integrates with `CApi.sqlite3_auto_extension`, `sqlite3_cancel_auto_extension`, and `sqlite3_reset_auto_extension`. Depends on `sqlite3` wrapper and `CallbackProxy`.

## Risks And Edge Cases
Opening another database inside the callback can recurse indefinitely. Mutating the extension list while extensions are running has unpredictable ordering. Closing the provided database from the callback is undefined.

## Test Signals
Register, cancel, and reset auto extensions; open databases; verify callback order, error propagation, and no recursion for safe implementations.
