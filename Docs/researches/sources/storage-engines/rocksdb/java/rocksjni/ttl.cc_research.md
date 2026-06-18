# sources/storage-engines/rocksdb/java/rocksjni/ttl.cc

## Purpose
This file bridges Java `TtlDB` to C++ `DBWithTTL`, enabling databases and column families with time-to-live expiration semantics.

## Important APIs, Types, and Functions
Exports include `open`, `openCF`, `disposeInternalJni`, `closeDatabase`, and `createColumnFamilyWithTtl`. It uses `Options`, `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, and `DBWithTTL`.

## Control Flow
The simple open path converts the database path string, calls `DBWithTTL::Open`, releases the path, and returns the DB handle or throws. The column-family path converts Java column family names with `JniUtil::byteStrings`, maps Java option handles to descriptors, copies Java TTL integers into a vector, opens the TTL DB, and returns a `long[]` containing the DB handle followed by column family handles. `createColumnFamilyWithTtl` pins the Java column family name, calls `CreateColumnFamilyWithTtl`, releases the array, and returns the handle.

## State and Persistence Behavior
Open and create-column-family operations create or access persistent RocksDB state with TTL behavior. Expiration behavior is implemented by RocksDB and compaction, not directly by JNI. `disposeInternalJni` deletes the `DBWithTTL` object. `closeDatabase` is intentionally disabled and does not close, pending an upstream issue noted in a TODO.

## Dependencies and Integration Points
It depends on `rocksdb/utilities/db_ttl.h`, generated `TtlDB` JNI headers, conversion helpers, and portal utilities. Java `TtlDB` extends RocksDB, so the bridge reuses ordinary RocksDB handle conventions.

## Risks and Edge Cases
`closeDatabase` is a no-op, so lifecycle differs from other DB wrappers and relies on disposal for cleanup. The column-family open path assumes the number and ordering of names, options, and TTLs line up. Invalid TTL values are not validated here. Error branches must release strings and arrays correctly.

## Test Signals
Tests should cover simple open, column-family open with multiple TTLs, read-only mode, creating a TTL column family, cleanup behavior despite no-op close, and expiration semantics after compaction.
