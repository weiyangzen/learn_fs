# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTestUtils.java

Purpose: Provides in-memory implementations of snapshot persistent collection interfaces for tests. Important APIs and types include `PersistentMap`, `PersistentSet`, `PersistentList`, `ClosableIterator`, `CodecRegistry`, Guava unsigned byte comparator, `TreeMap`, `TreeSet`, and `ArrayList`.

Control flow: A codec-backed comparator serializes keys to raw bytes and orders them lexicographically as unsigned bytes, matching RocksDB-style ordering more closely than Java object comparison. `StubbedPersistentMap` supports get/put/remove and bounded iteration with optional lower/upper keys. `StubbedPersistentSet` supports add and iteration. `ArrayPersistentList` extends `ArrayList`, implements persistent-list `addAll`, and returns closeable iterators.

State and persistence behavior: State is purely in memory, but ordering and iterator APIs emulate persistent snapshot data structures. No files or RocksDB instances are used.

Dependencies and integration points: Snapshot diff/local-data tests can use these classes where production code expects persistent interfaces. Risks include codec serialization failures and simplified close/no-resource behavior. Test signals are deterministic ordering, range filtering, add/remove semantics, and compatibility with `ClosableIterator`.
