# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/annotation/Nullable.java

## Purpose
Documents parameters and callback arguments that may legally be null in the SQLite JNI binding.

## Important APIs, Types, And Functions
`@Nullable` is documented, source-retained, and targets parameters. It has no members.

## Control Flow
No runtime flow. It documents code paths where Java wrappers translate null into SQLite null values, clear callbacks, or optional output parameters.

## State And Persistence Behavior
No state. It communicates acceptable nullability for APIs that may mutate SQLite state or callback registrations.

## Dependencies And Integration Points
Depends on `java.lang.annotation`. Used in `CApi` overloads for nullable strings, byte arrays, callbacks, output pointers, blobs, and Java objects.

## Risks And Edge Cases
Retention is source-only and not enforced. A nullable parameter can still carry semantic differences, for example binding SQL NULL, clearing a hook, or omitting an output value.

## Test Signals
Compilation and generated docs are primary. API tests should verify null behavior for callbacks, bind/result helpers, and optional output pointers.
