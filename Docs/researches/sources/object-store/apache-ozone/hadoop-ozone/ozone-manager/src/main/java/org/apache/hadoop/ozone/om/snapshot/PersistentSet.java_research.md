# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentSet.java

Purpose: `PersistentSet<E>` defines a minimal storage-backed set abstraction.

Important APIs and types: it exposes `add(E)` and `iterator()` returning `ClosableIterator<E>`.

Control flow and state: the interface contains no implementation. Persistence, uniqueness, and ordering semantics are supplied by implementations. `RocksDbPersistentSet` stores set entries as RocksDB keys with empty values.

Dependencies and integration points: it depends only on Ozone `ClosableIterator` and is used where snapshot code needs persistent unique membership.

Risks: the contract lacks `contains`, `remove`, size, clear, and transaction APIs. Callers must infer membership through iteration or implementation-specific access, and must close iterators.

Test signals: `TestRocksDbPersistentSet` validates the RocksDB-backed implementation.
