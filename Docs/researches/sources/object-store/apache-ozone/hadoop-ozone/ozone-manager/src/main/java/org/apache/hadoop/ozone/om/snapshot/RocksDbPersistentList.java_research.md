# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/RocksDbPersistentList.java

Purpose: `RocksDbPersistentList<E>` implements `PersistentList` using a RocksDB column family, assigning integer keys for list indexes and codec-encoded values.

Important APIs and types: the constructor takes `ManagedRocksDB`, `ColumnFamilyHandle`, `CodecRegistry`, and entry class. `add()`, `addAll()`, `get()`, and `iterator()` implement the interface. `currentIndex` is an in-memory append index.

Control flow: `add()` encodes the current index, increments `currentIndex`, encodes the entry, and puts it into RocksDB. `addAll()` iterates another persistent list and adds each entry. `get()` encodes the requested index and decodes the fetched value. `iterator()` creates a managed Rocks iterator, seeks to first, decodes each iterator value, and closes the iterator through `ClosableIterator.close()`.

State and persistence behavior: entries persist in RocksDB, but `currentIndex` starts at zero for each Java object. If an instance is recreated over a non-empty column family, new `add()` calls can overwrite index zero onward unless the caller controls lifecycle or the column family is fresh.

Dependencies and integration points: it depends on RocksDB managed wrappers and `CodecRegistry`. Snapshot diff manager tests use it as a persistent ordered collection.

Risks: exception handling wraps IO/RocksDB failures in `RuntimeException` with TODOs to fail gracefully. There is no size discovery, remove, transaction batching, or recovery of append index. Iterator `next()` names the value bytes `rawKey`, a harmless readability issue.

Test signals: `TestRocksDbPersistentList` should cover add/get/iteration behavior and resource closure.
