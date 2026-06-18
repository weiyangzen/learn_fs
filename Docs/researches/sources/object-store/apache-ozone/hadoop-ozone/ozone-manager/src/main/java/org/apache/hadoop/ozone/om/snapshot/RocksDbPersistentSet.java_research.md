# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentSet.java

Purpose: `RocksDbPersistentSet<E>` implements `PersistentSet` using a RocksDB column family, storing entries as keys with empty byte-array values.

Important APIs and types: the constructor takes `ManagedRocksDB`, `ColumnFamilyHandle`, `CodecRegistry`, and entry class. `add(E)` writes an encoded entry key. `iterator()` returns a closeable RocksDB key iterator.

Control flow: `add()` encodes the entry as the raw key and an encoded empty byte array as the value, then puts it into RocksDB. Duplicate adds overwrite the same key, giving set semantics. The iterator seeks to the first key and decodes each key as an entry.

State and persistence behavior: set membership persists in RocksDB. Ordering is RocksDB raw key order. No remove or contains operation is exposed by the interface.

Dependencies and integration points: it depends on RocksDB managed wrappers, `CodecRegistry`, and `ClosableIterator`. Snapshot diff structures can use it for persistent uniqueness.

Risks: failures are converted to `RuntimeException`; TODO comments indicate graceful handling is not implemented. The empty value is encoded through the codec registry instead of using the raw empty array directly, so the actual stored value depends on byte-array codec behavior. Iterators must be closed.

Test signals: `TestRocksDbPersistentSet` covers add and iteration semantics.
