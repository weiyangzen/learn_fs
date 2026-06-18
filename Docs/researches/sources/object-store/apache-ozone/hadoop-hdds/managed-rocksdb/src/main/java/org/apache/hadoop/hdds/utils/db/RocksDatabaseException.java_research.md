<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabaseException.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabaseException.java

## Purpose

Wraps RocksDBException as an IOException-facing database exception and prefixes messages with the RocksDB status code when the cause is a RocksDBException.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db`. Main type: `RocksDatabaseException`. Notable methods: `getStatus`, `getMessage`. Key imports include `java.io.IOException`, `org.rocksdb.RocksDBException`.

## Control flow

Constructors call a private formatter that extracts `getStatus().getCodeString()` or `NULL_STATUS`, then delegate to IOException.

## State and persistence behavior

No mutable state beyond inherited exception message/cause.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Only Exception causes are accepted by the formatted constructor, not arbitrary Throwable. Null status is handled, but callers must preserve the original cause for diagnostics.

## Test signals

Test with RocksDBException containing real and null statuses, ordinary Exception causes, empty messages, and default constructor serialization/logging behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/RocksDatabaseException.java -->
