# sources/storage-engines/sqlite/ext/jni/src/org/sqlite/jni/capi/TableColumnMetadata.java

## Purpose
`TableColumnMetadata` is a Java result object populated by the convenience overload of `sqlite3_table_column_metadata()`.

## Important APIs, Types, and Functions
The class owns package-private output holders for not-null, primary-key, autoincrement, collation sequence, and data type values. Public getters expose `getDataType()`, `getCollation()`, `isNotNull()`, `isPrimaryKey()`, and `isAutoincrement()`.

## Control Flow
Client code creates no meaningful state directly beyond constructing the object. The JNI/C API wrapper fills its `OutputPointer` fields, then callers read immutable-by-convention metadata through getters.

## State and Persistence Behavior
The object is a snapshot holder. It has mutable fields internally, but no setters; values persist until overwritten by package-level code or discarded.

## Dependencies and Integration Points
It depends on `OutputPointer.Bool` and `OutputPointer.String`, and is returned by `CApi.sqlite3_table_column_metadata(sqlite3, String, String, String)`.

## Risks
Because fields are package-visible and mutable holders, misuse inside the package could mutate a previously returned snapshot. Callers must also handle null return from the C API wrapper when a database/table lookup fails.

## Test Signals
`Tester1.testColumnMetadata()` compares raw output-pointer calls with this wrapper, checks declared type/collation flags, verifies missing database/table return null, and tests table-existence lookup when column name is null.
