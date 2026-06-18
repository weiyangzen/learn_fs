# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/DbPath.java

Purpose: Java tuple of database path and target size used by `DBOptions.setDbPaths`/`dbPaths`.

Control flow is pure Java value-object behavior: constructor stores package-visible final fields, `equals` compares path and target size with null handling, and `hashCode` combines both. State is immutable in Java and later converted by `DBOptions` into native path and target-size arrays that guide DB file placement across multiple paths.

Risks: fields are package-private rather than accessor-based, path nulls are allowed by equality but may fail native option conversion, and target size unit/meaning depends on RocksDB. Tests should cover equality/hash behavior, DBOptions conversion order, null-path rejection or behavior, and multi-path DB placement integration.
