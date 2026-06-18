# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/sqlite3_value.java

## Purpose
`sqlite3_value` is the Java wrapper for C `sqlite3_value*` values passed through SQLite expressions, columns, and UDF arguments.

## Important APIs, Types, and Functions
The class extends `NativePointerHolder<sqlite3_value>` and has a private JNI-only constructor. It defines no methods beyond inherited pointer access.

## Control Flow
Instances are returned by column-value APIs, UDF arguments, preupdate APIs, and duplication APIs. Callers pass them into `CApi.sqlite3_value_*()` readers or result setters.

## State and Persistence Behavior
Most instances are transient and valid only for a callback or active row. Duplicated values must be freed with `sqlite3_value_free()`.

## Dependencies and Integration Points
It integrates with scalar/aggregate/window functions, `SqlFunction.Arguments`, column accessors, Java object value APIs, and FTS5 extension functions.

## Risks
Retaining non-duplicated values beyond their legal lifetime is invalid. Tests intentionally retain them to verify the JNI layer clears native pointers after callbacks.

## Test Signals
`Tester1` checks value type, bytes/text conversion, `sqlite3_value_frombind()`, NIO buffer exposure, Java object extraction, duplicated value freeing, and invalidation of saved UDF argument values.
