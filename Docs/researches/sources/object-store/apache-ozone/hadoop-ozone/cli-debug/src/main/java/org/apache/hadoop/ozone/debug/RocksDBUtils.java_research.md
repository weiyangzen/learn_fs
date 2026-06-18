# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/RocksDBUtils.java

Purpose: `RocksDBUtils` provides shared helper methods for debug commands that inspect RocksDB stores.

Important APIs and types: It uses `RocksDatabase.listColumnFamiliesEmptyOptions`, RocksDB `ColumnFamilyDescriptor` and `ColumnFamilyHandle`, `ManagedRocksDB`, `Codec<T>`, and `StringCodec`.

Control flow: One method lists column-family descriptors from a DB path, another finds a handle by UTF-8 name bytes, and `getValue` performs a typed lookup using a string key codec and caller-provided value codec.

State and persistence behavior: It does not mutate DBs. Reads occur through a supplied RocksDB handle, generally opened read-only by callers.

Dependencies and integration points: The helpers support `Checkpoint`, `DBScanner`, and other ldb-style commands that need consistent column family enumeration and typed lookup.

Risks: `getColumnFamilyHandle` returns null when not found, so callers must handle that. `getValue` assumes string keys and is not appropriate for long/protobuf-keyed tables.

Test signals: Expected signals are correct descriptor enumeration, matching handles by name, null on missing column family, and decoded values for existing string keys.
