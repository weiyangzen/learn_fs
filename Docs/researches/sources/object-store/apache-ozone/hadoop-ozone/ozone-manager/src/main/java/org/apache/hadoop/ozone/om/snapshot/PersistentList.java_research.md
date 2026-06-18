# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/PersistentList.java

Purpose: `PersistentList<E>` defines the minimal list abstraction used by snapshot diff and metadata components that want storage-backed list semantics.

Important APIs and types: `add(E)`, `addAll(PersistentList<E>)`, `get(int)`, and `iterator()` returning `ClosableIterator<E>`.

Control flow and state: the interface has no state. Implementations decide how indexes are assigned, how entries persist, and how iterators are closed. The primary implementation in this subset is `RocksDbPersistentList`.

Dependencies and integration points: it depends on Ozone's `ClosableIterator` and is implemented over RocksDB column families for snapshot data structures.

Risks: the contract does not expose size, remove, clear, or transactional semantics. Callers must close iterators and should not assume `addAll()` is atomic unless an implementation documents it.

Test signals: `TestRocksDbPersistentList` validates the RocksDB implementation.
