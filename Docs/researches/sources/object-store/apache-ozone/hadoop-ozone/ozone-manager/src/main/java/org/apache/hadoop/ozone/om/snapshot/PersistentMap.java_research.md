# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentMap.java

Purpose: `PersistentMap<K,V>` defines a simple storage-backed map abstraction for snapshot-related metadata.

Important APIs and types: core operations are `get(K)`, `put(K,V)`, `remove(K)`, and bounded/unbounded iteration through `ClosableIterator<Map.Entry<K,V>>`. The default `iterator()` delegates to the optional-bound overload with empty bounds.

Control flow and state: the interface is stateless. Implementations define persistence, key ordering, and bound interpretation. `RocksDbPersistentMap` provides ordered RocksDB iteration with optional lower and upper raw key bounds.

Dependencies and integration points: it depends on Java `Map.Entry`, `Optional`, and Ozone `ClosableIterator`. Snapshot diff manager MXBean tests use the RocksDB implementation.

Risks: no atomic batch or compare-and-set operations are exposed. Iteration ordering is implementation-defined by the backing store's key encoding. Callers must close iterators.

Test signals: `TestRocksDbPersistentMap` covers puts, gets, removals, and bounded iteration.
