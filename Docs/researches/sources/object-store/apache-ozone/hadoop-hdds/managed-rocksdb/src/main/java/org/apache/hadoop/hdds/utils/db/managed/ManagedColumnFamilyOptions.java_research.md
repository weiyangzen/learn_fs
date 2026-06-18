<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedColumnFamilyOptions.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedColumnFamilyOptions.java

## Purpose

Managed ColumnFamilyOptions with leak tracking and deep-close support for managed table-format configs.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedColumnFamilyOptions`. Notable methods: `setTableFormatConfig`, `closeAndSetTableFormatConfig`, `setReused`, `isReused`, `close`, `closeDeeply`. Key imports include `static org.apache.hadoop.hdds.utils.db.managed.ManagedRocksObjectUtils.track`, `org.apache.ratis.util.UncheckedAutoCloseable`, `org.rocksdb.BlockBasedTableConfig`, `org.rocksdb.ColumnFamilyOptions`, `org.rocksdb.TableFormatConfig`.

## Control flow

`setTableFormatConfig` rejects overwriting an unclosed ManagedBlockBasedTableConfig and unsupported non-block configs. `closeAndSetTableFormatConfig` closes the previous managed config. `closeDeeply` closes child table config then options.

## State and persistence behavior

Tracks a reused flag and native options handle.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

The reused flag is advisory; callers must honor it. Table configs loaded from ini may be plain BlockBasedTableConfig and are treated specially.

## Test signals

Cover overwrite rejection, closeAndSet behavior, closeDeeply, copied options, and reused flag call sites.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedColumnFamilyOptions.java -->
