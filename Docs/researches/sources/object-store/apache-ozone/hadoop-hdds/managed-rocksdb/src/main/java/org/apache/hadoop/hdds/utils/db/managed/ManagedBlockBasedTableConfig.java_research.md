<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBlockBasedTableConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBlockBasedTableConfig.java

## Purpose

Managed BlockBasedTableConfig that owns child filter/cache resources and prevents overwriting an unclosed block cache.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedBlockBasedTableConfig`. Notable methods: `closeAndSetBlockCache`, `setBlockCache`, `isClosed`, `close`. Key imports include `java.util.concurrent.atomic.AtomicBoolean`, `org.rocksdb.BlockBasedTableConfig`, `org.rocksdb.Cache`.

## Control flow

`setBlockCache` rejects replacing an owning unclosed cache. `closeAndSetBlockCache` closes the previous cache first. `close` closes filter policy and block cache once.

## State and persistence behavior

Tracks blockCacheHolder and an AtomicBoolean closed flag.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

The class only tracks the cache assigned through this object. External owners can still close or reuse the cache unexpectedly.

## Test signals

Verify close closes filter/cache, overwriting without close throws, closeAndSetBlockCache succeeds, and double close is harmless.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedBlockBasedTableConfig.java -->
