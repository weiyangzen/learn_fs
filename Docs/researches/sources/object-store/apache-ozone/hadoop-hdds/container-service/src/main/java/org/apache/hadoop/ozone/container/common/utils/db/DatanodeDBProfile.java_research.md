<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/DatanodeDBProfile.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/DatanodeDBProfile.java

## Purpose

`DatanodeDBProfile` selects and memoizes managed RocksDB options for datanode metadata stores based on storage profile. It ensures column family options can be reused across containers and configures block cache size from datanode metadata RocksDB settings. The complete 156-line file was read.

## Important APIs, Types, and Functions

The abstract API exposes `getDBOptions()` and `getColumnFamilyOptions(ConfigurationSource)`. `getProfile(DBProfile)` returns `SSD` or `Disk` profile instances. Nested `SSD` and `Disk` delegate to `StorageBasedProfile`, which holds an `AtomicReference<Supplier<ManagedColumnFamilyOptions>>` and a base `DBProfile`.

## Control Flow

`getProfile` maps `SSD` to SSD options, and `DISK`/`TEST` to disk options. `StorageBasedProfile.getColumnFamilyOptions` creates a memoized supplier for options, installs it atomically once, and returns the shared value. Option creation gets base column-family options, marks them reused, and replaces table format config with a block-based table config using a configured `ManagedLRUCache` when config is present.

## State and Persistence Behavior

State is in-memory memoized RocksDB options and block cache objects. Persistent DB data is not touched here, but the returned options affect RocksDB behavior for datanode stores.

## Dependencies and Integration Points

It depends on HDDS `DBProfile`, managed RocksDB option wrappers, `ManagedLRUCache`, `MemoizedSupplier`, and config keys `HDDS_DATANODE_METADATA_ROCKSDB_CACHE_SIZE`.

## Risks and Edge Cases

Because column-family options are memoized per storage profile, the first configuration used controls later calls for that profile in the JVM. That is efficient for production but can surprise tests with different configs. Unsupported DB profiles throw `IllegalArgumentException`.

## Test Signals

Tests should verify profile mapping, DBOptions delegation, one-time memoization, configured block cache size, reused flag behavior, null-config fallback, and unsupported profile exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/db/DatanodeDBProfile.java -->
