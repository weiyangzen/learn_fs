<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksIterator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksIterator.java

## Purpose

Managed RocksIterator wrapper that can also hold an acquired database reference for the iterator lifetime.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksIterator`. Notable methods: `close`, `managed`, `managed`. Key imports include `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.RocksIterator`.

## Control flow

Constructors store an optional dbRef. `close` closes the iterator through ManagedObject, then closes dbRef so database shutdown can proceed.

## State and persistence behavior

Owns iterator native handle and optionally a database reference token.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Forgetting to close the iterator can keep DB references alive. Passing null dbRef is allowed for older call sites but offers no shutdown-race protection.

## Test signals

Verify iterator use in try-with-resources, dbRef release on close, and wait-and-close behavior with open iterators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksIterator.java -->
