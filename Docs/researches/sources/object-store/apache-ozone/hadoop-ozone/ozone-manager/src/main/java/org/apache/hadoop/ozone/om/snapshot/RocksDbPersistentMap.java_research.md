# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentMap.java

Purpose: `RocksDbPersistentMap<K,V>` implements `PersistentMap` on top of a RocksDB column family with `CodecRegistry` serialization.

Important APIs and types: the constructor requires non-null DB, column family, codec registry, key type, and value type. `get()`, `put()`, `remove()`, and `iterator(Optional<K>, Optional<K>)` implement the map contract.

Control flow: `get()` encodes a key, fetches raw bytes, and decodes the value type. `put()` encodes key and value and writes to RocksDB. `remove()` deletes the encoded key. Bounded `iterator()` creates managed lower and upper `Slice` bounds when present, attaches them to `ManagedReadOptions`, creates a Rocks iterator, seeks to first, and returns a `ClosableIterator` that decodes immutable `Map.Entry` objects and closes iterator, read options, and slices.

State and persistence behavior: data persists in RocksDB. Iteration is ordered by RocksDB raw encoded key order and excludes the upper bound through RocksDB iterate-upper-bound semantics. The returned entries do not support `setValue()`.

Dependencies and integration points: it depends on Jakarta `@Nonnull`, RocksDB managed wrappers, `CodecRegistry`, and Ozone `ClosableIterator`. Snapshot diff manager MXBean tests instantiate it for job/report metadata.

Risks: `get()` behavior for missing keys depends on `CodecRegistry.asObject(null, valueType)`, so callers should confirm null handling. All RocksDB/codec failures become unchecked runtime exceptions. Iterators must be closed to release native resources. Bound correctness depends on codec byte ordering matching intended key ordering.

Test signals: `TestRocksDbPersistentMap` covers map operations and bounded iteration.
